# -*- coding: utf8 -*-

'''
    核心交易模块扩展
        针对突破交易和即时止损

'''
from datetime import date

from wolfox.fengine.ifuture.ibase import *
import wolfox.fengine.ifuture.iftrade as iftrade
import wolfox.fengine.ifuture.ifuncs as ifuncs

#同一分钟先开后平, 由make_trades确保已有开仓时不重复. 但已有仓位时同时出现开平信号，则以平仓计
DTSORT2 = lambda x,y: int(((x.date%1000000 * 10000)+x.time) - ((y.date%1000000 * 10000)+y.time)) or x.xtype-y.xtype 

day2weekday = lambda x:date(x/10000,x%10000/100,x%100).weekday() + 1
d2wd = day2weekday

def last_stop_long(sif,sopened,ttrace=1500,tend=1511,drawback=60):
    '''
        每日收盘前的平仓,平多仓
        从ttrace开始跟踪
        如果价格回撤超过drawback就平仓
    '''
    sl = np.zeros_like(sif.time)
    poss = filter(lambda x: gand(x[0]>=ttrace,x[0]<=tend),zip(sif.time,range(len(sif.time))))
    xhigh = 0
    for v,iv in poss:
        if v == ttrace:
            xhigh = sif.open[iv]
            xstop = xhigh - drawback
        if sif.low[iv] < xstop: #先比较是否破位再做高点比较。会有误差，但不大
            sl[iv] = xstop
        if sif.high[iv] > xhigh:
            xhigh = sif.high[iv]
            xstop = xhigh - drawback
        if v == tend:
            xhigh = 0
            sl[iv] = 1
    sl[-3:] = 1
    return  sl * XSELL

def last_stop_short(sif,sopened,ttrace=1500,tend=1511,drawback=60):
    '''
        每日收盘前的平仓,平多仓
        从ttrace开始跟踪
        如果价格回撤超过drawback就平仓
    '''
    sl = np.zeros_like(sif.time)
    poss = filter(lambda x: gand(x[0]>=ttrace,x[0]<=tend),zip(sif.time,range(len(sif.time))))
    xlow = 999999
    for v,iv in poss:
        if v == ttrace:
            xlow = sif.open[iv]
            xstop = xlow + drawback
        if sif.high[iv] > xstop: #先比较是否破位再做高点比较。会有误差，但不大
            sl[iv] = xstop
        if sif.low[iv] < xlow:
            xlow = sif.low[iv]
            xstop = xlow + drawback
        if v == tend:
            xlow = 999999
            sl[iv] = 1
    sl[-3:] = 1
    return  sl * XBUY

def last_stop_long2(sif,sopened,ttrace=240,tend=270,vbegin=0.01):
    '''
        每日收盘前的拉近止损,平多仓
        从ttrace开始跟踪
    '''
    ldopen = dnext(sif.opend,sif.close,sif.i_oofd)
    #ldopen = np.select([sopened!=0],[-sopened],0)
    #ldopen = extend2next(ldopen)
    vmax_stop = ldopen * vbegin
    vstep = vmax_stop / (tend - ttrace)
    cstop = vmax_stop - (sif.iorder - ttrace+1) * vstep
    sl = np.zeros_like(sif.iorder)
    h30 = tmax(sif.high,30)

    poss = filter(lambda x: gand(x[0]>=ttrace,x[0]<=tend),zip(sif.iorder,range(len(sif.iorder))))
    xhigh = 0
    pre_high = 0
    cur_stop = 0
    for v,iv in poss:
        if v == ttrace:
            #xhigh = sif.open[iv]
            xhigh = h30[iv]
        elif pre_high > xhigh:
            xhigh = pre_high
        pre_high = sif.high[iv]
        cur_stop = xhigh - cstop[iv]
        if sif.low[iv] < cur_stop: 
            #sl[iv] = cur_stop
            sl[iv] = cur_stop if sif.open[iv] > cur_stop else sif.open[iv]
        if v == tend-1:
            sl[iv] = 1
    sl[-3:] = 1
    return  sl * XSELL

def last_stop_short2(sif,sopened,ttrace=240,tend=270,vbegin=0.01):
    '''
        每日收盘前的拉近止损,平空仓
        从ttrace开始跟踪
    '''
    ldopen = dnext(sif.opend,sif.close,sif.i_oofd)
    vmax_stop = ldopen * vbegin
    vstep = vmax_stop / (tend - ttrace)
    cstop = vmax_stop - (sif.iorder - ttrace+1) * vstep
    sl = np.zeros_like(sif.iorder)
    l30 = tmin(sif.low,30)

    poss = filter(lambda x: gand(x[0]>=ttrace,x[0]<=tend),zip(sif.iorder,range(len(sif.iorder))))
    xlow = 99999999
    pre_low = 99999999
    
    cs = np.zeros_like(sif.iorder)#临时调试用
    
    for v,iv in poss:
        if v == ttrace:
            #xlow = sif.open[iv]
            xlow = l30[iv]
        elif pre_low < xlow:
            xlow = pre_low
        pre_low = sif.low[iv]
        cur_stop = xlow + cstop[iv]
        cs[iv] = cur_stop
        if sif.high[iv] > cur_stop: 
            sl[iv] = cur_stop if sif.open[iv] < cur_stop else sif.open[iv]
        if v == tend-1:
            sl[iv] = 1
    sl[-3:] = 1
    #print zip(sif.iorder[-30:],cstop[-30:],cs[-30:])
    return  sl * XBUY


weights = [1.0 for i in range(270)]
def last_stop_short3(sif,sopened,ttrace=240,tend=270,vbegin=0.01):
    '''
        每日收盘前的拉近止损,平空仓
        从ttrace开始跟踪
    '''
    ldopen = dnext(sif.opend,sif.close,sif.i_oofd)
    vmax_stop = ldopen * vbegin
    #vstep = vmax_stop / (tend - ttrace)
    myweights = weights[:tend-ttrace]
    myweights.reverse()
    swght = sum(myweights)
    #cstop = vmax_stop - (sif.iorder - ttrace+1) * vstep
    #cstop = vmax_stop - (sif.iorder - ttrace+1) * vstep
    sl = np.zeros_like(sif.iorder)
    l30 = tmin(sif.low,30)

    poss = filter(lambda x: gand(x[0]>=ttrace,x[0]<=tend),zip(sif.iorder,range(len(sif.iorder))))
    xlow = 99999999
    pre_low = 99999999
    
    cs = np.zeros_like(sif.iorder)#临时调试用
    
    for v,iv in poss:
        if v == ttrace:
            #xlow = sif.open[iv]
            xlow = l30[iv]
        elif pre_low < xlow:
            xlow = pre_low
        pre_low = sif.low[iv]
        #cur_stop = xlow + cstop[iv]
        cur_stop = xlow + (swght-sum(myweights[:v-ttrace+1]))/swght * vmax_stop[iv]
        cs[iv] = cur_stop
        if sif.high[iv] > cur_stop: 
            sl[iv] = cur_stop if sif.open[iv] < cur_stop else sif.open[iv]
        if v == tend-1:
            sl[iv] = 1
    sl[-3:] = 1
    #print zip(sif.iorder[-30:],cs[-30:])
    return  sl * XBUY


def stop_long_3(sif,sopened):
    sl = np.zeros_like(sif.time)
    sl[-3:] = 1
    return  sl * XSELL

def stop_short_3(sif,sopened):
    sl = np.zeros_like(sif.time)
    sl[-3:] = 1
    return  sl * XBUY

def stop_long_time(sif,sopened,mytime):
    sl = np.select([sif.time==mytime],[1],0)
    return  sl * XSELL

def stop_short_time(sif,sopened,mytime):
    sl = np.select([sif.time==mytime],[1],0)
    return  sl * XBUY


def repeat_trades(actions,calc_profit=iftrade.normal_profit):  #简单的trades,每个trade只有一次开仓和平仓
    ''' 不支持同时双向开仓
        但支持同向多次开仓
    '''
    state = EMPTY   #LONG,SHORT
    trades = []
    cur_trades = []
    for action in actions:
        #print 'action:',action.date,action.time,action.position,action.price
        if action.xtype == XOPEN and (state == action.position or state == EMPTY):
            #print 'open:',action.date,action.time,action.position,action.price
            action.vol = 1
            cur_trades.append(BaseObject(actions = [action]))
            state == action.position
        elif action.xtype == XCLOSE and len(cur_trades)>0 and action.position != state:    #平仓且方向相反
            #print 'close:',action.date,action.time,action.position,action.price
            action.vol = 1
            for trade in cur_trades:
                trade.actions.append(action)
                trade.profit = calc_profit(trade.actions)
                trades.append(trade)
            state = EMPTY
            cur_trades = []
        else:   #持仓时碰到同向平仓或逆向开仓/未持仓时碰到平仓指令
            pass
    return trades


