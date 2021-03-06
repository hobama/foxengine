# -*- coding: utf-8 -*-

''' 头寸管理
    通过过滤matchedtrades来实现
'''

import operator
import logging

import numpy as np
from math import sqrt
#from scipy import stats


from wolfox.fengine.base.common import Trade
from wolfox.fengine.core.base import BaseObject,CLOSE,HIGH,OPEN
from wolfox.fengine.core.d1 import greater
from wolfox.fengine.core.utils import fcustom
from wolfox.fengine.core.d1ex import extend2next
from wolfox.fengine.core.future import decline_ranges,decline_periods,decline

logger = logging.getLogger('wolfox.fengine.core.postion_manager')

POS_BASE = 1000

NULL_TRADE = Trade(0,0,0,0) #用于占位的空TRADE
class Position(object): #只能用于管理单边头寸(即卖出都是pop，买入都是push或相反)，否则需要调用者判断某个买卖动作是push还是pop
    def __init__(self):
        self.holdings = {}  #现有仓位: code ==> [trade,....]    各trade都是同向操作
        self.history = []   #元素为一次封闭交易[trade_buy,trade_buy,...trade_sell]的列表

    def clear(self):
        self.holdings = {}  #比clear快
        self.history = []

    def push(self,trade,lostavg,risk,size_limit):    
        ''' trade为标准交易
            返回根据lostavg,risk计算的实际的交易额,但不能超过size_limit
            lostavg是平均损失比例(千分位表示)
            risk是能够承担的风险值,以0.001元表示
            size_limit为上限交易额,也以0.001元表示
            price<0时会溢出。这种情况也会出现，600497，20050906. 这个问题由trade去保障
        '''
        #print 'push:',trade
        if trade.tstock in self.holdings:   #已经在持股. 对于多个来源的交易集合可能出现这种情况
            logger.debug('repeated buy in : %s %s',trade.tstock,trade.tdate)
            trade.set_volume(0)
            return 0
        max_size = size_limit / trade.tprice * 990 / POS_BASE #预留的tax
        if trade.tprice * lostavg / POS_BASE == 0:
            logger.debug('divided by zero : %s,%s,price=%s,lost_avg=%s:',trade.tstock,trade.tdate,trade.tprice,lostavg)
            wanted_size = max_size
        else:
            wanted_size = risk / (trade.tprice * lostavg / POS_BASE)
            if wanted_size > max_size:
                wanted_size = max_size
        wanted_size = (wanted_size / 100) * 100     #交易量向100取整
        if trade.tvolume < 0:
            wanted_size = -wanted_size
        #print wanted_size
        if wanted_size == 0:
            logger.debug('wanted volume is too smal : %s %s',trade.tstock,trade.tdate)
            trade.set_volume(0)
            return 0
        trade.set_volume(wanted_size)
        self.holdings[trade.tstock] = [trade]
        return trade.calc()

    def pop(self,trade):
        ''' 确定卖出交易的额度,正常为全额. 子类可以定制这个方法,但需要maketrade函数的配合,以便部分卖出时有后续的卖出动作
            返回交易金额，正数
        '''
        holdeds = self.holdings.pop(trade.tstock,[NULL_TRADE])
        hv = sum([holded.tvolume for holded in holdeds] )
        trade.set_volume(-hv)   #方向相反
        if trade.tvolume:   #如果发生交易,则添加到历史
            self.history.append(holdeds + [trade])
        return trade.calc(),sum([holded.calc() for holded in holdeds])

    def cost(self): #持仓成本
        total = 0
        for vs in self.holdings.values():
            total -= sum([v.calc() for v in vs])   #计算所的是收入数(小于0)
        return total


def half_of_first_sizer(trades,max_times=4):    #max_times，最多买入次数
    if len(trades) < max_times:
        return abs(trades[0].tvolume / 2)
    return 0

def half_of_total_sizer(trades,max_times=4):    #max_times，最多买入次数
    if len(trades) < max_times:
        total = sum([t.tvolume for t in trades])
        return abs(total / 2)
    return 0

