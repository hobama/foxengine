# -*- coding: utf-8 -*-

#完整的演示脚本

from wolfox.fengine.core.shortcut import *

import logging
logger = logging.getLogger('wolfox.fengine.normal.demo')    

def buy_func_demo1(stock):
    t = stock.transaction
    #g = stock.g60 >= 7500
    #g = gand(stock.g5 > stock.g20,stock.g20 > stock.g60,stock.g60 > stock.g120,stock.g120 > stock.g250)    
    #g对这个没效果
    cma_5 = d1e.ma(t[CLOSE],5)
    cma_22 = d1e.ma(t[CLOSE],22)
    cma_long = d1e.ma(t[CLOSE],60)
    c_5_22 = d1e.cross(cma_22,cma_5) > 0
    c_trend_22 = d1e.strend(cma_22) > 0
    c_trend_5 = d1e.strend(cma_5) > 0
    c_trend_long = d1e.strend(cma_long) > 0    
    #signal = gand(c_5_22,c_trend_22,c_trend_5)
    sbuy = gand(g,c_5_22,c_trend_22,c_trend_5,c_trend_long)
    return sbuy

def buy_func_demo2(stock,fast,mid,slow,extend_days = 10):
    logger.debug('calc: %s ' % stock.code)    
    t = stock.transaction
    #g = gand(stock.g5 > stock.g20,stock.g20 > stock.g60,stock.g60 > stock.g120,stock.g120 > stock.g250)    
    #g对这个没效果
    ma_fast = ma(t[CLOSE],fast)
    ma_mid = ma(t[CLOSE],mid)
    ma_slow = ma(t[CLOSE],slow)
    trend_fast = trend(ma_fast) > 0
    trend_mid = trend(ma_mid) > 0    
    trend_slow = trend(ma_slow) > 0
    cross_fast_mid = band(cross(ma_mid,ma_fast),trend_fast)
    cross_fast_slow = band(cross(ma_slow,ma_fast),trend_fast)
    cross_mid_slow = band(cross(ma_slow,ma_mid),trend_mid)
    cross_fm_fs = sfollow(cross_fast_mid,cross_fast_slow,extend_days)
    confirm_cross = sfollow(cross_fm_fs,cross_mid_slow,extend_days)
    trend_standard = trend(ma(t[CLOSE],55)) > 0
    return gand(g,trend_standard,confirm_cross)

def buy_func_demo3(stock,fast,slow,extend_days = 20):
    #print stock.code
    #logger.debug('calc: %s ' % stock.code)
    t = stock.transaction
    #print t[CLOSE]
    #return np.ones_like(t[CLOSE])
    #g = stock.g60 >= 8500    
    g = gand(stock.g5 > stock.g20,stock.g20 > stock.g60,stock.g60 > stock.g120,stock.g120 > stock.g250)
    #kao.存在没有c60也就是不归属任何catalog的stock，直接异常
    #signal_s = catalog_signal(stock.c60,8500,8500)  
    #print stock.code,max(stock.g60)
    svap,v2i = svap_ma(t[VOLUME],t[CLOSE],22)
    ma_svapfast = ma(svap,fast)
    ma_svapslow = ma(svap,slow)
    trend_ma_svapfast = trend(ma_svapfast) > 0
    trend_ma_svapslow = trend(ma_svapslow) > 0
    cross_fast_slow = gand(cross(ma_svapslow,ma_svapfast)>0,trend_ma_svapfast,trend_ma_svapslow)
    msvap = transform(cross_fast_slow,v2i,len(t[VOLUME]))
    maslow = ma(t[CLOSE],55)
    ma120 = ma(t[CLOSE],120)
    trend_ma120 = trend(ma120) > 0
    trend_20 = trend(stock.g20) > 0
    trend_60 = trend(stock.g60) > 0
    
    #sconfirm = upconfirm(t[OPEN],t[CLOSE],t[HIGH])
    #down_up = downup(maslow,t[CLOSE],10,3)
    #confirm_up = band(down_up,sconfirm)
    #confirmed_signal = syntony(msvap,confirm_up,15)
    #smmroc = swingin(t[HIGH],t[LOW],45,800)
    #return gand(confirmed_signal,trend_ma120,smmroc)
    #confirmed_signal起到反作用
    #return gand(g,confirmed_signal,trend_ma120)  #,signal_s)
    return gand(g,msvap,trend_ma120,trend_20,trend_60)