#设定保证
def atr_stop_u2(
        sif
        ,sopened
        ,sbclose
        ,ssclose
        ,flost_base = 25
        #,fmax_drawdown = iftrade.F100_25 #fdmax:买入点数 --> 最大回落
        #,fmin_drawdown = iftrade.F60_15#fdmin:买入点数 --> 最小回落
        #,fkeeper = iftrade.FKEEP_30 #买入点数-->固定移动止损，移动到价格为止
        ,keeper_base = 25
        ,win_times=300        
        ,ftarget = iftrade.FTARGET #盈利目标,默认是无穷大
        ,tlimit = 300    #约定时间线. 目前没用
        ,wtlimit = -1000   #约定时间线的价格有利变动目标，如果不符合则平仓
        ,natr=1
        ,natr2=30
        ,nkeeper=30
        ,wave_stop = 300,  #约定的反向折返幅度最大比例(千分之一)单位. 基准幅度是dhigh-dlow
        ):
    '''
        根据价格突破即时止损,而不是下一个开盘价，返回值为止损价，未考虑滑点
            开仓时刻如果收盘价反向偏离开仓价超过初始止损，则也止损
        sif为实体
        sopened为价格序列，其中负数表示开多仓，正数表示开空仓
        sbclose是价格无关序列所发出的买入平仓信号集合(平空仓)
        ssclose是价格无关序列所发出的卖出平仓信号集合(平多仓)
        flost_base为初始止损函数
        win_times: 与ATR的乘积，来计算跟踪止损（盈）,如果在[fmin_drawdown(buy_point):fmax_drowdown(buy_point)]之外
            则取端点值
        fmax_drawdown: 确定从最高点起的最大回落点数的函数
        fmin_drawdown: 确定从最高点起的最小回落点数的函数
        只能持有一张合约。即当前合约在未平前会屏蔽掉所有其它开仓
    '''
    #print sbclose[-10:],ssclose[-10:]
    satr = rollx(iftrade.afm[natr](sif))
    satr2 = rollx(iftrade.afm[natr2](sif))
    skeeper = rollx(iftrade.afm[nkeeper](sif))
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        #willlost = flost_base(aprice)
        willlost = satr2[i]*flost_base/XBASE/XBASE
        #willlost = satr[i]*25/XBASE/XBASE
        #willlost = willlost if willlost < 250 else 250
        #max_drawdown = fmax_drawdown(aprice)
        #min_drawdown = fmin_drawdown(aprice)
        keeper = skeeper[i] * keeper_base / XBASE /XBASE
        wave_stop_v = (sif.dhigh[i] - sif.dlow[i]) * wave_stop / 1000
        if willlost>wave_stop_v:
            willlost = wave_stop_v
        #print price,willlost,max_drawdown,min_drawdown
        will_losts.append(willlost)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = cur_high - satr[i] * win_times / XBASE / XBASE
            cur_stop = lost_stop if lost_stop > win_stop else win_stop
            wtarget = buy_price + ftarget(buy_price)
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格,两次乘XSELL，把符号整回来
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL   #两次乘XSELL，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        rev[j] = cur_stop * XSELL 
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:
                        ilong_closed = j
                        rev[j] = myssclose[j] * XSELL 
                        #print 'sell in sclose:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif j==i+tlimit and tv<wtlimit:    #时间到
                        #print u'时间到'
                        ilong_closed = j
                        rev[j] = trans[ICLOSE][j] * XSELL   #两次乘XSELL，把符号整回来
                        print 'sell in time limit:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif trans[IHIGH][j] > wtarget: #超过目标价
                        ilong_closed = j                        
                        rev[j] = wtarget * XSELL    #两次乘XSELL，把符号整回来
                        #print 'sell at target:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    #if j == i+tlimit and cur_stop < buy_price+100 and trans[ICLOSE][j] > buy_price+100:
                    #    cur_stop = buy_price+80
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        drawdown = satr[j] * win_times / XBASE / XBASE
                        if drawdown > trans[ICLOSE][j] *9/8/100:
                            drawdown = trans[ICLOSE][j] *9/8/100
                        #if drawdown > max_drawdown:
                        #    drawdown = max_drawdown
                        #if drawdown < min_drawdown:
                        #    drawdown = min_drawdown
                        win_stop = cur_high - drawdown
                        #win_stop = cur_high - satr[j] * win_times / XBASE
                        #print nhigh,cur_stop,win_stop,satr[j]
                        if cur_stop < win_stop:
                            cur_stop = win_stop
                        keep_stop = cur_high - keeper
                        if cur_stop < buy_price and keep_stop > buy_price:  #一次跳变
                            cur_stop = buy_price 
                        #if cur_stop < keep_stop:
                        #    cur_stop = keep_stop if keep_stop < buy_price else buy_price
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = cur_low + satr[i] * win_times / XBASE / XBASE
            cur_stop = lost_stop if lost_stop < win_stop else win_stop
            wtarget = sell_price - ftarget(sell_price)
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY
            elif mysbclose[i] >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = mysbclose[i] *XBUY
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        rev[j] = cur_stop * XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif mysbclose[j] >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = mysbclose[j] * XBUY
                        break
                    elif (j==i+tlimit and tv < wtlimit):#时间到
                        ishort_closed = j
                        rev[j] = trans[ICLOSE][j] * XBUY   
                        break
                    elif trans[ILOW][j] < wtarget:#
                        ishort_closed = j
                        rev[j] = wtarget * XBUY
                        #print 'buy at target:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    if j == i+tlimit and cur_stop > sell_price-100 and trans[ICLOSE][j] < sell_price-100:
                        cur_stop = sell_price-80
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        drawdown = satr[j] * win_times / XBASE / XBASE
                        if drawdown > trans[ICLOSE][j] *9/8/100:
                            drawdown = trans[ICLOSE][j] *9/8/100
                        #if drawdown > max_drawdown:
                        #    drawdown = max_drawdown
                        #if drawdown < m0n_drawdown:
                        #    drawdown = min_drawdown
                        win_stop = cur_low + drawdown
                        #print nlow,cur_stop,win_stop,satr[j],win_times,drawdown
                        #win_stop = cur_low + satr[j] * win_times / XBASE / XBASE
                        if cur_stop > win_stop:
                            cur_stop = win_stop
                        keep_stop = cur_low + keeper
                        if cur_stop > sell_price and keep_stop < sell_price:
                            cur_stop = sell_price 
                        #if cur_stop > keep_stop:
                        #    cur_stop = keep_stop if keep_stop > sell_price else sell_price
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def atr_stop_u(
        sif
        ,sopened
        ,sbclose
        ,ssclose
        ,flost_base = iftrade.FBASE_30    #flost:买入点数 --> 止损点数
        ,fmax_drawdown = iftrade.F100_25 #fdmax:买入点数 --> 最大回落
        ,fmin_drawdown = iftrade.F60_15#fdmin:买入点数 --> 最小回落
        ,fkeeper = iftrade.FKEEP_30 #买入点数-->固定移动止损，移动到价格为止
        ,win_times=300        
        ,ftarget = iftrade.FTARGET #盈利目标,默认是无穷大
        ,tlimit = 300    #约定时间线. 目前没用
        ,wtlimit = -1000   #约定时间线的价格有利变动目标，如果不符合则平仓
        ,natr=1
        ,wave_stop = 300,  #约定的反向折返幅度最大比例(千分之一)单位. 基准幅度是dhigh-dlow
        ):
    '''
        根据价格突破即时止损,而不是下一个开盘价，返回值为止损价，未考虑滑点
            开仓时刻如果收盘价反向偏离开仓价超过初始止损，则也止损
        sif为实体
        sopened为价格序列，其中负数表示开多仓，正数表示开空仓
        sbclose是价格无关序列所发出的买入平仓信号集合(平空仓)
        ssclose是价格无关序列所发出的卖出平仓信号集合(平多仓)
        flost_base为初始止损函数
        win_times: 与ATR的乘积，来计算跟踪止损（盈）,如果在[fmin_drawdown(buy_point):fmax_drowdown(buy_point)]之外
            则取端点值
        fmax_drawdown: 确定从最高点起的最大回落点数的函数
        fmin_drawdown: 确定从最高点起的最小回落点数的函数
        只能持有一张合约。即当前合约在未平前会屏蔽掉所有其它开仓
    '''
    #print sbclose[-10:],ssclose[-10:]
    satr = iftrade.afm[natr](sif)
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        willlost = flost_base(aprice)
        max_drawdown = fmax_drawdown(aprice)
        min_drawdown = fmin_drawdown(aprice)
        keeper = fkeeper(aprice)
        #print price,willlost,max_drawdown,min_drawdown
        wave_stop_v = (sif.dhigh[i] - sif.dlow[i]) * wave_stop / 1000
        if willlost>wave_stop_v:
            willlost = wave_stop_v
        will_losts.append(willlost)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = cur_high - satr[i] * win_times / XBASE / XBASE
            cur_stop = lost_stop if lost_stop > win_stop else win_stop
            wtarget = buy_price + ftarget(buy_price)
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        rev[j] = cur_stop * XSELL 
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:
                        ilong_closed = j
                        rev[j] = myssclose[j] * XSELL 
                        #print 'sell in sclose:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif j==i+tlimit and tv<wtlimit:    #时间到
                        ilong_closed = j
                        rev[j] = trans[ICLOSE][j] * XSELL 
                        #print 'sell in time limit:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif trans[IHIGH][j] > wtarget: #超过目标价
                        ilong_closed = j                        
                        rev[j] = wtarget * XSELL
                        #print 'sell at target:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    if j == i+tlimit and cur_stop < buy_price+100 and trans[ICLOSE][j] > buy_price+100:
                        cur_stop = buy_price+80
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        drawdown = satr[j] * win_times / XBASE / XBASE
                        if drawdown > max_drawdown:
                            drawdown = max_drawdown
                        if drawdown < min_drawdown:
                            drawdown = min_drawdown
                        win_stop = cur_high - drawdown
                        #win_stop = cur_high - satr[j] * win_times / XBASE
                        #print nhigh,cur_stop,win_stop,satr[j]
                        if cur_stop < win_stop:
                            cur_stop = win_stop
                        keep_stop = cur_high - keeper
                        if cur_stop < buy_price and keep_stop > buy_price:  #一次跳变
                            cur_stop = buy_price 
                        #if cur_stop < keep_stop:
                        #    cur_stop = keep_stop if keep_stop < buy_price else buy_price
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = cur_low + satr[i] * win_times / XBASE / XBASE
            cur_stop = lost_stop if lost_stop < win_stop else win_stop
            wtarget = sell_price - ftarget(sell_price)
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY
            elif mysbclose[i] >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = mysbclose[i] *XBUY
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        rev[j] = cur_stop * XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif mysbclose[j] >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = mysbclose[j] * XBUY
                        break
                    elif (j==i+tlimit and tv < wtlimit):#时间到
                        ishort_closed = j
                        rev[j] = trans[ICLOSE][j] * XBUY   
                        break
                    elif trans[ILOW][j] < wtarget:#
                        ishort_closed = j
                        rev[j] = wtarget * XBUY
                        #print 'buy at target:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    if j == i+tlimit and cur_stop > sell_price-100 and trans[ICLOSE][j] < sell_price-100:
                        cur_stop = sell_price-80
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        drawdown = satr[j] * win_times / XBASE / XBASE
                        if drawdown > max_drawdown:
                            drawdown = max_drawdown
                        if drawdown < min_drawdown:
                            drawdown = min_drawdown
                        win_stop = cur_low + drawdown
                        #print nlow,cur_stop,win_stop,satr[j],win_times,drawdown
                        #win_stop = cur_low + satr[j] * win_times / XBASE / XBASE
                        if cur_stop > win_stop:
                            cur_stop = win_stop
                        keep_stop = cur_low + keeper
                        if cur_stop > sell_price and keep_stop < sell_price:
                            cur_stop = sell_price 
                        #if cur_stop > keep_stop:
                        #    cur_stop = keep_stop if keep_stop > sell_price else sell_price
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def atr_stop_v(
        sif,
        sopened,
        sbclose,
        ssclose,
        flost_base = iftrade.F70,    #flost:买入点数 --> 止损点数
        fmax_drawdown = iftrade.F250, #最大回落
        tstep = lambda sif,i:40,     #行情顺向滑动单位
        vstep = 20,                  #止损顺向移动单位   
        ):
    '''
    '''
    #print sbclose[-10:],ssclose[-10:]
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        willlost = flost_base(aprice)
        #willlost = sif.atr15x[i]/XBASE    #效果不佳
        max_drawdown = fmax_drawdown(aprice)
        will_losts.append(willlost)
        mytstep = tstep(sif,i)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
            #cur_stop = lost_stop if lost_stop > win_stop else win_stop
            cur_stop = win_stop #win_stop必然大于lost_stop
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        #rev[j] = cur_stop * XSELL 
                        rev[j] = (cur_stop if cur_stop < trans[IOPEN][j] else trans[IOPEN][j])* XSELL 
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:
                        ilong_closed = j
                        rev[j] = myssclose[j] * XSELL 
                        #print 'sell in sclose:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
                        mstop = cur_high - max_drawdown
                        cur_stop = win_stop if win_stop > mstop else mstop
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
            cur_stop = win_stop
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY
            elif mysbclose[i] >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = mysbclose[i] *XBUY
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        #rev[j] = cur_stop * XBUY
                        rev[j] = (cur_stop if cur_stop > trans[IOPEN][j] else trans[IOPEN][j])* XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif mysbclose[j] >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = mysbclose[j] * XBUY
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
                        mstop = cur_low + max_drawdown
                        cur_stop = win_stop if win_stop < mstop else mstop
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def atr_stop_x(
        sif,
        sopened,
        sbclose,
        ssclose,
        flost_base = iftrade.F70,    #flost:买入点数 --> 止损点数
        fmax_drawdown = iftrade.F250, #最大回落比例
        pmax_drawdown = 0.012, #最大回落比例
        tstep = lambda sif,i:40,     #行情顺向滑动单位
        vstep = 20,                  #止损顺向移动单位   
        ):
    '''
    '''
    #print sbclose[-10:],ssclose[-10:]
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    ldopen = dnext(sif.opend,sif.close,sif.i_oofd)        
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print mysbclose[np.nonzero(mysbclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        #willlost = flost_base(aprice)
        willlost = flost_base(ldopen[i])    #开盘价的定数
        #willlost = sif.atr15x[i]/XBASE    #效果不佳
        spmax_drawdown = pmax_drawdown * aprice
        sfmax_drawdown = fmax_drawdown(aprice)
        max_drawdown = spmax_drawdown if spmax_drawdown < sfmax_drawdown else sfmax_drawdown
        will_losts.append(willlost)
        mytstep = tstep(sif,i)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
            #cur_stop = lost_stop if lost_stop > win_stop else win_stop
            cur_stop = win_stop #win_stop必然大于lost_stop
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格   #两次乘XSELL，把符号整回来
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL   #两次乘XSELL，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        #rev[j] = cur_stop * XSELL 
                        rev[j] = (cur_stop if cur_stop < trans[IOPEN][j] else trans[IOPEN][j])* XSELL 

                        #if abs(myssclose[j]) >10 and abs(myssclose[j]) > rev[j]:    #不仅仅是信号
                        #    rev[j] = abs(myssclose[j]) * XSELL 
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:    #这个优先级比直接止损低，因为可能为收盘信号
                        ilong_closed = j
                        rev[j] = myssclose[j] * XSELL   #两次乘XSELL，把符号整回来
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
                        mstop = cur_high - max_drawdown
                        #mstop2 = buy_price if nhigh - buy_price > nhigh/250 else 0
                        #mstop = mstop2 if mstop2>mstop else mstop
                        cur_stop = win_stop if win_stop > mstop else mstop
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
            cur_stop = win_stop
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY    #两次乘XBUY，把符号整回来
            elif abs(mysbclose[i]) >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = abs(mysbclose[i]) *XBUY    #两次乘XBUY，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        #rev[j] = cur_stop * XBUY
                        rev[j] = (cur_stop if cur_stop > trans[IOPEN][j] else trans[IOPEN][j])* XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif abs(mysbclose[j]) >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = abs(mysbclose[j]) * XBUY   #两次乘XBUY，把符号整回来
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
                        mstop = cur_low + max_drawdown
                        #mstop2 = sell_price if sell_price - cur_low > sell_price/180 else 99999999
                        #mstop = mstop2 if mstop2 < mstop else mstop
                        cur_stop = win_stop if win_stop < mstop else mstop
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def atr_stop_x2(
        sif,
        sopened,
        sbclose,
        ssclose,
        flost_base = iftrade.F70,    #flost:买入点数 --> 止损点数
        fmax_drawdown = iftrade.F250, #最大回落比例
        pmax_drawdown = 0.012, #最大回落比例
        tstep = lambda sif,i:40,     #行情顺向滑动单位
        vstep = 20,                  #止损顺向移动单位   
        ):
    '''
    '''
    #print sbclose[-10:],ssclose[-10:]
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        willlost = flost_base(aprice)
        #willlost = sif.atr15x[i]/XBASE    #效果不佳
        spmax_drawdown = pmax_drawdown * aprice
        sfmax_drawdown = fmax_drawdown(aprice)
        max_drawdown = spmax_drawdown if spmax_drawdown < sfmax_drawdown else sfmax_drawdown
        will_losts.append(willlost)
        mytstep = tstep(sif,i)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
            #cur_stop = lost_stop if lost_stop > win_stop else win_stop
            cur_stop = win_stop #win_stop必然大于lost_stop
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格#两次乘XSELL，把符号整回来
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL   #两次乘XSELL，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        #rev[j] = cur_stop * XSELL 
                        rev[j] = (cur_stop if cur_stop < trans[IOPEN][j] else trans[IOPEN][j])* XSELL 
                        if myssclose[j] >10 and myssclose[j] > rev[j]:    #不仅仅是信号
                            rev[j] = myssclose[j] * XSELL   #两次乘XSELL，把符号整回来
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:
                        ilong_closed = j
                        #rev[j] = myssclose[j] * XSELL 
                        rev[j] = (myssclose[j] if myssclose[j] > cur_stop else cur_stop)* XSELL #两次乘XSELL，把符号整回来
                        #print 'sell in sclose:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
                        mstop = cur_high - max_drawdown
                        mstop2 = buy_price if nhigh - buy_price > nhigh/250 else 0
                        mstop = mstop2 if mstop2>mstop else mstop
                        #cur_stop = win_stop if win_stop > mstop else mstop
                        #assert cur_stop == max(mstop,mstop2,win_stop)
                        cur_stop = max(mstop,mstop2,win_stop)
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
            cur_stop = win_stop
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY    #两次乘XBUY，把符号整回来
            elif mysbclose[i] >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = mysbclose[i] *XBUY #两次乘XBUY，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        #rev[j] = cur_stop * XBUY
                        rev[j] = (cur_stop if cur_stop > trans[IOPEN][j] else trans[IOPEN][j])* XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif mysbclose[j] >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = mysbclose[j] * XBUY    #两次乘XBUY，把符号整回来
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
                        mstop = cur_low + max_drawdown
                        mstop2 = sell_price if sell_price - cur_low > cur_low/180 else 99999999
                        mstop = mstop2 if mstop2 < mstop else mstop
                        cur_stop = win_stop if win_stop < mstop else mstop
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def atr_stop_y( #atr_stop_x的最后版本，不再是主要stoper，而成为众多一致性stoper中的一个
        sif,
        sopened,
        flost_base = iftrade.F70,    #flost:买入点数 --> 止损点数
        fmax_drawdown = iftrade.F250, #最大回落比例
        pmax_drawdown = 0.012, #最大回落比例
        tstep = lambda sif,i:40,     #行情顺向滑动单位
        vstep = 20,                  #止损顺向移动单位   
        ):
    '''
    '''
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        willlost = flost_base(aprice)
        #willlost = sif.atr15x[i]/XBASE    #效果不佳
        spmax_drawdown = pmax_drawdown * aprice
        sfmax_drawdown = fmax_drawdown(aprice)
        max_drawdown = spmax_drawdown if spmax_drawdown < sfmax_drawdown else sfmax_drawdown
        will_losts.append(willlost)
        mytstep = tstep(sif,i)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
            #cur_stop = lost_stop if lost_stop > win_stop else win_stop
            cur_stop = win_stop #win_stop必然大于lost_stop
            #print 'wtarget:%s',wtarget
            print 'stop init:',buy_price,cur_stop,trans[IDATE][i],trans[ITIME][i]
            if trans[ICLOSE][i] < cur_stop:#到达止损
                print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格   #两次乘XSELL，把符号整回来
            else:
                #if trans[IDATE][i] == 20110214:
                print 'begin:',trans[IDATE][i],trans[ITIME][i],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][i]
                for j in range(i+1,len(rev)):
                    if trans[IORDER][j] >= 269: #换日
                        ilong_closed = j
                        break
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        rev[j] = (cur_stop if cur_stop < trans[IOPEN][j] else trans[IOPEN][j])* XSELL 
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        win_stop = lost_stop + (cur_high - buy_price)/mytstep * vstep
                        mstop = cur_high - max_drawdown
                        #mstop2 = buy_price if nhigh - buy_price > nhigh/250 else 0
                        #mstop = mstop2 if mstop2>mstop else mstop
                        cur_stop = win_stop if win_stop > mstop else mstop
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
            cur_stop = win_stop
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY    #两次乘XBUY，把符号整回来
            else:
                for j in range(i+1,len(rev)):
                    if trans[IORDER][j] >= 269: #换日
                        ishort_closed = j
                        break
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        #rev[j] = cur_stop * XBUY
                        rev[j] = (cur_stop if cur_stop > trans[IOPEN][j] else trans[IOPEN][j])* XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        win_stop = lost_stop - (sell_price - cur_low)/mytstep * vstep 
                        mstop = cur_low + max_drawdown
                        #mstop2 = sell_price if sell_price - cur_low > sell_price/180 else 99999999
                        #mstop = mstop2 if mstop2 < mstop else mstop
                        cur_stop = win_stop if win_stop < mstop else mstop
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def keep_stoper(
        ##这个是不妥的，单独有状态的stoper不能叠加. 因为连续的信号出来之后，前面一个如果一直没有平仓，则后面的被遮蔽了
        sif,
        sopened,
        lkeep = 250,    #cur_high的1/lkeep
        skeep = 180,    #cur_low的1/skeep
        ):
    '''
    '''
    #print sbclose[-10:],ssclose[-10:]
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            buy_price = -price
            cur_high = max(buy_price,sif.close[i])
            cur_stop = 0
            #print 'wtarget:%s',wtarget
            #print 'stop init:',cur_stop,lost_stop,willlost,min_lost,max_lost
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格
            else:
                for j in range(i+1,len(rev)):
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        rev[j] = (cur_stop if cur_stop < trans[IOPEN][j] else trans[IOPEN][j])* XSELL 
                        break
                    if trans[IORDER][j] >265:
                        ilong_closed = j
                        rev[j] = trans[IOPEN][j]
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        cur_stop = buy_price if cur_high - buy_price > cur_high/lkeep else 0
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            cur_stop = 99999999
            cur_low = min(sell_price,trans[ICLOSE][i])
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY
            else:
                for j in range(i+1,len(rev)):
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        rev[j] = (cur_stop if cur_stop > trans[IOPEN][j] else trans[IOPEN][j])* XBUY
                        break
                    if trans[IORDER][j] ==270:
                        ilong_closed = j
                        rev[j] = trans[IOPEN][j]
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        cur_stop = sell_price if sell_price - cur_low > cur_low/skeep else 99999999
                        
    #print will_losts
    #print rev[np.nonzero(rev)]
    return rev

def step_stop(
        sif
        ,sopened
        ,sbclose
        ,ssclose
        ,flost_base = iftrade.F250    #flost:买入点数 --> 止损点数
        ,step = 500  #每步50点
        ):
    '''
        根据价格突破即时止损,而不是下一个开盘价，返回值为止损价，未考虑滑点
            开仓时刻如果收盘价反向偏离开仓价超过初始止损，则也止损
        sif为实体
        sopened为价格序列，其中负数表示开多仓，正数表示开空仓
        sbclose是价格无关序列所发出的买入平仓信号集合(平空仓)
        ssclose是价格无关序列所发出的卖出平仓信号集合(平多仓)
        flost_base为初始止损函数
        只能持有一张合约。即当前合约在未平前会屏蔽掉所有其它开仓
    '''
    #print sbclose[-10:],ssclose[-10:]
    trans = sif.transaction
    rev = np.zeros_like(sopened)
    isignal = np.nonzero(sopened)[0]
    ilong_closed = 0    #多头平仓日
    ishort_closed = 0   #空头平仓日
    will_losts = []
    myssclose = ssclose * XSELL #取符号, 如果是买入平仓，则<0
    mysbclose = sbclose * XBUY #取符号, 如果是卖出平仓，则<0
    #print mysbclose[-300:]
    #print myssclose[np.nonzero(myssclose)]
    #print target
    for i in isignal:
        price = sopened[i]
        aprice = abs(price)
        willlost = flost_base(aprice)
        will_losts.append(willlost)
        if price<0: #多头止损
            #print u'多头止损'
            if i <= ilong_closed:
                #print 'long skipped'
                continue
            #print 'find long stop:',i
            #if i < ilong_closed:    #已经开了多头仓，且未平，不再计算
            #    print 'skiped',trans[IDATE][i],trans[ITIME][i],trans[IDATE][ilong_closed],trans[ITIME][ilong_closed]
            #    continue
            buy_price = -price
            lost_stop = buy_price - willlost
            cur_high = max(buy_price,sif.close[i])
            win_stop = lost_stop + (cur_high - buy_price)/step * step
            cur_stop = lost_stop if lost_stop > win_stop else win_stop
            if myssclose[i] > 0:
                #print 'sell signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                pass
            if trans[ICLOSE][i] < cur_stop:#到达止损
                #print '----sell----------:',trans[IDATE][i],trans[ITIME][i],cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ilong_closed = i
                rev[i] = cur_stop * XSELL   #设定价格
            elif myssclose[i] >0:#或平仓
                ilong_closed = i                
                rev[i] = myssclose[i] * XSELL
            else:
                for j in range(i+1,len(rev)):
                    tv = sif.close[j] - buy_price
                    #print trans[ITIME][j],buy_price,lost_stop,cur_high,win_stop,cur_stop,trans[ILOW][j],satr[j]
                    if trans[ILOW][j] < cur_stop:
                        ilong_closed = j
                        rev[j] = cur_stop * XSELL 
                        #print 'sell in atrstop:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    elif  myssclose[j] >0:
                        ilong_closed = j
                        rev[j] = myssclose[j] * XSELL 
                        #print 'sell in sclose:'#,i,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j],sif.low[j],cur_stop
                        break
                    nhigh = trans[IHIGH][j]
                    if(nhigh > cur_high):
                        cur_high = nhigh
                        win_stop = lost_stop + (cur_high - buy_price)/step * step
                        if cur_stop < win_stop:
                            cur_stop = win_stop
        else:   #空头止损
            #print 'find short stop:',i
            if i<=ishort_closed:
                #print 'short skipped'
                continue
            sell_price = price
            lost_stop = sell_price + willlost
            cur_low = min(sell_price,trans[ICLOSE][i])
            win_stop = lost_stop - (sell_price - cur_low)/step * step
            cur_stop = lost_stop if lost_stop < win_stop else win_stop
            if trans[ICLOSE][i] > cur_stop:
                #print '----buy----------:',cur_stop,trans[ICLOSE][i],cur_high,lost_stop
                ishort_closed = i
                rev[i] = cur_stop * XBUY
            elif mysbclose[i] >0:
                #print 'buy signali:',trans[IDATE][i],trans[ITIME][i],trans[ICLOSE][i]
                ishort_closed = i
                rev[i] = mysbclose[i] *XBUY
            else:
                for j in range(i+1,len(rev)):
                    tv = sell_price - sif.close[j]
                    #print trans[ITIME][j],sell_price,lost_stop,cur_low,win_stop,cur_stop,trans[IHIGH][j],satr[j]                
                    if trans[IHIGH][j] > cur_stop:
                        ishort_closed = j
                        rev[j] = cur_stop * XBUY
                        #print 'buy:',j
                        #print 'buy:',i,price,trans[IDATE][i],trans[ITIME][i],trans[IDATE][j],trans[ITIME][j]                        
                        break
                    elif mysbclose[j] >0:
                        #print 'buy signalj:',trans[IDATE][j],trans[ITIME][j],cur_stop,trans[ICLOSE][j]
                        ishort_closed = j
                        rev[j] = mysbclose[j] * XBUY
                        break
                    nlow = trans[ILOW][j]
                    if(nlow < cur_low):
                        cur_low = nlow
                        win_stop = lost_stop - (sell_price - cur_low)/step * step
                        if cur_stop > win_stop:
                            cur_stop = win_stop
    return rev

def sync_tradess_u(sif,tradess,acstrategy=iftrade.late_strategy):
    '''
        结合优先级和顺势逆势关系
        顺势信号可以逆反优先级小于等于它的逆势信号
        逆势信号不能逆反顺势信号
        低优先级顺势信号不能逆反高优先级顺势信号

    '''
    trans = sif.transaction
    sdate = trans[IDATE]
    stime = trans[ITIME]
    sopen = trans[IOPEN]
    sclose = trans[ICLOSE]
    shigh = trans[IHIGH]
    slow = trans[ILOW]    
    
    xtrades = []
    finished =False
    cur_trade = iftrade.find_first(tradess)
    if cur_trade == None:
        return []
    cur_trade.orignal = cur_trade.functor   
    cur_trade.open_action = cur_trade.actions[0]
    extended,filtered,rfiltered,reversed = [],[],[],[]
    close_action = cur_trade.actions[-1]
    #print '#####################first:',close_action.time
    while True:
        #print cur_trade.orignal
        trade = iftrade.find_first(tradess)
        if trade == None:
            xtrades.append(iftrade.close_trade(sif,cur_trade,close_action,extended,filtered,rfiltered,reversed))
            break
        #print 'find:date=%s,time=%s,functor=%s,priority=%s' % (trade.actions[0].date,trade.actions[0].time,trade.functor,fpriority(trade.functor))  
        #if trade.actions[0].xfollow <= 0:
        #    continue
        if DTSORT2(trade.actions[0],close_action)>0:  #时间超过
            #print u'时间超过'
            xtrades.append(iftrade.close_trade(sif,cur_trade,close_action,extended,filtered,rfiltered,reversed))
            trade.orignal = trade.functor
            cur_trade = trade
            close_action = cur_trade.actions[-1]
            extended,filtered,rfiltered,reversed = [],[],[],[]
            #print cur_trade.orignal
            trade.open_action = trade.actions[0]
            continue
           
        #if trade.actions[0].index > cur_trade.actions[0].index and (iftrade.aprofit(cur_trade.open_action,sclose[trade.actions[0].index]) > 251 
        #        or iftrade.aprofit(cur_trade.open_action,sclose[trade.actions[0].index]) < 31
        #        or trade.actions[0].index - cur_trade.actions[0].index > 20
        #        ):   #取决于浮动收益和持仓时间,大于25就平调(宁可后面再开)，小于3也平掉
        if trade.actions[0].index > cur_trade.actions[0].index: #必然平掉
            if trade.direction == cur_trade.direction:  #同向取代关系
                #print u'同向增强,%s|%s:%s被%s增强'%(cur_trade.functor,cur_trade.actions[0].date,cur_trade.actions[0].time,trade.functor)
                close_action = acstrategy(close_action,trade.actions[-1])
                extended.append(cur_trade)
                trade.orignal = cur_trade.orignal
                trade.open_action = cur_trade.open_action
                cur_trade = trade
            else:   #逆向平仓
            #elif 1>2:   #不逆向. 差别太小
                print u'\n\t逆向平仓:',iftrade.aprofit(cur_trade.open_action,sclose[trade.actions[0].index]),sif.date[cur_trade.open_action.index],sif.time[cur_trade.open_action.index],func_name(cur_trade.orignal),'--',func_name(trade.functor)
                reversed.append(trade)
                xindex = reversed[0].actions[0].index
                cposition = BaseObject(index=xindex,date=sdate[xindex],time=stime[xindex],position=reversed[0].direction,xtype=XCLOSE)    #因为已经抑制了1514开仓,必然不会溢出
                cposition.price = make_close_price(cposition.position,sopen[xindex],sclose[xindex],shigh[xindex],slow[xindex])
                xtrades.append(iftrade.close_trade(sif,cur_trade,cposition,extended,filtered,rfiltered,reversed))
                trade.orignal = trade.functor
                trade.open_action = trade.actions[0]
                cur_trade = trade
                extended,filtered,rfiltered,reversed = [],[],[],[]
                close_action = cur_trade.actions[-1]                
                ##逆向平仓但不开
                #reversed.append(trade)
                #xindex = reversed[0].actions[0].index
                #close_action = BaseObject(index=xindex,date=sdate[xindex],time=stime[xindex],position=reversed[0].direction,xtype=XCLOSE)    #因为已经抑制了1514开仓,必然不会溢出
                #close_action.price = make_close_price(close_action.position,sopen[xindex],sclose[xindex],shigh[xindex],slow[xindex])

        else:   #低优先级或逆势对顺势
            #print u'低优先级'
            if trade.direction == cur_trade.direction:  #同向屏蔽
                filtered.append(trade)
            else:   #逆向屏蔽
                rfiltered.append(trade)
    return xtrades

def make_close_price(position,open,close,high,low):
    if position == LONG:
        return (open+high)/2
    else:
        return (open+low)/2


def utrade_x(sif     #期指
            ,openers    #opener函数集合
            ,bclosers   #默认的多平仓函数集合(空头平仓)
            ,sclosers   #默认的空平仓函数集合(多头平仓)
            ,stop_closer    #止损closer函数，只能有一个，通常是atr_uxstop,    
                            #有针对性是指与买入价相关的 stop_closer必须处理之前的closers系列发出的卖出信号
            ,osc_stop_closer = None#震荡止损函数
            ,longfilter=iftrade.ocfilter    #opener过滤器,多空仓必须满足各自过滤器条件才可以发出信号. 
                                    #比如抑制在0915-0919以及1510-1514开仓等
                                    #closer没有过滤器,设置过滤器会导致合约一直开口
            ,shortfilter=iftrade.ocfilter   #opener过滤器,多空仓必须满足各自过滤器条件才可以发出信号. 
            ,make_trades=iftrade.simple_trades  #根据开平仓动作撮合交易的函数。对于最后交易序列，用last_trades
            ,sync_trades=sync_tradess_u    #汇总各opener得到的交易，计算优先级和平仓。
                                            #对于最后交易序列，用null_sync_tradess
            ,acstrategy=iftrade.late_strategy   #增强开仓时的平仓策略。late_strategy是平最晚的那个信号
            ,priority_level=2500    #筛选opener的优先级, 忽略数字大于此的开仓
        ):
    '''
        本函数针对每个opener计算出各自的闭合交易
        然后集中处理这些闭合交易，根据优先级来确认交易的持续性
            最终得到从开仓到平仓的单个交易的集合
            其中单个交易的要素有：
                开仓价格、时间、交易量
                平仓价格、时间、交易量
                当前主方法名(持有合约的方法)
                filtered: 开仓后被过滤掉的同向低优先级方法名及其信号价格和时间
                rfiltered:开仓后被过滤掉的反向低优先级方法名及其信号价格和时间
                extended: 曾经起效，但因优先级低而被取代的同向方法名及其信号价格和时间. 第一个价格即是开仓价格
                reversed: 逆转持仓的方法及其信号价格和时间
                          如优先级高的中止本次持仓的方法。通常导致反向开仓。  
            要求每个方法的属性有：
                direction:  多/空方向 XBUY/XSELL
                priority:   优先级, 数字越低越高
                            如果不存在，默认为0
                closer:     平仓方法
                            签名为 closer(closers):closers
                                根据传入的closers，返回处理后的，这样，可以取代默认的，也可以在默认之后附加
                            如果不存在，就使用默认的
                stop_closer 止损方法[单个], 如果存在，就取代默认的                                
                filter:     符合filter签名的filter
                name:       名字

    '''
    slongfilter = longfilter(sif)
    sshortfilter = shortfilter(sif)
    snull = np.zeros_like(sif.close)
    if not isinstance(openers,list):   #单个函数
        openers = [openers]
    if not isinstance(bclosers,list):   #单个函数
        bclosers = [bclosers]
    if not isinstance(sclosers,list):   #单个函数
        sclosers = [sclosers]
    
    openers = [opener for opener in openers if iftrade.fpriority(opener)<priority_level]

    tradess = []
    for opener in openers:
        #if 'filter' not in opener.__dict__: #用于对信号进行过滤,如开盘30分钟内不发出信号等
        #    myfilter = slongfilter if iftrade.fdirection(opener) == XBUY else sshortfilter
        #else:
        #    myfilter = opener.filter(sif)
        if iftrade.fdirection(opener) == XBUY:
            if 'is_followed' in opener.__dict__ and opener.is_followed == True: #如果设定为follow，则使用默认
                #print 'is_followed x:',longfilter,pstate_oc_filter
                myfilter = slongfilter
            elif 'longfilter' in opener.__dict__:
                #print 'lfilter'
                myfilter = opener.longfilter(sif)
            elif 'filter' in opener.__dict__:
                print 'buy infilter:'
                myfilter = opener.filter(sif)
            else:
                myfilter = slongfilter
        else:#XSELL
            if 'is_followed' in opener.__dict__ and opener.is_followed == True: #如果设定为follow，则使用默认
                #print 'is_followed y:',shortfilter,npstate_oc_filter
                myfilter = sshortfilter
            elif 'shortfilter' in opener.__dict__:
                #print 'sfilter'                
                myfilter = opener.shortfilter(sif)
            elif 'filter' in opener.__dict__:
                print 'sell,infilter:'                
                myfilter = opener.filter(sif)
            else:
                myfilter = sshortfilter
        if 'xfilter' not in opener.__dict__:    #xfilter用于自定义的信号变换,如根据5分钟内的波动决定延迟发送还是吞没
            xfilter = iftrade.gothrough_filter
        else:
            xfilter = opener.xfilter
        opens = uopen_position(sif,xfilter(sif,opener(sif)),myfilter,myfilter) #因为opener只返回一个方向的操作,所以两边都用myfilter，但实际上只有相应的一个有效，另一个是虚的
        #opens.sort(DTSORT)
        sopened = np.zeros(len(sif.transaction[IDATE]),int)   #为开仓价格序列,负数为开多仓,正数为开空仓
        for aopen in opens:
            sopened[aopen.index] = aopen.price * aopen.position
        sclose = np.zeros(len(sif.transaction[IDATE]),int)
        if 'closer' in opener.__dict__: #是否有特定的closer,如要将macd下叉也作为多头持仓的平仓条件,则可设置函数,在返回值中添加该下叉信号算法
            if iftrade.fdirection(opener) == XBUY:
                #print 'buy closer:',opener.closer
                closers = opener.closer(sclosers)
            elif iftrade.fdirection(opener) == XSELL:
                closers = opener.closer(bclosers)
        else:
            #print 'opener without close fdirection(opener) = %s' % ('XBUY' if fdirection(opener) == XBUY else 'XSELL',)
            closers = sclosers if iftrade.fdirection(opener) == XBUY else bclosers
        for closer in closers:
            sclose = gor(sclose,closer(sif,sopened)) * (-iftrade.fdirection(opener))
        if osc_stop_closer == None:
            osc_stop_closer = stop_closer 
        ms_closer = stop_closer if 'stop_closer' not in opener.__dict__ else opener.stop_closer
        
        if 'osc_stop_closer' not in opener.__dict__:
            osc_closer = opener.stop_closer if 'stop_closer' in opener.__dict__ else osc_stop_closer
        else:
            osc_closer = opener.osc_stop_closer

        #closes = uclose_position(sif,stop_closer(sif,sopened,sclose,sclose)) #因为是单向的，只有一个sclose起作用
        
        ms_sclose = ms_closer(sif,sopened,sclose,sclose)
        osc_sclose = osc_closer(sif,sopened,sclose,sclose)
        #sclose的优先级最高. ms_closer是atr类的止损,与osc是竞争关系
        xsclose = np.select([sif.xstate!=0,sif.xstate==0],[ms_sclose,osc_sclose])
        #xsclose = np.select([sclose!=0,sif.xstate!=0,sif.xstate==0],[sclose,ms_sclose,osc_sclose])
        
        xsclose = np.select([sclose!=0],[sclose],default=xsclose)   #不能用gor，gor后-1变1，就没有闭合交易了

        #closes = uclose_position(sif,ms_sclose)
        closes = uclose_position(sif,xsclose)
        #closes = uclose_position(sif,ms_closer(sif,sopened,sclose,sclose)) #因为是单向的，只有一个sclose起作用        


        actions = sorted(opens + closes,iftrade.DTSORT2)
        for action in actions:
            action.name = sif.name
            #print action.name,action.date,action.time,action.position,action.price
        trades = make_trades(actions)   #trade: [open , close] 的序列, 其中前部分都是open,后部分都是close
        for trade in trades:
            trade.functor = opener
            trade.direction = trade.actions[0].position   #LONG/SHORT
            #print trade.actions[0].date,trade.actions[0].time,trade.direction
        tradess.append(trades)
    return sync_trades(sif,tradess,acstrategy)


def utrade(sif     #期指
            ,openers    #opener函数集合
            ,bclosers   #默认的多平仓函数集合(空头平仓)
            ,sclosers   #默认的空平仓函数集合(多头平仓)
            ,stop_closer    #止损closer函数，只能有一个，通常是atr_uxstop,    
                            #有针对性是指与买入价相关的 stop_closer必须处理之前的closers系列发出的卖出信号
            ,make_trades=iftrade.simple_trades  #根据开平仓动作撮合交易的函数。对于最后交易序列，用last_trades
            ,sync_trades=sync_tradess_u    #汇总各opener得到的交易，计算优先级和平仓。
                                            #对于最后交易序列，用null_sync_tradess
            ,acstrategy=iftrade.late_strategy   #增强开仓时的平仓策略。late_strategy是平最晚的那个信号
            ,priority_level=2500    #筛选opener的优先级, 忽略数字大于此的开仓
        ):
    '''
        本函数针对每个opener计算出各自的闭合交易
        然后集中处理这些闭合交易，根据优先级来确认交易的持续性
            最终得到从开仓到平仓的单个交易的集合
            其中单个交易的要素有：
                开仓价格、时间、交易量
                平仓价格、时间、交易量
                当前主方法名(持有合约的方法)
                filtered: 开仓后被过滤掉的同向低优先级方法名及其信号价格和时间
                rfiltered:开仓后被过滤掉的反向低优先级方法名及其信号价格和时间
                extended: 曾经起效，但因优先级低而被取代的同向方法名及其信号价格和时间. 第一个价格即是开仓价格
                reversed: 逆转持仓的方法及其信号价格和时间
                          如优先级高的中止本次持仓的方法。通常导致反向开仓。  
            要求每个方法的属性有：
                direction:  多/空方向 XBUY/XSELL
                priority:   优先级, 数字越低越高
                            如果不存在，默认为0
                closer:     平仓方法
                            签名为 closer(closers):closers
                                根据传入的closers，返回处理后的，这样，可以取代默认的，也可以在默认之后附加
                            如果不存在，就使用默认的
                stop_closer 止损方法[单个], 如果存在，就取代默认的                                
                name:       名字

    '''
    if not isinstance(openers,list):   #单个函数
        openers = [openers]
    if not isinstance(bclosers,list):   #单个函数
        bclosers = [bclosers]
    if not isinstance(sclosers,list):   #单个函数
        sclosers = [sclosers]
    
    openers = [opener for opener in openers if iftrade.fpriority(opener)<priority_level]

    tradess = []
    for opener in openers:
        opens = uopen_position(sif,opener(sif))
        odir = iftrade.fdirection(opener)
        sopened = np.zeros(len(sif.date),int)   #为开仓价格序列,负数为开多仓,正数为开空仓
        for aopen in opens:
            sopened[aopen.index] = aopen.price * aopen.position
        sclose = np.zeros(len(sif.date),int)
        if 'closer' in opener.__dict__: #是否有特定的closer,如要将macd下叉也作为多头持仓的平仓条件,则可设置函数,在返回值中添加该下叉信号算法
            if odir == XBUY:
                #print 'buy closer:',opener.closer
                closers = opener.closer(sclosers)[:]    #复制
            elif odir == XSELL:
                closers = opener.closer(bclosers)[:]
        else:
            #print 'opener without close iftrade.fdirection(opener) = %s' % ('XBUY' if iftrade.fdirection(opener) == XBUY else 'XSELL',)
            closers = sclosers[:] if odir == XBUY else bclosers[:]


        #这里需要u处理
        if odir == XBUY:#卖平
            psclose = np.select([sclose],[np.abs(sclose)],PS_MAX)    #把0转换为最大值
            for closer in closers:#这里默认认为closer返回的数据中只要非0就算是有信号, 而不是区分买平还是卖平
                cur_s = closer(sif,sopened)
                #print closer,cur_s[-300:],XSELL,odir
                cur_ps = np.select([cur_s!=0],[np.abs(cur_s)],PS_MAX)   #把0转换为最大值
                psclose = gmin(psclose,cur_ps)       #卖出选最小
            sclose = np.select([psclose!=PS_MAX],[psclose* (-odir)],0) #将PS_MAX变回0, 已经有符号了
            #print sclose[np.nonzero(sclose)]
        else:#买平
            psclose = np.abs(sclose)
            for closer in closers:#这里默认认为closer返回的数据中只要非0就算是有信号, 而不是区分买平还是卖平
                psclose = gmax(psclose,np.abs(closer(sif,sopened)))
            sclose = psclose * (-odir)  #已经有符号了

        ms_closer = stop_closer if 'stop_closer' not in opener.__dict__ else opener.stop_closer
        
        closes = uclose_position(sif,ms_closer(sif,sopened,sclose,sclose)) #因为是单向的，只有一个sclose起作用        

        #print ms_closer(sif,sopened,sclose,sclose)[-300:]
        #print closes[-1].time,closes[-1].date,closes[-2].date,closes[-2].time
        #print opens[-1].time,opens[-1].date,opens[-2].date,opens[-2].time
        #print 'iclose:'
        #for iclose in closes:
        #    print iclose.date,iclose.time
        
        actions = sorted(opens + closes,iftrade.DTSORT2) #必须确保先开后平, 但如果已经开了，则只有平仓
        #print len(opens+closes),len(actions)
        for action in actions:
            action.name = sif.name
            #print action.name,action.date,action.time,action.position,action.price
        trades = make_trades(actions)   #trade: [open , close] 的序列, 其中前部分都是open,后部分都是close
        for trade in trades:
            trade.functor = opener
            trade.direction = trade.actions[0].position   #LONG/SHORT
            #print trade.actions[0].date,trade.actions[0].time,trade.direction
        tradess.append(trades)
    return sync_trades(sif,tradess,acstrategy)

def uopen_position(sif,sopener):
    '''
        sopener中,XBUY表示开多仓,XSELL表示开空仓
    '''
    pbuy = sopener * XBUY  #取数字, 如果是卖出平仓，则<0    
    psell = sopener * XSELL #取数字, 如果是买入平仓，则<0

    pslong = np.select([pbuy>0],[pbuy*LONG],0)
    psshort = np.select([psell>0],[psell*SHORT],0)    
    positions = uposition(sif,pslong,XOPEN)
    positions.extend(uposition(sif,psshort,XOPEN))
    return positions


def uclose_position(sif,scloser):
    ''' scloser中, XBUY表示平空(买入),XSELL表示平多(卖出)
    '''
    #print 'in uclose position'

    pbuy = scloser * XBUY  #取数字
    psell = scloser * XSELL #取数字

    pslong = np.select([pbuy>0],[pbuy*LONG],0)
    psshort = np.select([psell>0],[psell*SHORT],0)    
    
    positions = uposition(sif,pslong,XCLOSE)
    positions.extend(uposition(sif,psshort,XCLOSE))
    return positions


def uposition(sif,saction,xtype,defer=1):
    '''
        针对saction进行开仓或平仓
        如果与XLONG同向则开多仓     
            与XSHORT同向则开空仓
        如果价格的绝对值==1则按defer在开盘处开仓，否则按指定价即时开仓
    '''
    isignal = saction.nonzero()[0]
    positions = []
    for i in isignal:
        uprice = saction[i] #可能是信号，也可能是信号叠加价格
        direct = np.sign(uprice)    #如果是信号叠加价格，则其方向和信号方向一致
        xindex = i+defer if is_only_position_signal(uprice) else i  #如果是信号则按defer计算，是价格则即时发生
        if xindex >= len(sif.close):   #如果是最后一分钟，则放弃. 这种情况只会出现在动态计算中，且该分钟未走完(走完的话应该出现下一分钟的报价)，所以放弃是正常操作
            continue
        xprice = iftrade.make_price(direct,sif.open[xindex],sif.close[xindex],sif.high[xindex],sif.low[xindex]) if is_only_position_signal(uprice) else np.abs(uprice)
        #print xindex,len(sif.close)
        position = BaseObject(index=xindex,date=sif.date[xindex],time=sif.time[xindex],price=xprice,position=direct,xtype=xtype)    #因为已经抑制了1514开仓,必然不会溢出
        positions.append(position)
        if xtype == XOPEN:
            #顺势、逆势以及不明势
            if saction[i] == LONG:
                if sif.xstate[i] > 0:
                    position.xfollow = 1
                elif sif.xstate[i] < 0:
                    position.xfollow = -1
                else:
                    position.xfollow = 0
            else:
                if sif.xstate[i] < 0:
                    position.xfollow = 1
                elif sif.xstate[i] > 0:
                    position.xfollow = -1
                else:
                    position.xfollow = 0
    return positions

def day_trades(trades,limit=-200):
    '''
        每日连续回撤到limit(含limit)之后不再开仓. 即如果已经损失20点，limit=-20，则不能再开仓
        在中间即便有盈利，但是如果累计起来仍然为负，则持续计算
        最终返回每日的交易，其中profit为不过滤的值，sprofit为过滤后的,ntrade为每日的交易次数
            trades为当日交易
        总交易次数:    sum([trade.ntrade for trade in trades])
        总盈亏:        sum([trade.sprofit for trade in trades])
    '''
    if len(trades) == 0:
        return []
    cur_trade = trades[0]
    results = [BaseObject(day=cur_trade.actions[-1].date,
                            profit=cur_trade.profit,
                            sprofit = cur_trade.profit,
                            max_drawdown=cur_trade.profit if cur_trade.profit < 0 else 0,
                            ntrade = 1,
                            ontrade = 1,
                            tclose = 0,
                            trades = [cur_trade],
                            ii = cur_trade.actions[0].index,
                        )
                ]
    for trade in trades[1:]:
        tdate = trade.actions[-1].date
        tclose = trade.actions[-1].time
        topen = trade.actions[0].time
        rlast = results[-1]
        if tdate ==rlast.day:
            rlast.profit += trade.profit
            rlast.ontrade += 1
            last_drawdown = rlast.max_drawdown
            if rlast.sprofit > limit or topen < rlast.tclose:
                if rlast.sprofit > limit and trade.profit < 0 and tclose > rlast.tclose:   
                    #对未超界的亏损交易,设定最后平仓时间,用来在之后判断是否应当开新仓
                    rlast.tclose = tclose
                rlast.sprofit += trade.profit
                rlast.ntrade += 1
                rlast.max_drawdown += trade.profit
                rlast.trades.append(trade)
                if rlast.max_drawdown > 0:
                    rlast.max_drawdown = 0
                elif rlast.max_drawdown > last_drawdown:
                    rlast.max_drawdown = last_drawdown
        else:
            results.append(BaseObject(day=tdate,
                        profit=trade.profit,
                        sprofit = trade.profit,                            
                        max_drawdown=trade.profit if trade.profit < 0 else 0,
                        ntrade = 1,
                        ontrade = 1,
                        tclose = 0,
                        trades = [trade],
                        ii = trade.actions[0].index,
                    )
            )
    return results


def dmax_drawdown(dtrades,datefrom=20100401,dateto=20200101):
    '''
        按日计算. 计算结果可能会比按笔计算的最大回撤小，因为按日计算是按日汇总的
            碰到按笔的最大回撤日，很可能该日前几笔亏损，但最后是盈利的，那么按日的话该日就不算亏损日
            而按笔计算的时候，该日的前几笔亏损也被累计到最大回撤中了
        dtrades为每日的交易汇总
    '''
    smax = 0    #最大连续回撤
    max1 = 0    #最大单日回撤
    curs = 0
    mdate = 20100401
    for trade in dtrades:
        tdate = trade.day
        if tdate > datefrom and tdate < dateto: #忽略掉小于开始时间的
            curs += trade.sprofit   #本为负数
            if curs > 0:
                curs = 0
            elif curs < smax:
                smax = curs
                mdate = tdate
            if trade.sprofit < max1:
                max1 = trade.sprofit
                #print tdate,max1
    return smax,max1,mdate


atr5_ustop_V = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F60,
                fmax_drawdown=iftrade.F333
            )      #