class AdvancedPosition(Position):
    def __init__(self,sizer = half_of_first_sizer):
        Position.__init__(self)
        self.sizer = sizer

    def push(self,trade,lostavg,risk,size_limit):    
        ''' trade为标准交易
            返回根据lostavg,risk计算的实际的交易额,但不能超过size_limit
            lostavg是平均损失比例(千分位表示)
            risk是能够承担的风险值,以0.001元表示
            size_limit为上限交易额,也以0.001元表示
        '''
        if trade.tstock not in self.holdings:
            if trade.type == 'native':   
                return Position.push(self,trade,lostavg,risk,size_limit)
            else:#前面的没开仓，不应该再买进
                trade.set_volume(0)
                return 0
        tolds = self.holdings[trade.tstock]
        #print tolds
        direct = 1 if tolds[0].tvolume >= 0 else -1  #1买入-1卖出
        if (direct == 1 and trade.tprice <= tolds[-1].tprice) or (direct == -1 and trade.tprice >= tolds[-1].tprice):  
            #买入后下降中不再买入或卖出后上升中不再卖出
            #print u'后续交易条件不符合,last price:%s,cur price:%s' % (tolds[-1].tprice,trade.tprice)
            return 0
        wanted_size = self.sizer(tolds)
        if wanted_size * trade.tprice > size_limit:
            wanted_size = size_limit / trade.tprice * 990 / POS_BASE #预留的tax
        wanted_size = (wanted_size / 100) * 100     #交易量向100取整
        if direct == -1:
            wanted_size = - wanted_size
        #print u'后续交易开始，volume=%s' % wanted_size            
        if wanted_size == 0:
            logger.debug('second wanted volume is too small : %s %s',trade.tstock,trade.tdate)
            trade.set_volume(0)
            return 0
        trade.set_volume(wanted_size)
        tolds.append(trade)
        return trade.calc()


#平均损失函数，返回的是千分比表示的平均损失
def ev_lost(trade): 
    return trade.parent.evaluation.lostavg

def atr_lost(trade,times=1000):
    return trade.atr * times / trade.tprice

atr_lost_2000 = fcustom(atr_lost,times=2000)
atr_lost_1200 = fcustom(atr_lost,times=1200)

def RPR(xt,y):  #净值评估函数,xt为日期维x,y为相应净值
    '''#根据海龟交易法则
       计算方法来自http://www.scipy.org/Cookbook/LinearRegression
    '''
    (ar,br)=np.polyfit(xt,y,1)  #一阶拟合
    xr = np.polyval([ar,br],xt)
    err=sqrt(sum((xr-y)**2)/len(xt)) #标准差
    #(a_s,b_s,r,tt,stderr)=stats.linregress(xt,y)    #len(xt)必须>2，否则会有问题. 即[begin,end)包含的实际日期数必须大于2
    #year_inc_rate = int(a_s * 365 * POS_BASE/b_s)
    year_inc_rate = int(ar * 365 * POS_BASE/br)
    #logger.debug('rar:year_inc_rate=%s,a=%s,b=%s,k=a/b=%s,stderr=%s,err=%s',year_inc_rate,a_s,b_s,a_s/b_s,stderr,err)
    logger.debug('rar:year_inc_rate=%s,a=%s,b=%s,k=a/b=%s,err=%s',year_inc_rate,ar,br,ar/br,err)    
    #logger.debug('rar:ar:%s,br:%s',ar,br)
    if year_inc_rate >=0:
        pass
        #logger.debug('year_inc_rate>0,net:%s',y.tolist())
    return year_inc_rate

def CSHARP(xt,y):   #变异夏普比率
    ''' 以回报而非超额回报为分子近似计算月比例
    '''
    indices = range(0,len(xt),30)
    #print indices
    m_xt = xt[indices]
    m_y = y[indices]
    #print m_xt,m_y
    (ar,br)=np.polyfit(m_xt,m_y,1)  #一阶拟合
    yr = np.polyval([ar,br],m_xt)
    err=sqrt(sum((yr-m_y)**2)/len(m_xt)) #标准差
    #print ar,br,err
    csharp = ar/br/err * POS_BASE
    return int(csharp) if np.isfinite(csharp) else 99999999

def AVG_DECLINE(xt,y,covered=22):
    mranges = decline_ranges(y,covered)
    mperiods = decline_periods(y,covered)
    #print 'ranges,periods:',mranges,mperiods
    avg_range = np.sum(mranges) / np.sum(greater(mranges))
    avg_period = np.sum(mperiods) / np.sum(greater(mperiods))
    return int(avg_range),int(avg_period)

def MAX_DECLINE(xt,y):
    return decline(y)