def buy_func_demo4(stock):
    #print stock.code
    #logger.debug('calc: %s ' % stock.code)
    t = stock.transaction
    #print t[CLOSE]
    #return np.ones_like(t[CLOSE])
    #g = stock.g60 >= 8500    
    g = gand(stock.g5 > stock.g20,stock.g20 > stock.g60,stock.g60 > stock.g120,stock.g120 > stock.g250)
    #kao.存在没有c60也就是不归属任何catalog的stock，直接异常
    #signal_s = catalog_signal(stock.c60,8500,8500)  
    #print stock.code,max(stock.g60)
    trend_20 = trend(stock.g20) > 0
    trend_60 = trend(stock.g60) > 0

    cross_fast_slow = gand(cross(stock.g60,stock.g20)>0,trend_20,trend_60)
    #sconfirm = upconfirm(t[OPEN],t[CLOSE],t[HIGH])
    #down_up = downup(maslow,t[CLOSE],10,3)
    #confirm_up = band(down_up,sconfirm)
    #confirmed_signal = syntony(msvap,confirm_up,15)
    #smmroc = swingin(t[HIGH],t[LOW],45,800)
    #return gand(confirmed_signal,trend_ma120,smmroc)
    #confirmed_signal起到反作用
    #return gand(g,confirmed_signal,trend_ma120)  #,signal_s)
    ma120 = ma(t[CLOSE],120)
    trend_ma120 = trend(ma120) > 0
    
    return gand(g,cross_fast_slow,trend_ma120)


def demo(dates,sdata,begin,end,idata=None):
    #print ctree
    #for s in ctree:
    #    print s.name
    #    for c in s.catalogs:
    #        print c.name

    #print 'catalog number:',len(catalogs)
    #print [ str(c.name) for c in catalogs]

    #for c in catalogs:
    #    print c.name
    #    for st in c.stocks:
    #        print st.code

    from time import time
    tbegin = time()

    demo2 = fcustom(buy_func_demo2,fast=4,mid=20,slow=75)
    demo3 = fcustom(buy_func_demo3,fast=5,slow=98)
    #pman = AdvancedPositionManager()
    pman = AdvancedATRPositionManager()
    dman = XDateManager(dates)

    myMediator=mediator_factory(trade_strategy=B1S1,pricer = oo_pricer)

    seller = atr_seller_factory(3000)
    #seller = csc_func
    config1 = BaseObject(buyer = buy_func_demo1,seller=seller,pman=pman,dman=dman)    
    config2 = BaseObject(buyer = demo2,seller=seller,pman=pman,dman=dman)    
    config3 = BaseObject(buyer = demo3,seller=seller,pman=pman,dman=dman)
    config4 = BaseObject(buyer = buy_func_demo4,seller=seller,pman=pman,dman=dman)    
    #configs = [config1,config2,config3]
    configs = [config3]
    #configs = [config1,config2]
    batch(configs,sdata,dates,begin,cmediator=myMediator)

    tend = time()
    print u'耗时: %s' % (tend-tbegin)
    logger.debug(u'耗时: %s' % (tend-tbegin))    

    save_configs('demo_ev.txt',configs,begin,end)
    


if __name__ == '__main__':
    logging.basicConfig(filename="demo.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    
    #sdata = cs.get_stocks(['SH600503'],begin,end,ref_id)
    #sdata = cs.get_stocks(['SZ000655'],begin,end,ref_id)
    #print sdata[442].transaction[CLOSE]
    #sdata = cs.get_stocks(['SH600000'],begin,end,ref_id)
    begin = 20010701
    end = 20050701
    from time import time
    tbegin = time()
    
    dates,sdata,idata,catalogs = prepare_all(begin,end,[],[ref_code])
    tend = time()
    print u'数据准备耗时: %s' % (tend-tbegin)
    
    #dates,sdata,idata,catalogs = prepare_all(begin,end,['SH600000'],[ref_code])
    d_posort('g5',sdata.values(),distance=5)        
    d_posort('g20',sdata.values(),distance=20)    
    d_posort('g120',sdata.values(),distance=120)     
    d_posort('g250',sdata.values(),distance=250)     
    demo(dates,sdata,begin,end)