atr5_ustop_V7 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F70,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V712 = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F70,
                fmax_drawdown=iftrade.F333
            )      #


atr5_ustop_V8 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F80,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V9 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F90,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V10 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F100,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V12 = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F120,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V15 = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F150,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V20 = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F200,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V25 = fcustom(atr_stop_u,
                fkeeper=iftrade.F150,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F250,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V6 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F60,
                fmax_drawdown=iftrade.F333
            )      #

atr5_ustop_V12 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F120,
                fmax_drawdown=iftrade.F333
            )      #


atr5_ustop_T = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F70, #从6改到7
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )      #

atr5_ustop_TU = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F70, #从6改到7
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )      #

atr5_ustop_TD = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=iftrade.F70, #从6改到7
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )      #

atr5_ustop_T9 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=lambda x:90,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )   #

atr5_ustop_TA = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,   #12为好,15太大了，相当于回撤15+9=24点
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=lambda x:70,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )   #

atr5_ustop_TB = fcustom(atr_stop_u,
                fkeeper=iftrade.F120,   #12为好,15太大了，相当于回撤15+9=24点
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=lambda x:100,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                tlimit = 30,
            )   #

atr5_ustop_TT = fcustom(atr_stop_u2,
                fkeeper=iftrade.F300,
                #win_times=250,                
                #win_times=280,
                #natr=5,
                win_times=40,
                natr = 270,
                flost_base=100,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
                natr2 = 30,
                #tlimit = 30,
            )      #