class PositionManager(object):  #只适合先买后卖，卖空和混合方式都要由子类定制run实现
    def __init__(self,init_size=100000000,max_proportion=200,risk=6,calc_lost=ev_lost,position=Position):
        self.init_size = init_size     #现金,#以0.001元为单位
        self.max_proportion = max_proportion    #满足risk条件下单笔占总金额的最大占比(千分比)
        self.risk = risk    #每笔交易承担的风险占总金额的比例(千分比)
        self.calc_lost = calc_lost
        #print position
        self.position = position()  #现有仓位: code ==> trade
        self.cash = init_size
        self.earning = 0        #当前盈利
        self.vhistory = [BaseObject(date=0,value=self.init_size)]      #净值历史

    def clear(self):
        self.cash = self.init_size
        self.earning = 0
        self.position.clear()
        self.vhistory = [BaseObject(date=0,value=self.init_size)]

    def assets(self):
        #return self.init_size + self.earning   #self.earning类型某些情况下可能是numpy.int32?
        return int(self.init_size + self.earning)   #self.earning类型某些情况下可能是numpy.int32? 如果在计算过程中引入了numpy.int32,则都会被转为这个.从而导致yaml.dump出错

    def cur_limit(self): #计算当前的最大单笔占比,不能大于当前现金数
        v = int(self.assets() * self.max_proportion / POS_BASE)
        return v if v<= self.cash else self.cash    
    
    def cur_risk(self):
        return int(self.assets() * self.risk / POS_BASE)

    def income_rate(self):
        return int(self.earning * POS_BASE / self.init_size)

    def organize_trades(self,named_trades):
        ''' 输入是元素如下的列表：
                trades:[[trade1,trade2,...],[trade3,trade4,...],....] 闭合交易列表
            转换合并按日期排序后返回
                [trade1,trade2,.....]
        '''
        nts = filter(lambda ts : ts,named_trades)   #滤去空元素
        if not nts: #啥也没剩下
            return []
        tradess = reduce(operator.add,nts) #转换为[[...],[...],[...]]
        trades = reduce(operator.add,tradess)   #为[......]
        trades.sort(cmp=lambda x,y:x.tdate-y.tdate)
        return [trade.copy() for trade in trades]

    def filter(self,named_trades):
        self.run(self.organize_trades(named_trades))
        return self.position.history

    def run(self,trades):
        for trade in trades:
            climit = self.cur_limit()
            crisk = self.cur_risk()
            if trade.tvolume > 0:   #买入
                #print u'买入,before cash:',self.cash,'tstock:',trade.tstock,'tdate:',trade.tdate
                self.cash += self.position.push(trade,self.calc_lost(trade),crisk,climit)
                #print u'买入,after cash:',self.cash                
            else:   #卖出
                #print u'卖出,before cash:',self.cash,'tstock:',trade.tstock,'tdate:',trade.tdate
                income,cost = self.position.pop(trade)
                if income:  #非空转
                    self.cash += income
                    self.earning += (income + cost)
                    self.vhistory.append(BaseObject(date=int(trade.tdate),value=self.assets()))
                #print u'卖出,after cash:',self.cash

    def calc_net_indicator(self,date_manager,func=RPR): 
        xt = np.arange(len(date_manager))    #x轴
        y = self.organize_net_array(date_manager)  #y轴
        return func(xt,y)

    def organize_net_array(self,date_manager):
        ''' 根据date_manager和vhistory获得净值数组(坐标与dates相一致)
        '''
        rev = np.zeros(len(date_manager),int)
        self.vhistory[0].date = date_manager.begin
        try:
            for b in self.vhistory: #第一个是初始值
                index = date_manager.get_index(b.date)
                rev[index] = b.value
        except: #错误的时候才有可能，利润无限高
            print u'溢出了:',b.value
        rev = extend2next(rev)
        return rev

    def net_history(self):
        return [ (bo.date,bo.value) for bo in self.vhistory]

AdvancedPositionManager = fcustom(PositionManager,position=AdvancedPosition)
AdvancedATRPositionManager = fcustom(PositionManager,position=AdvancedPosition,calc_lost=atr_lost_1200) #默认1.2倍atr止损
AdvancedATRPositionManager2000 = fcustom(PositionManager,position=AdvancedPosition,calc_lost=atr_lost_2000)