atr5_ustop_TU = fcustom(atr_stop_u2,
                keeper_base=50,
                nkeeper = 270,
                win_times=60,
                natr = 270,
                flost_base=10,
                natr2 = 270,
            )      #


atr5_ustop_TV = fcustom(atr_stop_u2,
                keeper_base=20,
                nkeeper = 270,
                win_times=40,
                natr = 270,
                flost_base=12,
                natr2 = 270,
            )#

atr5_ustop_TX = fcustom(atr_stop_u2,
                keeper_base=400,
                nkeeper = 1,
                win_times=800,
                natr = 1,
                flost_base=600,
                natr2 = 1,
            )#

atr5_ustop_T5 = fcustom(atr_stop_u,
                fkeeper=iftrade.F80,
                win_times=250,
                natr=5,
                flost_base=iftrade.F50,
                fmax_drawdown=iftrade.F333,
                tlimit = 30,
            )      #


atr5_ustop_T1 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        #,win_times=280
        #,natr=5
        ,win_times = 40
        ,natr=270
        ,flost_base=iftrade.F80 #
        ,fmax_drawdown=iftrade.F333
        ,tlimit = 15,
        )      #120-60
atr5_ustop_TV1 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        #,win_times=250
        #,natr=5
        ,win_times = 40
        ,natr=270
        ,flost_base=iftrade.F40 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333
        ,tlimit = 30,
      )      #120-60

atr5_ustop_TX4 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F60
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F40 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333
        ,tlimit = 30,
      )      #120-60

atr5_ustop_VX = fcustom(atr_stop_u,#有浮盈持有到收盘
                fkeeper=iftrade.F90,
                win_times=250,
                natr=5,
                flost_base=iftrade.F250,
                fmax_drawdown=lambda x:100000,
                fmin_drawdown=lambda x:100000,                
            )      

atr5_ustop_VY = fcustom(atr_stop_u,#
                fkeeper=iftrade.F120,
                #win_times=250,
                #natr=5,
                win_times = 40,
                natr = 270,
                flost_base=lambda x:90,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F250,
            )      


atr5_ustop_VZ = fcustom(atr_stop_u,#有浮盈持有到收盘
                fkeeper=iftrade.F100,
                #win_times=250,
                #natr=5,
                win_times = 40,
                natr = 270,
                flost_base=iftrade.F100,
                fmax_drawdown=iftrade.F333,
                fmin_drawdown=iftrade.F150,
            )      


atr5_ustop_V5 = fcustom(atr_stop_u,
                fkeeper=iftrade.F150,
                win_times=250,
                natr=5,
                flost_base=iftrade.F60,
                fmax_drawdown=iftrade.F333
            )      #

#V1的回报类似(减少10%)，单次止损小,回撤收窄.R大
atr5_ustop_V0 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F20 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_V1 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        #,win_times=250
        #,natr=5
        ,win_times = 40
        ,natr=270
        ,flost_base=iftrade.F40 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333
        ,fmin_drawdown=iftrade.F250
        #,fmin_drawdown=iftrade.F150
        )      #120-60