class StepPositionManager(PositionManager):  #只适合先买后卖，卖空和混合方式都要由子类定制run实现
    def __init__(self,dates,init_size=100000000,max_proportion=200,risk=6,calc_lost=ev_lost,position=Position):
        PositionManager.__init__(self,init_size,max_proportion,risk,calc_lost,position)
        self.dates = dates

    def organize_trades(self,named_trades):
        trades = PositionManager.organize_trades(self,named_trades)
        #for trade in trades:
        #    print trade
        if len(trades) == 0:
            return trades
        new_trades = []
        ti = 0
        tcur = trades[ti]
        dlen = len(trades[0].stock.transaction[CLOSE])
        holding = {}
        for i in xrange(dlen):
            for hold in holding.values():   #i=0是没有持仓，所以不需要判断i>1
                tlimit = (hold[0].transaction[CLOSE][i-1] + hold[0].transaction[HIGH][i-1])/2
                base = hold[-1]
                #print tlimit,hold[1]+hold[2]
                if(tlimit > hold[1] + hold[2] and tlimit <  base.tprice + hold[2]*5):#当不超过3ATR时,添加一个trade
                    #print base.tstock,self.dates[i],tlimit,hold[1],hold[2],base.tprice
                    tvolume = base.tvolume/2 or 1
                    trade = Trade(base.tstock,int(self.dates[i]),int(hold[0].transaction[OPEN][i]),tvolume,base.taxrate)
                    trade.stock = base.stock
                    trade.atr = int(base.stock.atr2[i])
                    trade.type = 'append'
                    new_trades.append(trade)
                    holding[hold[0]][1] = hold[1] + hold[2] #更改起始价格
            while tcur.idate == i:
                if tcur.tvolume>0:
                    holding[tcur.stock] = [tcur.stock,tcur.tprice,int(tcur.stock.atr2[i]),tcur]
                elif tcur.tvolume<0 and tcur.stock in holding:
                    #print 'del:',tcur.tdate
                    del holding[tcur.stock]
                ti += 1
                if ti >= len(trades):
                    break
                tcur = trades[ti]
            if ti>=len(trades):
                break
        trades[0:0]= new_trades #插入到前面,以便如果B/S同时出现,B排序在前面
        trades.sort(cmp=lambda x,y:x.tdate-y.tdate)
        #for trade in trades:print trade
        return trades

AdvancedStepPositionManager = fcustom(StepPositionManager,position=AdvancedPosition)
AdvancedATRStepPositionManager = fcustom(StepPositionManager,position=AdvancedPosition,calc_lost=atr_lost_1200) #默认1.2倍atr止损
AdvancedATRStepPositionManager2000 = fcustom(StepPositionManager,position=AdvancedPosition,calc_lost=atr_lost_2000)


import datetime
class DateManager(object):
    def __init__(self,begin=0,end=0):
        self.begin = begin
        self.end = end
        self.date_map = self.init_dates(begin,end)

    def __len__(self):
        return len(self.date_map)

    def init_dates(self,begin,end):
        if end <= begin:
            return {}
        date_map = {}
        from_date = datetime.date(begin/10000,begin%10000/100,begin%100)
        to_date = datetime.date(end/10000,end%10000/100,end%100)
        step = datetime.timedelta(1)
        cur_date = from_date
        i = 0
        while cur_date < to_date:
            idate = cur_date.year * 10000 + cur_date.month * 100 + cur_date.day
            date_map[idate] = i
            cur_date += step
            i += 1
        return date_map
    
    def get_index(self,date):
        if date in self.date_map:
            return self.date_map[date]
        else:
            logger.warn('%s not in [%s,%s)',date,self.begin,self.end)
            print '%s not in [%s,%s)' % (date,self.begin,self.end)
            raise KeyError('%s not in [%s,%s)' % (date,self.begin,self.end))

    def get_dates(self):
        return sorted(self.date_map.keys())


class XDateManager(object):
    def __init__(self,xdates):
        self.xdates = xdates
        self.date_map = dict((y,x) for x,y in enumerate(xdates))    #date ==> index
        if len(xdates) > 0:
            self.begin,self.end = xdates[0],xdates[-1]
        else:
            self.begin = self.end = 0

    def __len__(self):
        return len(self.xdates)

    def get_index(self,date):
        if date in self.date_map:
            return self.date_map[date]
        else:
            logger.warn('%s not in curdates' % date)
            print '%s not in curdates' % date
            raise KeyError('%s not in curdates' % date)

    def get_xdates(self):
        return self.xdates