atr5_ustop_V2 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F30 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_V1_LK = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F40 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmin_drawdown=iftrade.F100        
        ,fmax_drawdown=iftrade.F100)      #120-60


atr5_ustop_X = fcustom(atr_stop_u
        ,fkeeper=iftrade.F150
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F60 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_X1 = fcustom(atr_stop_u
        ,fkeeper=iftrade.F80
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F80 #
        ,fmax_drawdown=iftrade.F333
        )      #120-60

atr5_ustop_X2 = fcustom(atr_stop_u
        ,fkeeper=lambda x: 60#
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F30 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_X3 = fcustom(atr_stop_u
        ,fkeeper=lambda x: 100#效果和X2差不多,哲学上选择这个。倡导较长持仓
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F30 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_X4 = fcustom(atr_stop_u
        ,fkeeper=lambda x: 60#
        ,win_times=250
        ,natr=5
        ,flost_base=iftrade.F40 #止损太窄不好操作，很可能还没设止损单就已经破了
        ,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_XX = fcustom(atr_stop_u, #有浮盈持有到收盘
                fkeeper=iftrade.F80,
                win_times=250,
                natr=5,
                flost_base=iftrade.F80,
                fmax_drawdown=iftrade.F333,
            )      

atr5_ustop_W1 = fcustom(atr_stop_u,fkeeper=iftrade.F120,win_times=250,natr=5,flost_base=iftrade.F60,fmax_drawdown=iftrade.F333)      #120-60
atr5_ustop_V3 = fcustom(atr_stop_u,fkeeper=iftrade.F90,win_times=250,natr=5,flost_base=iftrade.F80,fmax_drawdown=iftrade.F333)      #120-60

atr5_ustop_5 = fcustom(atr_stop_u
                ,fkeeper=iftrade.F50
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F30
                ,fmax_drawdown=iftrade.F180
                ,fmin_drawdown=iftrade.F100                
                #,ftarget = iftrade.F180
            )

atr5_ustop_6 = fcustom(atr_stop_u
                ,fkeeper=iftrade.F80
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F60
                ,fmax_drawdown=iftrade.F120
                ,fmin_drawdown=iftrade.F80
                #,ftarget = iftrade.F180
            )

atr5_ustop_61 = fcustom(atr_stop_u
                ,fkeeper=iftrade.F60
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F40
                ,fmax_drawdown=iftrade.F120
                ,fmin_drawdown=iftrade.F80
                #,ftarget = iftrade.F180
            )

atr5_ustop_62 = fcustom(atr_stop_u
                ,fkeeper=iftrade.F80
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F30
                ,fmax_drawdown=iftrade.F120
                ,fmin_drawdown=iftrade.F80
                #,ftarget = iftrade.F180
            )

atr5_ustop_63 = fcustom(atr_stop_u
                ,fkeeper=iftrade.F80
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F30
                ,fmax_drawdown=iftrade.F120
                ,fmin_drawdown=iftrade.F120
                #,ftarget = iftrade.F180
            )

atr5_ustop_j = fcustom(atr_stop_u
                ,fkeeper=iftrade.F50
                ,win_times=250
                ,natr=5
                ,flost_base=iftrade.F30
                ,fmax_drawdown=iftrade.F80
                ,fmin_drawdown=iftrade.F80                
                #,ftarget = iftrade.F180
            )      #120-60


step_stop_12 = fcustom(step_stop,
                flost_base = iftrade.F120,
                step = 240,
                )

step_stop_7 = fcustom(step_stop,
                #flost_base = iftrade.F180,
                flost_base = lambda x:275,
                step = 550,
                )

vstop_9_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F90,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_10_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F100,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )


def PSTOP_BASE(price,p=0.004):
    sbase = int(price * p + 0.5)/10*10
    return sbase

def SSTOP_BASE(price):
    if price > 40000:
        return 120
    if price > 34000:
        return 110
    if price > 27000:
        return 100
    elif price > 18000:
        return 90
    elif price > 10000:
        return 80
    return 50

vstop_10_42 = fcustom(atr_stop_x,
                flost_base = iftrade.F100, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_10_42 = fcustom(atr_stop_x,
                flost_base = lambda p:p/250, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_10_21 = fcustom(atr_stop_x,
                flost_base = lambda p:p/250, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:20,     
                vstep = 10,                  
            )

vstop_5_21 = fcustom(atr_stop_x,
                flost_base = lambda p:p/666, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:20,     
                vstep = 10,                  
            )

vstop_6_21 = fcustom(atr_stop_x,
                flost_base = lambda p:p/400, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:20,     
                vstep = 12,                  
            )


vstop_8_21 = fcustom(atr_stop_x,
                flost_base = lambda p:p/300, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:20,     
                vstep = 10,                  
            )


vstop2_10_42 = fcustom(atr_stop_x2,
                flost_base = iftrade.F100, 
                #flost_base = SSTOP_BASE, 
                fmax_drawdown = iftrade.F360, 
                pmax_drawdown = 0.011, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )


vstop_12_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F120,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_15_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F150,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )


vstop_7_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F70,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_8_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F80,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_6_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F60,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )


vstop_5_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F50,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )

vstop_4_42 = fcustom(atr_stop_v,
                flost_base = iftrade.F40,    
                fmax_drawdown = iftrade.F360, 
                tstep = lambda sif,i:40,     
                vstep = 20,                  
            )



###这里设定的stop_closer会被opener函数指定的stop_closer所覆盖
utrade_n0 = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[ifuncs.daystop_short],sclosers=[ifuncs.daystop_long])
#utrade_n = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[],sclosers=[])
utrade_m = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[stop_short_3],sclosers=[stop_long_3])  #最后平仓. 增长惊人
#utrade_n = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[last_stop_short],sclosers=[last_stop_long])
utrade_d = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[ifuncs.xdaystop_short],sclosers=[ifuncs.xdaystop_long],make_trades=iftrade.last_trades,sync_trades=iftrade.null_sync_tradess)

utrade_n = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[fcustom(last_stop_short2,ttrace=250,tend=266,vbegin=0.020)],sclosers=[fcustom(last_stop_long2,ttrace=240,tend=266,vbegin=0.020)])

utrade_nk = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[fcustom(last_stop_short2,ttrace=250,tend=266,vbegin=0.020),keep_stoper],sclosers=[fcustom(last_stop_long2,ttrace=240,tend=266,vbegin=0.020),keep_stoper])


utrade_c = fcustom(utrade,stop_closer=atr5_ustop_V,bclosers=[ifuncs.daystop_short_c],sclosers=[ifuncs.daystop_long_c])


utrade_nr = fcustom(utrade,make_trades=repeat_trades,sync_trades=iftrade.null_sync_tradess,stop_closer=atr5_ustop_V,bclosers=[ifuncs.daystop_short],sclosers=[ifuncs.daystop_long])

utrade_s = fcustom(utrade,stop_closer=step_stop,bclosers=[ifuncs.daystop_short],sclosers=[ifuncs.daystop_long])

#最简单的合并
#>>> tz2 = sorted(tz2,lambda tradex,tradey:cmp(tradex.actions[0].date,tradey.actions[0].date))
#>>> tz2 = sorted(trades1 + trades2,iftrade.DTSORT3)


def utrade_nc(sif,*fss):    #返回策略集合的独立运算的合并结果
    tradess = [utrade_n(sif,fs) for fs in fss]
    trades = reduce(lambda x,y:x+y,tradess)
    trades.sort(iftrade.DTSORT3)
    return trades

def utrade_ncp(sif,hmax,*fss):   
    '''
        返回策略集合的独立运算的仓位管理结果. 单个策略可在参数中出现多次以体现权重
        hmax是最大持仓数
    '''
    strades = utrade_nc(sif,*fss)
    cur_day = 0
    hcur = []
    rtrades = []
    for trade in strades:
        dopen,topen = trade.actions[0].date,trade.actions[0].time
        dclose,tclose = trade.actions[-1].date,trade.actions[-1].time
        if dopen > cur_day:
            cur_day = dopen
            hcur = [tclose] #清理掉前一日的
            rtrades.append(trade)
        elif len(hcur) < hmax:
            hcur.append(tclose)
            rtrades.append(trade)
        elif topen >= min(hcur):#等于其实不确定，暂定算
            pos = 0
            while(hcur[pos] > topen): #必然找到小于等于的.并且一般先开仓的先平，所以先找到概率大
                pos+=1
            del hcur[pos]   #减一个就够了
            hcur.append(tclose)
            rtrades.append(trade)
        else:#舍弃
            #print 'skip:',dopen,topen
            pass
    return rtrades

def utrade_ncp_n(hmax):
    def my_ncp(sif,*fss):
        return utrade_ncp(sif,hmax,*fss)
    return my_ncp

utrade_ncpx = utrade_ncp_n(2)   #等同于2张
utrade_ncp2 = utrade_ncp_n(2)
utrade_ncp3 = utrade_ncp_n(3)

def utrade_nct(sif,hmax,hmin,wds,*fss):   
    '''
        返回策略集合的独立运算的仓位管理结果. 单个策略可在参数中出现多次以体现权重
        hmax是有利日持仓数, hmin是不利日持仓数
        wds是有利日集合. 

        这个处理有个问题。即对当分钟开仓后平仓的，因为在topen与min(hcur)比较的时候没有处理到这种情况，
            所以如果下一笔交易也是该分钟的，就会突破仓位限制开出来
            但是如果采用topen>min(hcur)，又会漏掉当分钟反手的开仓那一笔.
        目前的处理只会加多止损，不会有利于回测。所以采用目前这种方式.
    '''
    strades = utrade_nc(sif,*fss)
    cur_day = 0
    hcur = []
    rtrades = []
    cur_max = 0
    for trade in strades:
        dopen,topen = trade.actions[0].date,trade.actions[0].time
        dclose,tclose = trade.actions[-1].date,trade.actions[-1].time
        if dopen > cur_day:
            cur_day = dopen
            cur_max = hmax if d2wd(cur_day) in wds else hmin
            if cur_max > 0:
                hcur = [tclose] #清理掉前一日的
                rtrades.append(trade)
            else:
                hcur = []
        elif len(hcur) < cur_max:
            hcur.append(tclose)
            rtrades.append(trade)
        elif hcur != [] and topen >= min(hcur):#在这里hcur==[]只有不利日持仓上限为0导致的. 
            #topen与min(hcur)的等于关系其实不确定，暂定算
            hcur = [c for c in hcur if c > topen]   #剔除所有前面平仓的
            hcur.append(tclose)
            rtrades.append(trade)
        else:#舍弃
            #print 'skip:',dopen,topen
            pass
    return rtrades

def utrade_nct_n(hmax,hmin,wds):
    def my_nct(sif,*fss):
        return utrade_nct(sif,hmax,hmin,wds,*fss)
    return my_nct

utrade_nctx = utrade_nct_n(2,1,(1,2,3,4,5)) #等同于不分日
utrade_nct12 = utrade_nct_n(2,1,(1,2))
utrade_nct125 = utrade_nct_n(2,1,(1,2,5))
utrade_nct1235 = utrade_nct_n(2,1,(1,2,3,5))
utrade_nct1245 = utrade_nct_n(2,1,(1,2,4,5))


###根据日内时间来确定仓位的办法
def utrade_ncd(sif,hmax,hmin,btime,*fss):   
    '''
        返回策略集合的独立运算的仓位管理结果. 单个策略可在参数中出现多次以体现权重
        hmax是前向持仓数，hmin为后向持仓数
        btime为区分前后向的时间界限，<=btime为前向，>btime为后向

        这个处理有个问题。即对当分钟开仓后平仓的，因为在topen与min(hcur)比较的时候没有处理到这种情况，
            所以如果下一笔交易也是该分钟的，就会突破仓位限制开出来
            但是如果采用topen>min(hcur)，又会漏掉当分钟反手的开仓那一笔.
        目前的处理只会加多止损，不会有利于回测。所以采用目前这种方式.
    '''
    strades = utrade_nc(sif,*fss)
    cur_day = 0
    hcur = []
    rtrades = []
    for trade in strades:
        dopen,topen = trade.actions[0].date,trade.actions[0].time
        dclose,tclose = trade.actions[-1].date,trade.actions[-1].time
        cur_max = hmax if topen <= btime else hmin
        if dopen > cur_day: #换日
            cur_day = dopen
            if cur_max > 0:
                hcur = [tclose] #清理掉前一日的
                rtrades.append(trade)
            else:
                hcur = []
        else:#当日延续
            hcur = [c for c in hcur if c > topen]   #剔除所有开仓前平仓的
            if len(hcur) < cur_max:
                hcur.append(tclose)
                rtrades.append(trade)
            else:#舍弃
                pass
    return rtrades

def utrade_ncd_n(hmax,hmin,btime):
    def my_ncd(sif,*fss):
        return utrade_ncd(sif,hmax,hmin,btime,*fss)
    return my_ncd

utrade_ncdx = utrade_ncd_n(2,1,1500) #等同于不分日
utrade_ncd1300 = utrade_ncd_n(2,1,1300)
utrade_ncd1315 = utrade_ncd_n(2,1,1315)
utrade_ncd1320 = utrade_ncd_n(2,1,1320)
utrade_ncd1325 = utrade_ncd_n(2,1,1325)
utrade_ncd1330 = utrade_ncd_n(2,1,1330)
utrade_ncd1345 = utrade_ncd_n(2,1,1345)
utrade_ncd1400 = utrade_ncd_n(2,1,1400)
utrade_ncd1415 = utrade_ncd_n(2,1,1415)
utrade_ncd1430 = utrade_ncd_n(2,1,1430)

####nct和ncd的组合
def utrade_ncdt(sif,hmax,hmin,wds,btime,*fss):   
    '''
        返回策略集合的独立运算的仓位管理结果. 单个策略可在参数中出现多次以体现权重
        hmax是有利日前向持仓数，hmin为不利日或后向持仓数
        wds是有利日集合.
        btime为区分前后向的时间界限，<=btime为前向，>btime为后向

        这个处理有个问题。即对当分钟开仓后平仓的，因为在topen与min(hcur)比较的时候没有处理到这种情况，
            所以如果下一笔交易也是该分钟的，就会突破仓位限制开出来
            但是如果采用topen>min(hcur)，又会漏掉当分钟反手的开仓那一笔.
        目前的处理只会加多止损，不会有利于回测。所以采用目前这种方式.
    '''
    strades = utrade_nc(sif,*fss)
    cur_day = 0
    hcur = []
    rtrades = []
    for trade in strades:
        dopen,topen = trade.actions[0].date,trade.actions[0].time
        dclose,tclose = trade.actions[-1].date,trade.actions[-1].time
        cur_max = hmax if d2wd(dopen) in wds and topen <= btime else hmin
        if dopen > cur_day: #换日
            cur_day = dopen
            if cur_max > 0:
                hcur = [tclose] #清理掉前一日的
                rtrades.append(trade)
            else:
                hcur = []
        else:#当日延续
            hcur = [c for c in hcur if c > topen]   #剔除所有开仓前平仓的
            if len(hcur) < cur_max:
                hcur.append(tclose)
                rtrades.append(trade)
            else:#舍弃
                pass
    return rtrades

def utrade_ncdt_n(hmax,hmin,wds,btime):
    def my_ncdt(sif,*fss):
        return utrade_ncdt(sif,hmax,hmin,wds,btime,*fss)
    return my_ncdt

utrade_ncdtx = utrade_ncdt_n(2,1,(1,2,3,4,5),1500) #等同于不分日
utrade_ncdt_1235_1330 = utrade_ncdt_n(2,1,(1,2,3,5),1330) # 貌似意义不大
utrade_ncdt_15_1330 = utrade_ncdt_n(2,1,(1,5),1330) # 貌似意义不大
utrade_ncdt_125_1330 = utrade_ncdt_n(2,1,(1,2,5),1330) # 貌似意义不大


def range_distribution(sif,rlimit = [300,500,800,1200,1500,10000]):#求振幅分布
    '''
>>> for range in ranges:
...     print range.begin,range.end,range.times
    '''
    srange = sif.highd - sif.lowd
    #srange = srange[-180:]
    results = [0]*len(rlimit)
    prelimit = 0
    i = 0
    for il in rlimit:
        results[i] = BaseObject(begin=prelimit,end=il,times=sum(gand(srange>prelimit,srange<il)))
        prelimit = il
        i += 1
    results.append(BaseObject(begin=0,end=il,times=len(srange)))
    return results

rd = range_distribution


#day_trades能获取dtrades
def profit_distribution(sif,dtrades,limit = [300,500,1000,1500,10000]):#求盈利分布
    mylimit = [l for l in limit]
    mylimit.append(999999)  #哨兵
    results = [BaseObject(end=il,wins=0,losts=0,pwins=0,plosts=0) for il in mylimit]
    for dtrade in dtrades:
        drange = sif.day2range[dtrade.day]
        id = 0
        while(drange > mylimit[id]): #必然会触及条件
            id+=1
        if dtrade.sprofit>0:
            results[id].wins += 1
            results[id].pwins += dtrade.sprofit
        elif dtrade.sprofit<=0:
            results[id].losts += 1
            results[id].plosts += dtrade.sprofit
    return results[:-1]

def profit_distribution2(sif,dtrades,limit = [0.6,1,1.5,4]):#求按照振幅/atr的盈利分布
    mylimit = [l for l in limit]
    mylimit.append(99999999)  #哨兵
    results = [BaseObject(end=il,wins=0,losts=0,pwins=0,plosts=0) for il in mylimit]
    for dtrade in dtrades:
        drange = sif.day2range_std[dtrade.day]
        id = 0
        while(drange > mylimit[id]): #必然会触及条件
            id+=1
        if dtrade.sprofit>0:
            results[id].wins += 1
            results[id].pwins += dtrade.sprofit
        elif dtrade.sprofit<=0:
            results[id].losts += 1
            results[id].plosts += dtrade.sprofit
    return results[:-1]

def profit_distribution3(sif,dtrades,limit = [0.01,0.02,0.03,0.04,0.05,0.1]):#求按照opend的盈利分布
    mylimit = [l for l in limit]
    mylimit.append(99999999)  #哨兵
    results = [BaseObject(end=il,wins=0,losts=0,pwins=0,plosts=0) for il in mylimit]
    for dtrade in dtrades:
        drange = sif.day2range[dtrade.day]
        dr = drange * 1.0 / sif.opend[sif.day2i[dtrade.day]]
        id = 0
        while(dr > mylimit[id]): #必然会触及条件
            id+=1
        if dtrade.sprofit>0:
            results[id].wins += 1
            results[id].pwins += dtrade.sprofit
        elif dtrade.sprofit<=0:
            results[id].losts += 1
            results[id].plosts += dtrade.sprofit
    return results[:-1]

pd = profit_distribution
pd2 = profit_distribution2
pd3 = profit_distribution3

def calc_profit(trades,av=200000,rate=0.9,lever=0.17,base=300,max_volume=80):#计算增量
    '''
        理论计算
        av:起点值
        rate:用于交易的资金比例
        lever:保证金比例
    '''
    s = av
    for trade in trades:
        price = trade.actions[0].price
        am = price * base / 10 * lever
        volume = int(s * rate / am)
        volume = volume - 1 if volume > 1 and volume < 20 else volume
        volume = volume if volume < max_volume else max_volume
        s = s + volume * trade.profit/10 * base
        #print price,am,volume,s
    return s

def calc_profit2(trades,av=200000,rate=0.97,lever=0.17,base=300,max_volume=80):#计算增量
    '''
        理论计算
        av:起点值
        rate:用于交易的资金比例
        lever:保证金比例
        区别:
        一旦手数增加，除非不足，不能下降
    '''
    s = av
    cur_volume = 1
    ff = open('d:/work/temp/dd.csv','w+')
    for trade in trades:
        price = trade.actions[0].price
        am = price * base / 10 * lever
        #volume = int(s * rate / am)
        volume0 = int(s/am)
        if volume0 < cur_volume:
            cur_volume = volume0
        else:
            volume = int(s * rate / am)
            volume = volume if volume < max_volume else max_volume
            if volume > cur_volume:
                cur_volume = volume
        s = s + cur_volume * trade.profit/10 * base
        print >> ff,'%s,%s,%s,%s,%s,%s' % (trade.actions[0].date,trade.profit,s,price,am,cur_volume)
    ff.close()
    return s

def calc_profit2d(trades,av=200000,rate=0.97,lever=0.17,base=300,max_volume=80):#计算增量
    '''
        理论计算
        av:起点值
        rate:用于交易的资金比例
        lever:保证金比例
        区别:
            每日计算一次
            0.97保证第二次开仓的时候手数还能不变
    '''
    s = av
    cur_volume = 1
    cur_date = 0
    for trade in trades:
        price = trade.actions[0].price
        am = price * base / 10 * lever
        #volume = int(s * rate / am)
        volume0 = int(s/am)
        if volume0 < cur_volume:
            cur_volume = volume0
        elif trade.actions[0].date != cur_date:
            cur_date = trade.actions[0].date
            volume = int(s * rate / am)
            volume = volume if volume < max_volume else max_volume
            if volume > cur_volume:
                cur_volume = volume
        s = s + cur_volume * trade.profit/10 * base
        #print cur_date,price,am,cur_volume,s
    return s

def calc_profitd(trades,av=200000,max_drawdown = 0.0215,max_ddrawdown = 0.0122,lever=0.17,base=300,max_volume=80):#计算增量
    '''
        理论计算
        av:起点值
        max_ddrawdown: 手数计算
        lever:保证金比例
         每日计算一次
    '''
    s = av
    cur_volume = 1
    cur_date = 0
    for trade in trades:
        price = trade.actions[0].price
        am = price * base / 10 * lever
        #volume = int(s * rate / am)
        volume0 = int(s/am)
        if volume0 < cur_volume:
            cur_volume = volume0
        elif trade.actions[0].date != cur_date:
            cur_date = trade.actions[0].date
            volume = int(s * rate / am)
            volume = volume if volume < max_volume else max_volume
            if volume > cur_volume:
                cur_volume = volume
        s = s + cur_volume * trade.profit/10 * base
        #print cur_date,price,am,cur_volume,s
    return s

def calc_amount_per_hand(cur_point,max_drawdown,max_ddrawdown,level,base):
    ''' 计算每手所需资金
    '''
    pass
    
    


def limit_lost(trades,maxlost=200): #请参见day_trades,有更完善版本
    #限定每日最大损失，超过改值后不再开仓
    cur_day = 0
    rtrades = []
    cur_lost = 0
    for trade in trades:
        dopen = trade.actions[0].date
        if dopen > cur_day: #换日
            cur_lost = 0
            cur_day = dopen
        if cur_lost <= -maxlost:
            continue
        cur_lost += trade.profit
        rtrades.append(trade)
    return rtrades

def limit_times(trades,maxtimes=3):
    #限定每日操作次数，超过此数(>=)就不再开仓
    cur_day = 0
    rtrades = []
    cur_times = 0
    for trade in trades:
        dopen = trade.actions[0].date
        if dopen > cur_day: #换日
            cur_times = 0
            cur_day = dopen
        if cur_times >= maxtimes:
            continue
        cur_times += 1
        rtrades.append(trade)
    return rtrades

def limit2(trades,maxlost=200,maxtimes=3):
    return limit_lost(limit_times(trades,maxtimes),maxlost)

