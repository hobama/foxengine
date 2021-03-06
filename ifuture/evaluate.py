# -*- coding: utf-8 -*-

'''
    方法测试与研究的工具
'''

from wolfox.fengine.ifuture.ibase import *

def evaluate(sif
             ,signal    #信号序列
             ,interval  #信号之后的价格间隔
             ,end = 1500    #信号过滤
             ,begin = 929   #信号过滤
             ,uplimit = 90  #分割统计的上限
             ,downlimit = 90    #分割统计的下限
             ,filter = None  #过滤器
             ):
    '''
        对开仓后10分钟内的上下情况进行统计，无所谓买入或卖出，仅统计上下
    '''
    if filter != None:
        signal = gand(signal,filter)
    ssignal = np.select([gand(sif.time>begin,sif.time<end)],[rollx(signal)],0)  #信号在下一周期开始发出
    indics = np.nonzero(ssignal)
    s1open = sif.close[indics]  #不可能马上买入,最快在信号发出的分钟末买入
    s2close = rollx(sif.close,-interval)[indics]
    #+1以包括开仓那一分钟,计如果次分钟平仓，即interval=1,则实际上也涉及到了2个分钟，即开仓分钟和平仓分钟
    s0high = rollx(tmax(sif.high,interval+1),-interval)[indics] 
    s0low = rollx(tmin(sif.low,interval+1),-interval)[indics]
    profits = s2close - s1open
    up_wave = s0high-s1open
    down_wave = s1open-s0low
    wtimes = np.sum(profits>0)
    ltimes = np.sum(profits<=0)
    xavg = np.sum(profits) / len(profits)
    wavg = np.sum(profits[profits>0]) / wtimes
    lavg = np.sum(profits[profits<=0]) / ltimes  
    nu = np.sum(up_wave > uplimit)
    nd = np.sum(down_wave > downlimit)
    mu = 0 if len(up_wave) ==0 else np.max(up_wave)
    md = 0 if len(down_wave) ==0 else np.max(down_wave)
    pinfo = []
    pinfo.append((-downlimit,np.sum(profits<-downlimit)))
    for step in range(-downlimit,uplimit,10):
        sn = np.sum(gand(profits>step,profits<=step+10))
        pinfo.append((step,sn))
    pinfo.append((uplimit,np.sum(profits>uplimit)))

    return (xavg,wavg,lavg,wtimes,ltimes),(nu,nd,mu,md)#,(pinfo,)#,(profits,up_wave,down_wave)

def evaluate2_b(sif
             ,signal    #信号序列
             ,interval  #信号之后的价格间隔
             ,end = 1500    #信号过滤
             ,begin = 929   #信号过滤
             ,downlimit = 60    #止损
             ,uplimit = 90  #分类统计的上限
             ,filter = None #过滤器
             ):
    ''' 
        对买入开仓后超过下限的进行止损平仓
    '''
    if filter != None:
        signal = gand(signal,filter)
    ssignal = np.select([gand(sif.time>begin,sif.time<end)],[rollx(signal)],0)  #信号在下一周期开始发出
    indics = np.nonzero(ssignal)
    s1open = sif.close[indics]  #不可能马上买入,最快在信号发出的分钟末买入
    s2close = rollx(sif.close,-interval)[indics]
    #+1以包括开仓那一分钟,计如果次分钟平仓，即interval=1,则实际上也涉及到了2个分钟，即开仓分钟和平仓分钟
    s0high = rollx(tmax(sif.high,interval+1),-interval)[indics] 
    s0low = rollx(tmin(sif.low,interval+1),-interval)[indics]
    profits = s2close - s1open
    up_wave = s0high-s1open
    down_wave = s1open-s0low
    profits = np.select([down_wave<downlimit],[profits],-downlimit-5)   #取一半的滑点
    wtimes = np.sum(profits>0)
    ltimes = np.sum(profits<=0)
    xavg = np.sum(profits) / len(profits)
    wavg = np.sum(profits[profits>0]) / wtimes
    lavg = np.sum(profits[profits<=0]) / ltimes  
    nu = np.sum(up_wave > uplimit)
    nd = np.sum(down_wave > downlimit)
    mu = 0 if len(up_wave) ==0 else np.max(up_wave)
    md = 0 if len(down_wave) ==0 else np.max(down_wave)
    pinfo = []
    pinfo.append((-downlimit,np.sum(profits<-downlimit)))
    for step in range(-downlimit,uplimit,10):
        sn = np.sum(gand(profits>step,profits<=step+10))
        pinfo.append((step,sn))
    pinfo.append((uplimit,np.sum(profits>uplimit)))

    return (xavg,wavg,lavg,wtimes,ltimes),(nu,-nd,mu,-md),(pinfo,)#,(profits,up_wave,down_wave)

def evaluate2_s(sif
             ,signal    #信号序列
             ,interval  #信号之后的价格间隔
             ,end = 1500    #信号过滤
             ,begin = 929   #信号过滤
             ,downlimit = 90    #分类统计的上限
             ,uplimit = 60      #止损
             ,filter = None #过滤器
             ):
    ''' 
        对卖出开仓后超过上限的进行止损平仓
    '''
    if filter != None:
        signal = gand(signal,filter)
    ssignal = np.select([gand(sif.time>begin,sif.time<end)],[rollx(signal)],0)  #信号在下一周期开始发出
    indics = np.nonzero(ssignal)
    s1open = sif.close[indics]  #不可能马上买入,最快在信号发出的分钟末买入
    s2close = rollx(sif.close,-interval)[indics]
    #+1以包括开仓那一分钟,计如果次分钟平仓，即interval=1,则实际上也涉及到了2个分钟，即开仓分钟和平仓分钟
    s0high = rollx(tmax(sif.high,interval+1),-interval)[indics] 
    s0low = rollx(tmin(sif.low,interval+1),-interval)[indics]
    profits = s1open - s2close  #空头利润
    up_wave = s0high-s1open
    down_wave = s1open-s0low
    profits = np.select([up_wave<uplimit],[profits],-uplimit-5)   #取一半的滑点
    wtimes = np.sum(profits>0)
    ltimes = np.sum(profits<=0)
    xavg = np.sum(profits) / len(profits)
    wavg = np.sum(profits[profits>0]) / wtimes
    lavg = np.sum(profits[profits<=0]) / ltimes  
    nu = np.sum(up_wave > uplimit)
    nd = np.sum(down_wave > downlimit)
    mu = 0 if len(up_wave) ==0 else np.max(up_wave)
    md = 0 if len(down_wave) ==0 else np.max(down_wave)
    pinfo = []
    pinfo.append((-uplimit,np.sum(profits<-uplimit)))
    for step in range(-uplimit,downlimit,10):
        sn = np.sum(gand(profits>step,profits<=step+10))
        pinfo.append((step,sn))
    pinfo.append((downlimit,np.sum(profits>downlimit)))

    return (xavg,wavg,lavg,wtimes,ltimes),(-nu,nd,-mu,md),(pinfo,)#,(profits,up_wave,down_wave)

def evaluate3_b(sif
             ,signal    #信号序列
             ,interval  #信号之后的价格间隔
             ,end = 1500    #信号过滤
             ,begin = 929   #信号过滤
             ,downlimit = 60    #止损
             ,uplimit = 90  #分类统计的上限
             ,filter = None #过滤器
             ):
    ''' 
        对买入开仓后超过下限的进行止损平仓
        并抑制未平仓前的继续开仓，以避免一次上升被计入多次，最后导致数据与实际操作不符的问题
    '''
    if filter != None:
        signal = gand(signal,filter)
    ssignal = np.select([gand(sif.time>begin,sif.time<end)],[rollx(signal)],0)  #信号在下一周期开始发出
    indics = np.nonzero(ssignal)
    
    occupy = np.zeros_like(sif.close)
    slength = len(sif.close)    
    for index in indics[0]:
        if occupy[index] != 0:
            ssignal[index] = 0
            continue    #被忽略
        cindex = index + interval if index+interval<slength else slength
        cdownl = sif.close[index] - downlimit
        for si in range(index,cindex):
            occupy[si] = 1
            if sif.low[si] < cdownl:
                break
    indics = np.nonzero(ssignal)
    
    s1open = sif.close[indics]  #不可能马上买入,最快在信号发出的分钟末买入
    s2close = rollx(sif.close,-interval)[indics]
    #+1以包括开仓那一分钟,计如果次分钟平仓，即interval=1,则实际上也涉及到了2个分钟，即开仓分钟和平仓分钟
    s0high = rollx(tmax(sif.high,interval+1),-interval)[indics] 
    s0low = rollx(tmin(sif.low,interval+1),-interval)[indics]

    profits = s2close - s1open
    up_wave = s0high-s1open
    down_wave = s1open-s0low
    profits = np.select([down_wave<downlimit],[profits],-downlimit-5)   #取一半的滑点
    wtimes = np.sum(profits>0)
    ltimes = np.sum(profits<=0)
    xavg = np.sum(profits) / len(profits)
    wavg = np.sum(profits[profits>0]) / wtimes
    lavg = np.sum(profits[profits<=0]) / ltimes  
    nu = np.sum(up_wave > uplimit)
    nd = np.sum(down_wave > downlimit)
    mu = 0 if len(up_wave) ==0 else np.max(up_wave)
    md = 0 if len(down_wave) ==0 else np.max(down_wave)
    pinfo = []
    pinfo.append((-downlimit,np.sum(profits<-downlimit)))
    for step in range(-downlimit,uplimit,10):
        sn = np.sum(gand(profits>step,profits<=step+10))
        pinfo.append((step,sn))
    pinfo.append((uplimit,np.sum(profits>uplimit)))

    return (xavg,wavg,lavg,wtimes,ltimes),(nu,-nd,mu,-md),(pinfo,)#,(profits,up_wave,down_wave)

def evaluate3_s(sif
             ,signal    #信号序列
             ,interval  #信号之后的价格间隔
             ,end = 1500    #信号过滤
             ,begin = 929   #信号过滤
             ,downlimit = 90    #分类统计的上限
             ,uplimit = 60      #止损
             ,filter = None #过滤器
             ):
    ''' 
        对卖出开仓后超过上限的进行止损平仓
    '''
    if filter != None:
        signal = gand(signal,filter)
    ssignal = np.select([gand(sif.time>begin,sif.time<end)],[rollx(signal)],0)  #信号在下一周期开始发出
    indics = np.nonzero(ssignal)

    occupy = np.zeros_like(sif.close)
    slength = len(sif.close)    
    for index in indics[0]:
        if occupy[index] != 0:
            ssignal[index] = 0
            continue    #被忽略
        cindex = index + interval if index+interval<slength else slength
        cupl = sif.close[index] + uplimit
        for si in range(index,cindex):
            occupy[si] = 1
            if sif.high[si] > cupl:
                break
    indics = np.nonzero(ssignal)

    s1open = sif.close[indics]  #不可能马上买入,最快在信号发出的分钟末买入
    s2close = rollx(sif.close,-interval)[indics]
    #+1以包括开仓那一分钟,计如果次分钟平仓，即interval=1,则实际上也涉及到了2个分钟，即开仓分钟和平仓分钟
    s0high = rollx(tmax(sif.high,interval+1),-interval)[indics] 
    s0low = rollx(tmin(sif.low,interval+1),-interval)[indics]
    profits = s1open - s2close  #空头利润
    up_wave = s0high-s1open
    down_wave = s1open-s0low
    profits = np.select([up_wave<uplimit],[profits],-uplimit-5)   #取一半的滑点
    wtimes = np.sum(profits>0)
    ltimes = np.sum(profits<=0)
    xavg = np.sum(profits) / len(profits)
    wavg = np.sum(profits[profits>0]) / wtimes
    lavg = np.sum(profits[profits<=0]) / ltimes  
    nu = np.sum(up_wave > uplimit)
    nd = np.sum(down_wave > downlimit)
    mu = 0 if len(up_wave) ==0 else np.max(up_wave)
    md = 0 if len(down_wave) ==0 else np.max(down_wave)
    pinfo = []
    pinfo.append((-uplimit,np.sum(profits<-uplimit)))
    for step in range(-uplimit,downlimit,10):
        sn = np.sum(gand(profits>step,profits<=step+10))
        pinfo.append((step,sn))
    pinfo.append((downlimit,np.sum(profits>downlimit)))

    return (xavg,wavg,lavg,wtimes,ltimes),(-nu,nd,-mu,md),(pinfo,)#,(profits,up_wave,down_wave)




test_funcs = []
def add_funcs(tests,suffix):
    test_funcs.extend([(key,value) for key,value in globals().items() if key[:len(suffix)] == suffix])


'''
>>> import wolfox.fengine.ifuture.evaluate as ev
>>> evf = fcustom(ev.evaluate,interval=60,begin=944,end=1444)
>>> results = ev.ev_tests(i00,evf,ev.test_funcs)
>>> ev.ev_output(results,'d:/temp/ev_test.txt',evf)

>>> evf_b = fcustom(ev.evaluate2_b,interval=60,begin=944,end=1414,downlimit=90)
>>> evf_s = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90)
>>> results_b = ev.ev_tests(i00,evf_b,ev.test_funcs)
>>> results_s = ev.ev_tests(i00,evf_s,ev.test_funcs)
>>> ev.ev_output(results_b,'d:/temp/evb_test.txt',evf)
>>> ev.ev_output(results_s,'d:/temp/evs_test.txt',evf)
>>> evf_b120 = fcustom(ev.evaluate2_b,interval=120,begin=944,end=1314,downlimit=90)
>>> evf_s120 = fcustom(ev.evaluate2_s,interval=120,begin=944,end=1314,uplimit=90)
####120不如60
>>> results_b120 = ev.ev_tests(i00,evf_b120,ev.test_funcs)
>>> results_s120 = ev.ev_tests(i00,evf_s120,ev.test_funcs)
>>> ev.ev_output(results_b120,'d:/temp/evb120_test.txt',evf)
>>> ev.ev_output(results_s120,'d:/temp/evs120_test.txt',evf)
>>> ufilter = strend2(i00.ma30)>0
>>> dfilter = strend2(i00.ma30)<0
>>> evf_b_s30 = fcustom(ev.evaluate2_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter)
>>> evf_s_s30 = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter)
>>> results_b_s30 = ev.ev_tests(i00,evf_b_s30,ev.test_funcs)
>>> results_s_s30 = ev.ev_tests(i00,evf_s_s30,ev.test_funcs)
>>> ev.ev_output(results_b_s30,'d:/temp/evb_s30_test.txt',evf)
>>> ev.ev_output(results_s_s30,'d:/temp/evs_s30_test.txt',evf)

###发现13可以，60不行
>>> ufilter13 = strend2(i00.ma13)>0
>>> dfilter13 = strend2(i00.ma13)<0
>>> dfilter60 = strend2(i00.ma60)<0
>>> ufilter60 = strend2(i00.ma60)>0
>>> evf_s_s13 = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter13)
>>> evf_s_s60 = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90
>>> evf_b_s13 = fcustom(ev.evaluate2_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter13)
>>> evf_b_s60 = fcustom(ev.evaluate2_b,interval=60,begin=944,end=1414,downlimit=
>>> results_s_s13 = ev.ev_tests(i00,evf_s_s13,ev.test_funcs)
>>> results_s_s30 = ev.ev_tests(i00,evf_s_s30,ev.test_funcs)
>>> results_s_s60 = ev.ev_tests(i00,evf_s_s60,ev.test_funcs)
>>> results_b_s60 = ev.ev_tests(i00,evf_b_s60,ev.test_funcs)
>>> results_b_s13 = ev.ev_tests(i00,evf_b_s13,ev.test_funcs)
>>> ev.ev_output(results_b_s13,'d:/temp/evb_s13_test.txt',evf)
>>> ev.ev_output(results_b_s60,'d:/temp/evb_s60_test.txt',evf)
>>> ev.ev_output(results_s_s60,'d:/temp/evs_s60_test.txt',evf)
>>> ev.ev_output(results_s_s13,'d:/temp/evs_s13_test.txt',evf)

>>> ufilter13_30 = gand(strend2(i00.ma13)>0,strend2(i00.ma30)>0)
>>> dfilter13_30 = gand(strend2(i00.ma13)<0,strend2(i00.ma30)<0)
>>> evf_s_s13_30 = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter13_30)
>>> evf_b_s13_30 = fcustom(ev.evaluate2_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter13_30)
>>> results_s_s13_30 = ev.ev_tests(i00,evf_s_s13_30,ev.test_funcs)
>>> results_b_s13_30 = ev.ev_tests(i00,evf_b_s13_30,ev.test_funcs)
>>> ev.ev_output(results_b_s13_30,'d:/temp/evb_b13_30_test.txt',evf)
>>> ev.ev_output(results_s_s13_30,'d:/temp/evs_s13_30_test.txt',evf)

##多: 13_30略优于13/30
##空: 13_30不如13
##总体来说使用13,但对于大幅度筛选的，使用13-30


#采用evaluate3_b/s,以与实际更贴近
evf_b = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90)
evf_s = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90)
results_b = ev.ev_tests(i00,evf_b,ev.test_funcs)
results_s = ev.ev_tests(i00,evf_s,ev.test_funcs)
ev.ev_output(results_b,'d:/temp/evb_test.txt',evf_b)
ev.ev_output(results_s,'d:/temp/evs_test.txt',evf_s)
evf_b120 = fcustom(ev.evaluate3_b,interval=120,begin=944,end=1314,downlimit=90)
evf_s120 = fcustom(ev.evaluate3_s,interval=120,begin=944,end=1314,uplimit=90)
####120不如60
results_b120 = ev.ev_tests(i00,evf_b120,ev.test_funcs)
results_s120 = ev.ev_tests(i00,evf_s120,ev.test_funcs)
ev.ev_output(results_b120,'d:/temp/evb120_test.txt',evf_b120)
ev.ev_output(results_s120,'d:/temp/evs120_test.txt',evf_s120)
ufilter = strend2(i00.ma30)>0
dfilter = strend2(i00.ma30)<0
evf_b_s30 = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter)
evf_s_s30 = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter)
results_b_s30 = ev.ev_tests(i00,evf_b_s30,ev.test_funcs)
results_s_s30 = ev.ev_tests(i00,evf_s_s30,ev.test_funcs)
ev.ev_output(results_b_s30,'d:/temp/evb_s30_test.txt',evf_b_s30)
ev.ev_output(results_s_s30,'d:/temp/evs_s30_test.txt',evf_s_s30)

###发现13可以，60不行
ufilter13 = strend2(i00.ma13)>0
dfilter13 = strend2(i00.ma13)<0
dfilter60 = strend2(i00.ma60)<0
ufilter60 = strend2(i00.ma60)>0
evf_s_s13 = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter13)
evf_s_s60 = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter60)
evf_b_s13 = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter13)
evf_b_s60 = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter60)
results_s_s13 = ev.ev_tests(i00,evf_s_s13,ev.test_funcs)
results_s_s30 = ev.ev_tests(i00,evf_s_s30,ev.test_funcs)
results_s_s60 = ev.ev_tests(i00,evf_s_s60,ev.test_funcs)
results_b_s60 = ev.ev_tests(i00,evf_b_s60,ev.test_funcs)
results_b_s13 = ev.ev_tests(i00,evf_b_s13,ev.test_funcs)
ev.ev_output(results_b_s13,'d:/temp/evb_s13_test.txt',evf_b_s13)
ev.ev_output(results_b_s60,'d:/temp/evb_s60_test.txt',evf_b_s60)
ev.ev_output(results_s_s60,'d:/temp/evs_s60_test.txt',evf_s_s60)
ev.ev_output(results_s_s13,'d:/temp/evs_s13_test.txt',evf_s_s13)

ufilter13_30 = gand(strend2(i00.ma13)>0,strend2(i00.ma30)>0)
dfilter13_30 = gand(strend2(i00.ma13)<0,strend2(i00.ma30)<0)
evf_s_s13_30 = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90,filter=dfilter13_30)
evf_b_s13_30 = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter13_30)
results_s_s13_30 = ev.ev_tests(i00,evf_s_s13_30,ev.test_funcs)
results_b_s13_30 = ev.ev_tests(i00,evf_b_s13_30,ev.test_funcs)
ev.ev_output(results_b_s13_30,'d:/temp/evb_b13_30_test.txt',evf_b_s13_30)
ev.ev_output(results_s_s13_30,'d:/temp/evs_s13_30_test.txt',evf_s_s13_30)


'''
def ev_tests(sif,efunc,tests):
    #for name,tfunc in tests:
    #    print name
    #    signal=tfunc(sif)
    return [ (name,efunc(sif,signal=tfunc(sif))) for name,tfunc in tests]

def ev_output(results,filename,tfunc):
    results = sorted(results,lambda x,y:int(y[1][0][0]-x[1][0][0])) #逆序
    outf = open(filename,'wt+')
    print >>outf,'%s:%s\n' % (func_name(tfunc),tfunc.paras)
    for name,result in results:
        print >>outf,name,result
    outf.close()


xx_up = lambda sfast,sslow:gand(cross(sslow,sfast)>0,strend2(sfast)>0)
xx_down = lambda sfast,sslow:gand(cross(sslow,sfast)<0,strend2(sfast)<0)

xx_bottom = lambda sfast,sslow,length=2:gand(strend2(sfast-sslow)==length,sfast<sslow,strend2(sfast)>0)
xx_top = lambda sfast,sslow,length=2:gand(strend2(sfast-sslow)==-length,sfast>sslow,strend2(sfast)<0)

def sxnative(sclose,sfast,sslow,sindics,sfunc=xx_up):
    sx = sfunc(sfast,sslow)
    signal = np.zeros_like(sclose)
    signal[sindics] = sx
    return signal


'''
发现 
买入:短周期macd基本是反效果，10分钟以上长周期比较好
卖出:5分钟下叉

#10分钟上叉，成功率很小，但成功的上涨幅度很不错
>>> ev.evaluate2_b(i00,ev.sxmacd10_b(i00),120,downlimit=90,end=1315,begin=944)  #成功率太少
((71, 561, -92, 10, 30), (25, -28, 900, -764), ([(-90, 28), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 2), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (1
0, 0), (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 10)],
))
>>> ev.evaluate2_b(i00,ev.sxmacd10_b(i00),120,downlimit=60,end=1315,begin=945)
((75, 639, -65, 8, 32), (25, -32, 900, -764), ([(-60, 32), (-60, 0), (-50, 0), (
-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (30, 0), (40, 0
), (50, 0), (60, 0), (70, 0), (80, 0), (90, 8)],))


>>> ev.evaluate2_b(i00,ev.sxmacd15_b(i00),120,downlimit=90,end=1315,begin=1000) 
((62, 454, -91, 7, 18), (16, -17, 892, -856), ([(-90, 17), (-90, 0), (-80, 0), (
-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (10
, 0), (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 7)],))


##头45分钟的15分钟上叉交易不行
>>> ev.evaluate2_b(i00,ev.sxmacd15_b(i00),60,downlimit=80,end=1414,begin=1000)  ####
((56, 328, -85, 12, 23), (18, -22, 856, -852), ([(-80, 23), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (2
, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 12)],))

>>> ev.evaluate2_b(i00,ev.sxmacd30_b(i00),120,downlimit=90,end=1314,begin=1000) ####
((118, 301, -95, 7, 6), (9, -6, 716, -658), ([(-90, 6), (-90, 0), (-80, 0), (-70
, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1
), (20, 0), (30, 0), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 5)],))

>>> ev.evaluate2_b(i00,ev.sxmacd30_b(i00),60,downlimit=90,end=1414,begin=1000)  ####
((54, 224, -93, 13, 15), (17, -14, 610, -424), ([(-90, 14), (-90, 0), (-80, 0),
(-70, 1), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (1
0, 0), (20, 0), (30, 0), (40, 0), (50, 1), (60, 0), (70, 0), (80, 1), (90, 11)],


#卖出
>>> ev.evaluate2_s(i00,ev.sxmacd5_s(i00),120,uplimit=90,begin=945,end=1314) #####
((53, 260, -92, 41, 59), (-54, 74, -1272, 1422), ([(-90, 56), (-90, 0), (-80, 0)
, (-70, 0), (-60, 0), (-50, 0), (-40, 2), (-30, 0), (-20, 0), (-10, 1), (0, 1),
(10, 2), (20, 2), (30, 2), (40, 2), (50, 1), (60, 0), (70, 0), (80, 0), (90, 31)
],))

#准确率太低
>>> ev.evaluate2_s(i00,ev.sxmacd3_s(i00),120,uplimit=80,begin=945,end=1314)
((35, 255, -84, 57, 106), (-102, 118, -1114, 1428), ([(-80, 103), (-80, 0), (-70
, 0), (-60, 0), (-50, 0), (-40, 1), (-30, 1), (-20, 1), (-10, 0), (0, 3), (10, 2
), (20, 2), (30, 3), (40, 0), (50, 2), (60, 2), (70, 0), (80, 1), (90, 42)],))

#准确率太低
>>> ev.evaluate2_s(i00,ev.sxmacd1_s(i00),120,uplimit=80,begin=945,end=1314)
((30, 277, -83, 151, 329), (-315, 345, -1250, 1510), ([(-80, 319), (-80, 0), (-7
0, 0), (-60, 0), (-50, 1), (-40, 1), (-30, 0), (-20, 6), (-10, 2), (0, 4), (10,
1), (20, 5), (30, 5), (40, 5), (50, 2), (60, 6), (70, 7), (80, 6), (90, 110)],))

>>> ev.evaluate2_s(i00,ev.sxmacd3_s(i00),60,uplimit=80,begin=945,end=1414)
((22, 166, -81, 104, 145), (-133, 138, -766, 850), ([(-80, 133), (-80, 1), (-70,
 0), (-60, 0), (-50, 1), (-40, 4), (-30, 1), (-20, 2), (-10, 3), (0, 3), (10, 1)
, (20, 5), (30, 4), (40, 4), (50, 5), (60, 2), (70, 5), (80, 4), (90, 71)],))

>>> ev.evaluate2_s(i00,ev.sxmacd15_s(i00),60,uplimit=80,begin=945,end=1414)
((35, 169, -81, 19, 22), (-20, 27, -910, 664), ([(-80, 20), (-80, 0), (-70, 0),
(-60, 1), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 1), (10, 2), (20
, 0), (30, 0), (40, 1), (50, 0), (60, 1), (70, 0), (80, 0), (90, 14)],))
>>> ev.evaluate2_s(i00,ev.sxmacd15_s(i00),120,uplimit=80,begin=945,end=1314)
((23, 230, -80, 10, 20), (-18, 20, -1170, 1004), ([(-80, 18), (-80, 0), (-70, 0)
, (-60, 0), (-50, 0), (-40, 1), (-30, 1), (-20, 0), (-10, 0), (0, 1), (10, 2), (
20, 0), (30, 1), (40, 0), (50, 0), (60, 1), (70, 0), (80, 1), (90, 4)],))
>>> ev.evaluate2_s(i00,ev.sxmacd15_s(i00),60,uplimit=80,begin=1000,end=1414)        ####
((39, 172, -80, 18, 20), (-18, 26, -910, 664), ([(-80, 18), (-80, 0), (-70, 0),
(-60, 1), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 1), (10, 2), (20
, 0), (30, 0), (40, 1), (50, 0), (60, 1), (70, 0), (80, 0), (90, 13)],))



#之前都没有添加strend2(sif.ma30)条件


>>> ev.evaluate(i00,ev.sxmacd1_b(i00),10)
((-10, 52, -61, 447, 547), (147, 212, 462, 512), ([(-90, 120), (-90, 19), (-80,
29), (-70, 24), (-60, 54), (-50, 48), (-40, 50), (-30, 68), (-20, 53), (-10, 75)
, (0, 73), (10, 61), (20, 64), (30, 49), (40, 39), (50, 33), (60, 26), (70, 19),
 (80, 19), (90, 64)],))
>>> ev.evaluate(i00,ev.sxmacd1_s(i00),10)
((2, 62, -57, 487, 502), (207, 178, 566, 414), ([(-90, 97), (-90, 20), (-80, 26)
, (-70, 32), (-60, 31), (-50, 49), (-40, 43), (-30, 68), (-20, 60), (-10, 70), (
0, 65), (10, 59), (20, 39), (30, 53), (40, 55), (50, 37), (60, 29), (70, 23), (8
0, 24), (90, 103)],))
>>> ev.evaluate(i00,ev.sxmacd3_b(i00),10)
((-8, 50, -59, 155, 172), (40, 59, 482, 354), ([(-90, 37), (-90, 5), (-80, 9), (
-70, 9), (-60, 13), (-50, 12), (-40, 19), (-30, 22), (-20, 20), (-10, 24), (0, 2
7), (10, 26), (20, 25), (30, 20), (40, 9), (50, 11), (60, 7), (70, 6), (80, 1),
(90, 23)],))
>>> ev.evaluate(i00,ev.sxmacd3_s(i00),10)
((4, 55, -53, 184, 162), (69, 51, 416, 482), ([(-90, 23), (-90, 5), (-80, 11), (
-70, 12), (-60, 17), (-50, 13), (-40, 23), (-30, 18), (-20, 19), (-10, 18), (0,
29), (10, 20), (20, 21), (30, 23), (40, 17), (50, 14), (60, 10), (70, 10), (80,
12), (90, 28)],))
>>> ev.evaluate(i00,ev.sxmacd5_b(i00),10)
((-10, 60, -59, 75, 108), (27, 34, 520, 332), ([(-90, 20), (-90, 3), (-80, 8), (
-70, 7), (-60, 8), (-50, 11), (-40, 12), (-30, 12), (-20, 14), (-10, 12), (0, 9)
, (10, 12), (20, 13), (30, 7), (40, 7), (50, 5), (60, 3), (70, 1), (80, 5), (90,
 13)],))
>>> ev.evaluate(i00,ev.sxmacd5_s(i00),10)
((-9, 54, -56, 85, 111), (27, 40, 328, 358), ([(-90, 23), (-90, 4), (-80, 5), (-
70, 4), (-60, 10), (-50, 5), (-40, 9), (-30, 13), (-20, 19), (-10, 18), (0, 16),
 (10, 9), (20, 15), (30, 10), (40, 6), (50, 8), (60, 3), (70, 2), (80, 1), (90,
15)],))
>>> ev.evaluate(i00,ev.sxmacd10_b(i00),10)
((-3, 86, -56, 32, 54), (19, 18, 310, 366), ([(-90, 11), (-90, 1), (-80, 2), (-7
0, 2), (-60, 5), (-50, 3), (-40, 7), (-30, 7), (-20, 6), (-10, 9), (0, 4), (10,
4), (20, 4), (30, 0), (40, 1), (50, 2), (60, 2), (70, 1), (80, 4), (90, 10)],))
>>> ev.evaluate(i00,ev.sxmacd10_s(i00),10)
((-5, 54, -65, 46, 45), (14, 24, 406, 310), ([(-90, 11), (-90, 3), (-80, 1), (-7
0, 2), (-60, 3), (-50, 3), (-40, 3), (-30, 8), (-20, 3), (-10, 7), (0, 6), (10,
7), (20, 3), (30, 8), (40, 6), (50, 2), (60, 5), (70, 3), (80, 0), (90, 6)],))
>>> ev.evaluate(i00,ev.sxmacd15_b(i00),10)
((8, 97, -57, 26, 36), (13, 10, 376, 366), ([(-90, 7), (-90, 1), (-80, 3), (-70,
 1), (-60, 1), (-50, 3), (-40, 9), (-30, 3), (-20, 3), (-10, 5), (0, 2), (10, 2)
, (20, 1), (30, 4), (40, 1), (50, 1), (60, 5), (70, 0), (80, 1), (90, 9)],))
>>> ev.evaluate(i00,ev.sxmacd15_s(i00),10)
((-4, 54, -61, 29, 30), (7, 12, 380, 346), ([(-90, 8), (-90, 0), (-80, 0), (-70,
 1), (-60, 2), (-50, 4), (-40, 2), (-30, 4), (-20, 4), (-10, 5), (0, 5), (10, 3)
, (20, 3), (30, 3), (40, 1), (50, 3), (60, 5), (70, 1), (80, 2), (90, 3)],))
>>> ev.evaluate(i00,ev.sxmacd30_b(i00),10,end=1444,begin=945)
((8, 105, -46, 10, 18), (7, 3, 466, 142), ([(-90, 1), (-90, 2), (-80, 0), (-70,
1), (-60, 3), (-50, 3), (-40, 3), (-30, 0), (-20, 4), (-10, 1), (0, 1), (10, 0),
 (20, 0), (30, 4), (40, 1), (50, 0), (60, 0), (70, 0), (80, 1), (90, 3)],))
>>> ev.evaluate(i00,ev.sxmacd30_s(i00),10,end=1444,begin=945)
((-7, 45, -67, 14, 12), (3, 5, 164, 296), ([(-90, 4), (-90, 0), (-80, 0), (-70,
1), (-60, 1), (-50, 1), (-40, 0), (-30, 1), (-20, 2), (-10, 2), (0, 4), (10, 2),
 (20, 1), (30, 2), (40, 2), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate(i00,ev.sxmacd45_b(i00),10,end=1429,begin=1000)
((-9, 93, -43, 3, 9), (2, 2, 170, 116), ([(-90, 0), (-90, 1), (-80, 0), (-70, 2)
, (-60, 0), (-50, 2), (-40, 1), (-30, 0), (-20, 3), (-10, 0), (0, 0), (10, 0), (
20, 0), (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate(i00,ev.sxmacd45_s(i00),10,end=1429,begin=1000)
((-9, 40, -39, 5, 8), (1, 3, 114, 174), ([(-90, 1), (-90, 0), (-80, 1), (-70, 0)
, (-60, 0), (-50, 1), (-40, 0), (-30, 0), (-20, 4), (-10, 1), (0, 1), (10, 1), (
20, 0), (30, 0), (40, 1), (50, 0), (60, 1), (70, 1), (80, 0), (90, 0)],))

##添加了strend2(ma30)>/<0条件
bfilter = strend2(ma30)>0
sfilter = strend2(ma30)<0

多

>>> ev.evaluate2_b(i00,ev.sxmacd45_b(i00),60,begin=944,end=1414,downlimit=90)
((35, 179, -89, 6, 7), (8, -5, 614, -260), ([(-90, 6), (-90, 0), (-80, 0), (-70,
 0), (-60, 1), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_b(i00,ev.sxmacd45_s(i00),60,begin=944,end=1414,downlimit=90)
((66, 184, -69, 8, 7), (9, -5, 820, -456), ([(-90, 5), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 2), (0, 0), (10, 1)
, (20, 1), (30, 0), (40, 0), (50, 0), (60, 0), (70, 1), (80, 0), (90, 5)],))
>>> ev.evaluate2_b(i00,ev.sxmacd30_b(i00),60,begin=944,end=1414,downlimit=90)
((72, 210, -88, 14, 12), (18, -11, 610, -424), ([(-90, 11), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (1
0, 0), (20, 0), (30, 1), (40, 0), (50, 1), (60, 0), (70, 0), (80, 1), (90, 11)],
>>> ev.evaluate2_b(i00,ev.sxmacd15_b(i00),60,begin=944,end=1414,downlimit=90)
((29, 245, -92, 14, 25), (20, -23, 856, -636), ([(-90, 24), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 2), (1
0, 0), (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 1), (90, 11)],
>>> ev.evaluate2_b(i00,ev.sxmacd10_b(i00),60,begin=944,end=1414,downlimit=90)   ####
((35, 244, -90, 22, 37), (32, -33, 740, -578), ([(-90, 34), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 1), (-40, 0), (-30, 1), (-20, 1), (-10, 0), (0, 1), (1
0, 0), (20, 1), (30, 2), (40, 2), (50, 0), (60, 1), (70, 0), (80, 0), (90, 15)],



空
>>> ev.evaluate2_s(i00,ev.sxmacd1_s(i00),60,begin=944,end=1414,uplimit=90)  ####
((34, 207, -86, 135, 195), (-167, 198, -936, 990), ([(-90, 169), (-90, 1), (-80,
 1), (-70, 1), (-60, 2), (-50, 1), (-40, 3), (-30, 4), (-20, 8), (-10, 5), (0, 8
), (10, 8), (20, 7), (30, 7), (40, 5), (50, 0), (60, 5), (70, 6), (80, 5), (90,
84)],))
>>> ev.evaluate2_s(i00,ev.sxmacd3_s(i00),60,begin=944,end=1414,uplimit=90)
((29, 175, -85, 73, 93), (-79, 95, -766, 850), ([(-90, 79), (-90, 0), (-80, 1),
(-70, 0), (-60, 0), (-50, 1), (-40, 3), (-30, 2), (-20, 3), (-10, 4), (0, 2), (1
0, 0), (20, 5), (30, 6), (40, 2), (50, 4), (60, 3), (70, 1), (80, 2), (90, 48)],
))
>>> ev.evaluate2_s(i00,ev.sxmacd10_s(i00),60,begin=944,end=1414,uplimit=90)
((30, 192, -85, 27, 38), (-32, 40, -668, 576), ([(-90, 32), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 0), (-40, 2), (-30, 1), (-20, 0), (-10, 2), (0, 1), (1
0, 3), (20, 2), (30, 1), (40, 0), (50, 0), (60, 1), (70, 1), (80, 0), (90, 18)],
>>> ev.evaluate2_s(i00,ev.sxmacd15_s(i00),60,begin=944,end=1414,uplimit=90)
((32, 169, -86, 18, 21), (-18, 25, -910, 664), ([(-90, 18), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 0), (-40, 0), (-30, 1), (-20, 1), (-10, 0), (0, 1), (1
0, 2), (20, 0), (30, 0), (40, 1), (50, 0), (60, 1), (70, 0), (80, 0), (90, 13)],
))
>>> ev.evaluate2_s(i00,ev.sxmacd15_b(i00),60,begin=944,end=1414,uplimit=90)
((29, 189, -95, 17, 22), (-20, 23, -856, 636), ([(-90, 22), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (1
0, 0), (20, 0), (30, 2), (40, 0), (50, 1), (60, 0), (70, 1), (80, 1), (90, 11)],
))



>>> ev.evaluate(i00,ev.sxmacd1_b(i00),60,begin=944,end=1414)
((-11, 171, -161, 140, 170), (143, 186, 1052, 852))
>>> ev.evaluate(i00,ev.sxmacd1_s(i00),60,begin=944,end=1414)
((-42, 143, -182, 142, 188), (167, 198, 936, 990))
>>> ev.evaluate(i00,ev.sxmacd3_b(i00),60,begin=944,end=1414)
((3, 154, -146, 80, 81), (92, 85, 856, 602))
>>> ev.evaluate(i00,ev.sxmacd3_s(i00),60,begin=944,end=1414)
((-35, 139, -168, 72, 94), (79, 95, 766, 850))
>>> ev.evaluate(i00,ev.sxmacd5_b(i00),60,begin=944,end=1414)
((6, 181, -143, 58, 68), (68, 72, 742, 728))
>>> ev.evaluate(i00,ev.sxmacd5_s(i00),60,begin=944,end=1414)
((-27, 124, -160, 58, 66), (54, 77, 668, 726))
>>> ev.evaluate(i00,ev.sxmacd10_b(i00),60,begin=944,end=1414)
((1, 197, -201, 30, 29), (32, 33, 740, 578))
>>> ev.evaluate(i00,ev.sxmacd10_s(i00),60,begin=944,end=1414)
((-31, 148, -175, 29, 36), (32, 40, 668, 576))
>>> ev.evaluate(i00,ev.sxmacd15_b(i00),60,begin=944,end=1414)
((10, 228, -176, 18, 21), (20, 23, 856, 636))
>>> ev.evaluate(i00,ev.sxmacd15_s(i00),60,begin=944,end=1414)
((13, 224, -167, 18, 21), (18, 25, 910, 664))
>>> ev.evaluate(i00,ev.sxmacd30_b(i00),60,begin=944,end=1414)
((64, 202, -155, 16, 10), (18, 11, 610, 424))
>>> ev.evaluate(i00,ev.sxmacd30_s(i00),60,begin=944,end=1414)
((-14, 143, -172, 13, 13), (15, 12, 820, 614))
>>> ev.evaluate(i00,ev.sxmacd45_s(i00),60,begin=944,end=1414)
((51, 153, -153, 10, 5), (9, 5, 820, 456))
>>> ev.evaluate(i00,ev.sxmacd45_b(i00),60,begin=944,end=1414)
((80, 161, -101, 9, 4), (8, 5, 614, 260))


'''



sxmacd1_b = lambda sif:xx_up(sif.diff1,sif.dea1)
sxmacd1_s = lambda sif:xx_down(sif.diff1,sif.dea1)
sxmacd5_b = lambda sif:sxnative(sif.close,sif.diff5x,sif.dea5x,sif.i_cof5)
sxmacd5_s = lambda sif:sxnative(sif.close,sif.diff5x,sif.dea5x,sif.i_cof5,xx_down)
sxmacd3_b = lambda sif:sxnative(sif.close,sif.diff3x,sif.dea3x,sif.i_cof3)
sxmacd3_s = lambda sif:sxnative(sif.close,sif.diff3x,sif.dea3x,sif.i_cof3,xx_down)
sxmacd10_b = lambda sif:sxnative(sif.close,sif.diff10x,sif.dea10x,sif.i_cof10)
sxmacd10_s = lambda sif:sxnative(sif.close,sif.diff10x,sif.dea10x,sif.i_cof10,xx_down)
sxmacd15_b = lambda sif:sxnative(sif.close,sif.diff15x,sif.dea15x,sif.i_cof15)
sxmacd15_s = lambda sif:sxnative(sif.close,sif.diff15x,sif.dea15x,sif.i_cof15,xx_down)
sxmacd30_b = lambda sif:sxnative(sif.close,sif.diff30x,sif.dea30x,sif.i_cof30)
sxmacd30_s = lambda sif:sxnative(sif.close,sif.diff30x,sif.dea30x,sif.i_cof30,xx_down)
sxmacd45_b = lambda sif:sxnative(sif.close,sif.diff45x,sif.dea45x,sif.i_cof45)
sxmacd45_s = lambda sif:sxnative(sif.close,sif.diff45x,sif.dea45x,sif.i_cof45,xx_down)

sxmacd1s_b = lambda sif:xx_bottom(sif.diff1,sif.dea1,length=2)
sxmacd1s_s = lambda sif:xx_top(sif.diff1,sif.dea1)
sxmacd5s_b = lambda sif:sxnative(sif.close,sif.diff5x,sif.dea5x,sif.i_cof5,fcustom(xx_bottom,length=2))   #
sxmacd5s_s = lambda sif:sxnative(sif.close,sif.diff5x,sif.dea5x,sif.i_cof5,fcustom(xx_top,length=2))
sxmacd3s_b = lambda sif:sxnative(sif.close,sif.diff3x,sif.dea3x,sif.i_cof3,fcustom(xx_bottom,length=2))   #
sxmacd3s_s = lambda sif:sxnative(sif.close,sif.diff3x,sif.dea3x,sif.i_cof3,fcustom(xx_top,length=2))
sxmacd10s_b = lambda sif:sxnative(sif.close,sif.diff10x,sif.dea10x,sif.i_cof10,fcustom(xx_bottom,length=2))   #
sxmacd10s_s = lambda sif:sxnative(sif.close,sif.diff10x,sif.dea10x,sif.i_cof10,fcustom(xx_top,length=2))
sxmacd15s_b = lambda sif:sxnative(sif.close,sif.diff15x,sif.dea15x,sif.i_cof15,fcustom(xx_bottom,length=2))   #
sxmacd15s_s = lambda sif:sxnative(sif.close,sif.diff15x,sif.dea15x,sif.i_cof15,fcustom(xx_top,length=2))
sxmacd30s_b = lambda sif:sxnative(sif.close,sif.diff30x,sif.dea30x,sif.i_cof30,fcustom(xx_bottom,length=2))   #
sxmacd30s_s = lambda sif:sxnative(sif.close,sif.diff30x,sif.dea30x,sif.i_cof30,fcustom(xx_top,length=2))



'''
未加ma30条件

>>> ev.evaluate2_b(i00,ev.sxmacd5s_s(i00),60,begin=1414,downlimit=80)       ####
((64, 161, -74, 17, 12), (19, -10, 470, -710), ([(-80, 10), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 1), (-30, 0), (-20, 0), (-10, 1), (0, 0), (10, 1), (20
, 0), (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 15)],))
>>> ev.evaluate2_b(i00,ev.sxmacd10s_s(i00),60,begin=1414,downlimit=80)
((56, 197, -85, 2, 2), (2, -2, 430, -344), ([(-80, 2), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 1)],))
>>> ev.evaluate2_b(i00,ev.sxmacd3s_s(i00),60,begin=1414,downlimit=80)       ####
((20, 172, -82, 14, 21), (18, -20, 546, -838), ([(-80, 20), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (10, 0), (20
, 0), (30, 3), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 10)],))

>>> ev.evaluate2_s(i00,ev.sxmacd5s_b(i00),60,begin=1414,uplimit=80)
((31, 244, -85, 6, 11), (-11, 11, -600, 732), ([(-80, 11), (-80, 0), (-70, 0), (
-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
 0), (30, 1), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_s(i00,ev.sxmacd30s_b(i00),60,begin=1414,uplimit=80)
((91, 203, -78, 3, 2), (-1, 3, -546, 480), ([(-80, 1), (-80, 1), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))


>>> ev.evaluate(i00,ev.sxmacd1s_b(i00),10)
((-2, 54, -56, 258, 269), (85, 100, 616, 300))
>>> ev.evaluate(i00,ev.sxmacd1s_s(i00),10)
((-4, 59, -59, 226, 259), (95, 94, 360, 446))
>>> ev.evaluate(i00,ev.sxmacd3s_b(i00),10)
((0, 55, -58, 96, 92), (30, 39, 486, 288))
>>> ev.evaluate(i00,ev.sxmacd3s_s(i00),10)
((-2, 71, -62, 94, 115), (50, 41, 678, 394))
>>> ev.evaluate(i00,ev.sxmacd5s_b(i00),10)
((11, 69, -54, 61, 54), (27, 19, 406, 332))
>>> ev.evaluate(i00,ev.sxmacd5s_s(i00),10)
((8, 62, -54, 68, 60), (23, 19, 580, 244))
>>> ev.evaluate(i00,ev.sxmacd10s_b(i00),10)
((-10, 80, -57, 21, 41), (8, 12, 434, 294))
>>> ev.evaluate(i00,ev.sxmacd10s_s(i00),10)
((10, 78, -46, 23, 28), (10, 6, 328, 190))
>>> ev.evaluate(i00,ev.sxmacd15s_s(i00),10)
((-15, 45, -54, 14, 21), (5, 7, 204, 310))
>>> ev.evaluate(i00,ev.sxmacd15s_b(i00),10)
((-18, 47, -80, 16, 17), (5, 8, 340, 382))
>>> ev.evaluate(i00,ev.sxmacd30s_b(i00),10)
((-17, 125, -81, 5, 11), (3, 6, 388, 212))
>>> ev.evaluate(i00,ev.sxmacd30s_s(i00),10)
((-19, 55, -142, 10, 6), (4, 4, 126, 282))


添加sma30条件
多
>>> ev.evaluate2_b(i00,ev.sxmacd1s_b(i00),60,begin=1414,downlimit=90)
((31, 189, -95, 20, 25), (29, -25, 594, -698), ([(-90, 25), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (1
0, 0), (20, 0), (30, 0), (40, 1), (50, 0), (60, 0), (70, 1), (80, 2), (90, 16)],
))
>>> ev.evaluate2_b(i00,ev.sxmacd10s_s(i00),60,begin=1414,downlimit=90)
((51, 197, -95, 2, 2), (2, -2, 430, -344), ([(-90, 2), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 1)],))
>>> ev.evaluate2_b(i00,ev.sxmacd10s_b(i00),60,begin=1414,downlimit=90)          
((41, 164, -82, 5, 5), (5, -4, 414, -508), ([(-90, 4), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0)
, (20, 0), (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ev.sxmacd30s_s(i00),60,begin=1414,downlimit=90)
((78, 224, -69, 3, 3), (3, -2, 384, -486), ([(-90, 2), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (10, 0)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))

#空
>>> ev.evaluate2_s(i00,ev.sxmacd30s_b(i00),60,begin=1414,uplimit=90)
((89, 203, -83, 3, 2), (-1, 3, -546, 480), ([(-90, 1), (-90, 0), (-80, 1), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_s(i00,ev.sxmacd15s_s(i00),60,begin=1414,uplimit=90)
((144, 223, -95, 6, 2), (-2, 7, -166, 588), ([(-90, 2), (-90, 0), (-80, 0), (-70
, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1
), (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 5)],))



##注意，同一组信号，做多和做空，只要设定好止损，都能获利!!!!!
>>> ev.evaluate2_s(i00,ev.sxmacd30s_s(i00),60,begin=1414,uplimit=90)
((36, 168, -95, 3, 3), (-3, 2, -384, 486), ([(-90, 3), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_b(i00,ev.sxmacd30s_b(i00),60,begin=1414,downlimit=90)
((48, 546, -77, 1, 4), (1, -3, 546, -480), ([(-90, 3), (-90, 0), (-80, 0), (-70,
 0), (-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0)
, (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 1)],))
######



>>> ev.evaluate(i00,ev.sxmacd1s_b(i00),10)
((2, 68, -57, 100, 112), (47, 47, 616, 260))
>>> ev.evaluate(i00,ev.sxmacd1s_s(i00),10)
((-7, 54, -68, 109, 109), (48, 51, 330, 446))
>>> ev.evaluate(i00,ev.sxmacd3s_b(i00),10)
((-11, 35, -47, 21, 27), (6, 7, 152, 258))
>>> ev.evaluate(i00,ev.sxmacd3s_s(i00),10)
((-12, 79, -84, 26, 33), (15, 19, 416, 394))
>>> ev.evaluate(i00,ev.sxmacd5s_b(i00),10)
((10, 61, -39, 26, 27), (11, 7, 376, 210))
>>> ev.evaluate(i00,ev.sxmacd5s_s(i00),10)
((20, 68, -55, 36, 23), (14, 9, 580, 184))
>>> ev.evaluate(i00,ev.sxmacd10s_b(i00),10)
((-4, 81, -52, 18, 32), (7, 6, 434, 294))
>>> ev.evaluate(i00,ev.sxmacd10s_s(i00),10)
((6, 82, -47, 19, 27), (8, 6, 328, 190))
>>> ev.evaluate(i00,ev.sxmacd15s_b(i00),10)
((-19, 47, -85, 16, 16), (5, 8, 340, 382))
>>> ev.evaluate(i00,ev.sxmacd15s_s(i00),10)
((-15, 45, -54, 14, 21), (5, 7, 204, 310))
>>> ev.evaluate(i00,ev.sxmacd30s_b(i00),10)
((-24, 113, -79, 4, 10), (2, 5, 388, 212))
>>> ev.evaluate(i00,ev.sxmacd30s_s(i00),10)
((-19, 55, -142, 10, 6), (4, 4, 126, 282))

'''




sxma_5_13b = lambda sif:xx_up(sif.ma5,sif.ma13)
sxma_5_13s = lambda sif:xx_down(sif.ma5,sif.ma13)
sx5ma_5_13b = lambda sif:sxnative(sif.close,ma(sif.close5,5),ma(sif.close5,13),sif.i_cof5)
sx5ma_5_13s = lambda sif:sxnative(sif.close,ma(sif.close5,5),ma(sif.close5,13),sif.i_cof5,xx_down)
sxma_3_13b = lambda sif:xx_up(sif.ma3,sif.ma13)
sxma_3_13s = lambda sif:xx_down(sif.ma3,sif.ma13)

add_funcs(test_funcs,'sxma')    #包括macd/ma

def sxfkdj(sclose,sshigh,sslow,ssclose,sindics,sfunc=xx_up):
    sk,sd = skdj(sshigh,sslow,ssclose)    
    sx = sfunc(sk,sd)
    signal = np.zeros_like(sclose)
    signal[sindics] = sx
    return signal

'''
skdj全部是反指
#从反指中找出一个最反指的做反向交易
>>> ev.evaluate2_s(i00,ev.sxskdj30_b(i00),60,uplimit=60,begin=944,end=1414)
((36, 158, -65, 24, 29), (-29, 36, -714, 558), ([(-60, 29), (-60, 0), (-50, 0),
(-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (30, 2), (40,
1), (50, 0), (60, 0), (70, 2), (80, 2), (90, 17)],))
>>> ev.evaluate2_s(i00,ev.sxskdj30_b(i00),120,uplimit=60,begin=944,end=1314)    ####
((81, 316, -65, 15, 24), (-24, 32, -942, 768), ([(-60, 24), (-60, 0), (-50, 0),
(-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (30, 0), (40,
0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 15)],))

#量足
>>> ev.evaluate2_s(i00,ev.sxskdj3_b(i00),120,uplimit=90,begin=944,end=1314)     ####
((54, 295, -92, 149, 245), (-230, 290, -1260, 1492), ([(-90, 234), (-90, 0), (-8
0, 0), (-70, 1), (-60, 0), (-50, 1), (-40, 1), (-30, 1), (-20, 2), (-10, 5), (0,
 2), (10, 3), (20, 2), (30, 8), (40, 4), (50, 4), (60, 4), (70, 1), (80, 3), (90
, 118)],))
>>> ev.evaluate2_s(i00,ev.sxskdj3_b(i00),120,uplimit=60,begin=944,end=1314)
((43, 317, -65, 111, 283), (-271, 290, -1260, 1492), ([(-60, 279), (-60, 0), (-5
0, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 3), (0, 2), (10, 1), (20, 1), (30, 4)
, (40, 2), (50, 3), (60, 3), (70, 0), (80, 2), (90, 93)],))

>>> ev.evaluate2_s(i00,ev.sxskdj3_b(i00),60,uplimit=80,begin=944,end=1414)
((25, 174, -79, 254, 363), (-320, 381, -966, 1070), ([(-80, 323), (-80, 0), (-70
, 0), (-60, 1), (-50, 5), (-40, 9), (-30, 10), (-20, 8), (-10, 7), (0, 9), (10,
18), (20, 11), (30, 9), (40, 7), (50, 9), (60, 15), (70, 9), (80, 7), (90, 160)]
,))
>>> ev.evaluate2_s(i00,ev.sxskdj5_b(i00),60,uplimit=80,begin=944,end=1414)
((31, 181, -81, 164, 220), (-202, 233, -966, 1058), ([(-80, 205), (-80, 0), (-70
, 1), (-60, 0), (-50, 2), (-40, 0), (-30, 5), (-20, 3), (-10, 4), (0, 9), (10, 8
), (20, 10), (30, 3), (40, 8), (50, 3), (60, 11), (70, 5), (80, 7), (90, 100)],)
)
>>> ev.evaluate2_s(i00,ev.sxskdj5_b(i00),60,uplimit=60,begin=944,end=1414)
((27, 198, -64, 134, 250), (-241, 233, -966, 1058), ([(-60, 243), (-60, 0), (-50
, 1), (-40, 0), (-30, 3), (-20, 1), (-10, 2), (0, 5), (10, 6), (20, 8), (30, 1),
 (40, 6), (50, 2), (60, 10), (70, 4), (80, 5), (90, 87)],))



>>> ev.evaluate(i00,ev.sxskdj1_b(i00),10)
((-2, 58, -56, 1046, 1176), (378, 424, 616, 408)
>>> ev.evaluate(i00,ev.sxskdj1_s(i00),10)
((-3, 58, -59, 1049, 1153), (387, 415, 566, 490)
>>> ev.evaluate(i00,ev.sxskdj3_b(i00),10)
((-8, 52, -58, 371, 436), (118, 158, 486, 512)
>>> ev.evaluate(i00,ev.sxskdj3_s(i00),10)
((5, 65, -56, 411, 402), (178, 138, 566, 392)
>>> ev.evaluate(i00,ev.sxskdj5_b(i00),10)
((-7, 55, -57, 214, 264), (68, 91, 572, 370)
>>> ev.evaluate(i00,ev.sxskdj5_s(i00),10)
((4, 65, -59, 249, 242), (106, 87, 580, 358)
>>> ev.evaluate(i00,ev.sxskdj10_b(i00),10)
((-6, 57, -54, 92, 120), (33, 34, 260, 366)
>>> ev.evaluate(i00,ev.sxskdj10_s(i00),10)
((-2, 50, -50, 109, 117), (32, 37, 364, 264)
>>> ev.evaluate(i00,ev.sxskdj15_b(i00),10)
((-9, 57, -53, 57, 85), (25, 30, 320, 314)
>>> ev.evaluate(i00,ev.sxskdj15_s(i00),10)
((-8, 49, -53, 67, 82), (20, 25, 328, 346)
>>> ev.evaluate(i00,ev.sxskdj30_b(i00),10)
((-18, 72, -62, 25, 50), (10, 17, 340, 382)
((-4, 55, -66, 37, 35), (10, 15, 380, 282)

添加sma30条件
多

空
>>> ev.evaluate2_s(i00,ev.sxskdj1_s(i00),60,uplimit=90,end=1414,begin=944)      ###
((30, 197, -88, 350, 491), (-434, 502, -1064, 1076), ([(-90, 438), (-90, 0), (-8
0, 3), (-70, 6), (-60, 4), (-50, 3), (-40, 7), (-30, 9), (-20, 7), (-10, 14), (0
, 16), (10, 13), (20, 20), (30, 16), (40, 8), (50, 12), (60, 16), (70, 17), (80,
 18), (90, 214)],))
>>> ev.evaluate2_s(i00,ev.sxskdj3_s(i00),60,uplimit=90,end=1414,begin=944)
((32, 204, -88, 115, 165), (-144, 163, -814, 990), ([(-90, 145), (-90, 0), (-80,
 1), (-70, 0), (-60, 2), (-50, 3), (-40, 6), (-30, 3), (-20, 1), (-10, 4), (0, 7
), (10, 4), (20, 7), (30, 4), (40, 3), (50, 1), (60, 7), (70, 1), (80, 4), (90,
77)],))
>>> ev.evaluate2_s(i00,ev.sxskdj3_b(i00),60,uplimit=90,end=1414,begin=944)
((29, 175, -87, 111, 141), (-120, 157, -918, 872), ([(-90, 123), (-90, 0), (-80,
 0), (-70, 1), (-60, 0), (-50, 1), (-40, 6), (-30, 4), (-20, 2), (-10, 4), (0, 5
), (10, 5), (20, 4), (30, 2), (40, 2), (50, 4), (60, 5), (70, 4), (80, 4), (90,
76)],))
>>> ev.evaluate2_s(i00,ev.sxskdj10_s(i00),60,uplimit=90,end=1414,begin=944)
((32, 151, -80, 62, 66), (-50, 73, -806, 786), ([(-90, 51), (-90, 0), (-80, 1),
(-70, 0), (-60, 1), (-50, 0), (-40, 4), (-30, 3), (-20, 6), (-10, 0), (0, 1), (1
0, 2), (20, 5), (30, 1), (40, 6), (50, 4), (60, 4), (70, 3), (80, 4), (90, 32)],
))
>>> ev.evaluate2_s(i00,ev.sxskdj5_s(i00),60,uplimit=90,end=1414,begin=944)
((27, 212, -89, 71, 112), (-98, 104, -786, 880), ([(-90, 100), (-90, 0), (-80, 1
), (-70, 1), (-60, 1), (-50, 2), (-40, 2), (-30, 3), (-20, 1), (-10, 1), (0, 0),
 (10, 1), (20, 4), (30, 4), (40, 1), (50, 4), (60, 2), (70, 2), (80, 3), (90, 50
)],))
>>> ev.evaluate2_s(i00,ev.sxskdj30_b(i00),60,uplimit=90,end=1414,begin=944)
((33, 180, -95, 22, 25), (-25, 31, -714, 558), ([(-90, 25), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (1
0, 0), (20, 0), (30, 0), (40, 1), (50, 1), (60, 0), (70, 2), (80, 2), (90, 16)],
))


>>> ev.evaluate(i00,ev.sxskdj1_b(i00),10)
((1, 66, -54, 469, 549), (211, 192, 616, 316))
>>> ev.evaluate(i00,ev.sxskdj1_s(i00),10)
((-6, 54, -66, 566, 561), (185, 240, 566, 490))
>>> ev.evaluate(i00,ev.sxskdj3_b(i00),10)
((-10, 52, -53, 133, 195), (54, 60, 356, 326))
>>> ev.evaluate(i00,ev.sxskdj3_s(i00),10)
((-5, 53, -63, 185, 183), (72, 69, 416, 392))
>>> ev.evaluate(i00,ev.sxskdj5_b(i00),10)
((-6, 56, -53, 91, 120), (30, 33, 572, 370))
>>> ev.evaluate(i00,ev.sxskdj5_s(i00),10)
((5, 60, -64, 130, 104), (50, 46, 580, 358))
>>> ev.evaluate(i00,ev.sxskdj10_b(i00),10)
((-4, 57, -51, 71, 92), (26, 26, 260, 366))
>>> ev.evaluate(i00,ev.sxskdj10_s(i00),10)
((-4, 44, -48, 86, 92), (23, 30, 328, 264))
>>> ev.evaluate(i00,ev.sxskdj15_b(i00),10)
((-10, 54, -52, 51, 79), (21, 25, 320, 314))
>>> ev.evaluate(i00,ev.sxskdj15_s(i00),10)
((-11, 45, -54, 61, 79), (15, 25, 328, 346))
>>> ev.evaluate(i00,ev.sxskdj30_b(i00),10)
((-17, 77, -63, 22, 45), (9, 15, 340, 382))
>>> ev.evaluate(i00,ev.sxskdj30_s(i00),10)
((-4, 56, -69, 34, 31), (10, 14, 380, 282))


'''

sxskdj1_b = lambda sif:xx_up(sif.sk,sif.sd)
sxskdj1_s = lambda sif:xx_down(sif.sk,sif.sd)
sxskdj5_b = lambda sif:sxfkdj(sif.close,sif.high5,sif.low5,sif.close5,sif.i_cof5)
sxskdj5_s = lambda sif:sxfkdj(sif.close,sif.high5,sif.low5,sif.close5,sif.i_cof5,xx_down)
sxskdj3_b = lambda sif:sxfkdj(sif.close,sif.high3,sif.low3,sif.close3,sif.i_cof3)
sxskdj3_s = lambda sif:sxfkdj(sif.close,sif.high3,sif.low3,sif.close3,sif.i_cof3,xx_down)
sxskdj10_b = lambda sif:sxfkdj(sif.close,sif.high10,sif.low10,sif.close10,sif.i_cof10)
sxskdj10_s = lambda sif:sxfkdj(sif.close,sif.high10,sif.low10,sif.close10,sif.i_cof10,xx_down)
sxskdj15_b = lambda sif:sxfkdj(sif.close,sif.high15,sif.low15,sif.close15,sif.i_cof15)
sxskdj15_s = lambda sif:sxfkdj(sif.close,sif.high15,sif.low15,sif.close15,sif.i_cof15,xx_down)
sxskdj30_b = lambda sif:sxfkdj(sif.close,sif.high30,sif.low30,sif.close30,sif.i_cof30)
sxskdj30_s = lambda sif:sxfkdj(sif.close,sif.high30,sif.low30,sif.close30,sif.i_cof30,xx_down)

add_funcs(test_funcs,'sxskdj')    #包括macd/ma

def sxfrsi(sclose,source,rshort,rlong,sindics,sfunc=xx_up):
    rsia = rsi2(source,rshort)
    rsib = rsi2(source,rlong)
    sx = sfunc(rsia,rsib)
    signal = np.zeros_like(sclose)
    signal[sindics] = sx
    return signal

''' rsi30分钟时正向的
>>> ev.evaluate(i00,ev.sxrsi30_b(i00),10)
((10, 94, -53, 31, 41), (15, 16, 508, 212))

#多仓
###成功率太小
>>> ev.evaluate2_b(i00,ev.sxrsi30_b(i00),60,begin=945,downlimit=80,end=1414)
((30, 357, -83, 9, 26), (19, -25, 918, -636), ([(-80, 25), (-80, 0), (-70, 0), (
-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 9)],))
>>> ev.evaluate2_b(i00,ev.sxrsi30_b(i00),120,begin=945,downlimit=80,end=1314)
((17, 504, -85, 4, 19), (15, -19, 942, -856), ([(-80, 19), (-80, 0), (-70, 0), (
-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ev.sxrsi30_b(i00),60,begin=1045,downlimit=80,end=1414)
((25, 327, -82, 6, 17), (12, -16, 918, -636), ([(-80, 16), (-80, 0), (-70, 0), (
-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 6)],))
 ##只有这个勉强可用，但次数太少
>>> ev.evaluate2_b(i00,ev.sxrsi30_b(i00),60,begin=1145,downlimit=80,end=1414)
((63, 343, -78, 4, 8), (6, -7, 918, -424), ([(-80, 7), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))

#空
#这个勉强可以
>>> ev.evaluate2_s(i00,ev.sxrsi15_b(i00),60,begin=945,uplimit=90,end=1414)  #####
((28, 192, -90, 44, 61), (-56, 64, -856, 1076), ([(-90, 56), (-90, 0), (-80, 0),
 (-70, 0), (-60, 1), (-50, 0), (-40, 0), (-30, 3), (-20, 1), (-10, 0), (0, 0), (
10, 0), (20, 1), (30, 3), (40, 1), (50, 3), (60, 1), (70, 3), (80, 2), (90, 30)]
,))

>>> ev.evaluate2_s(i00,ev.sxrsi15_b(i00),30,begin=945,uplimit=90,end=1444)
((9, 112, -83, 58, 64), (-51, 57, -670, 816), ([(-90, 52), (-90, 0), (-80, 1), (
-70, 2), (-60, 0), (-50, 1), (-40, 2), (-30, 2), (-20, 0), (-10, 4), (0, 3), (10
, 5), (20, 6), (30, 4), (40, 1), (50, 1), (60, 2), (70, 4), (80, 2), (90, 30)],)
)
>>> ev.evaluate2_s(i00,ev.sxrsi15_b(i00),120,begin=945,uplimit=90,end=1314)
((9, 197, -93, 25, 46), (-45, 51, -1164, 802), ([(-90, 45), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 1), (0, 0), (1
0, 0), (20, 1), (30, 1), (40, 0), (50, 2), (60, 3), (70, 0), (80, 0), (90, 18)],
))


>>> ev.evaluate(i00,ev.sxrsi1_b(i00),10)
((-3, 59, -58, 1119, 1255), (411, 471, 616, 390))
>>> ev.evaluate(i00,ev.sxrsi1_s(i00),10)
((-1, 61, -58, 1155, 1260), (455, 468, 594, 490))
>>> ev.evaluate(i00,ev.sxrsi3_b(i00),10)
((-4, 58, -54, 340, 427), (124, 146, 508, 408))
>>> ev.evaluate(i00,ev.sxrsi3_s(i00),10)
((2, 64, -58, 391, 405), (159, 135, 590, 394))
>>> ev.evaluate(i00,ev.sxrsi5_b(i00),10)
((-7, 53, -55, 196, 245), (68, 82, 508, 332))
>>> ev.evaluate(i00,ev.sxrsi5_s(i00),10)
((6, 65, -49, 218, 233), (84, 75, 684, 322))
>>> ev.evaluate(i00,ev.sxrsi10_b(i00),10)
((-8, 71, -63, 92, 130), (32, 49, 406, 496))
>>> ev.evaluate(i00,ev.sxrsi10_s(i00),10)
((8, 62, -51, 118, 109), (45, 30, 684, 346))
>>> ev.evaluate(i00,ev.sxrsi15_b(i00),10)
((-20, 52, -64, 63, 103), (25, 31, 376, 458))
>>> ev.evaluate(i00,ev.sxrsi15_s(i00),10)
((1, 56, -52, 82, 85), (26, 29, 508, 346))
>>> ev.evaluate(i00,ev.sxrsi30_b(i00),10)
((10, 94, -53, 31, 41), (15, 16, 508, 212))
>>> ev.evaluate(i00,ev.sxrsi30_s(i00),10)
((0, 43, -56, 41, 32), (10, 10, 220, 216))

##添加sma30条件后
多
>>> ev.evaluate2_b(i00,ev.sxrsi1_b(i00),60,begin=944,end=1414,downlimit=80)
((23, 226, -81, 264, 517), (425, -468, 1068, -758), ([(-80, 478), (-80, 1), (-70
, 3), (-60, 5), (-50, 4), (-40, 5), (-30, 7), (-20, 10), (-10, 4), (0, 10), (10,
 8), (20, 6), (30, 5), (40, 10), (50, 10), (60, 9), (70, 10), (80, 12), (90, 184
)],))

空
>>> ev.evaluate2_s(i00,ev.sxrsi1_s(i00),60,begin=944,end=1414,uplimit=80)       ###
((29, 190, -79, 354, 528), (-468, 537, -936, 970), ([(-80, 475), (-80, 0), (-70,
 2), (-60, 5), (-50, 2), (-40, 6), (-30, 9), (-20, 12), (-10, 17), (0, 14), (10,
 17), (20, 11), (30, 16), (40, 19), (50, 10), (60, 15), (70, 17), (80, 13), (90,
 222)],))
>>> ev.evaluate2_s(i00,ev.sxrsi3_s(i00),60,begin=944,end=1414,uplimit=80)
((29, 195, -81, 121, 183), (-170, 185, -830, 898), ([(-80, 170), (-80, 0), (-70,
 0), (-60, 1), (-50, 1), (-40, 2), (-30, 3), (-20, 3), (-10, 3), (0, 2), (10, 5)
, (20, 5), (30, 6), (40, 4), (50, 3), (60, 6), (70, 6), (80, 5), (90, 79)],))
>>> ev.evaluate2_s(i00,ev.sxrsi30_s(i00),60,begin=944,end=1414,uplimit=80)
((27, 166, -83, 23, 29), (-28, 32, -822, 664), ([(-80, 28), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 1), (0, 1), (10, 1), (20
, 2), (30, 1), (40, 0), (50, 1), (60, 3), (70, 0), (80, 1), (90, 13)],))


>>> ev.evaluate(i00,ev.sxrsi1_b(i00),10)
((4, 69, -55, 514, 569), (233, 209, 616, 296))
>>> ev.evaluate(i00,ev.sxrsi1_s(i00),10)
((-10, 51, -65, 560, 615), (186, 263, 580, 490))
>>> ev.evaluate(i00,ev.sxrsi3_b(i00),10)
((-5, 58, -50, 153, 214), (60, 70, 508, 384))
>>> ev.evaluate(i00,ev.sxrsi3_s(i00),10)
((-7, 58, -68, 193, 207), (74, 91, 428, 394))
>>> ev.evaluate(i00,ev.sxrsi5_b(i00),10)
((-8, 52, -53, 106, 140), (35, 47, 508, 328))
>>> ev.evaluate(i00,ev.sxrsi5_s(i00),10)
((3, 64, -53, 127, 137), (50, 52, 580, 322))
>>> ev.evaluate(i00,ev.sxrsi10_b(i00),10)
((0, 73, -51, 63, 90), (24, 25, 356, 370))
>>> ev.evaluate(i00,ev.sxrsi10_s(i00),10)
((2, 54, -48, 83, 87), (30, 23, 328, 346))
>>> ev.evaluate(i00,ev.sxrsi15_b(i00),10)
((-16, 51, -58, 56, 88), (19, 24, 376, 382))
>>> ev.evaluate(i00,ev.sxrsi15_s(i00),10)
((-1, 54, -54, 66, 69), (19, 24, 380, 346))
>>> ev.evaluate(i00,ev.sxrsi30_b(i00),10)
>>> ev.evaluate(i00,ev.sxrsi30_s(i00),10)
((0, 43, -57, 40, 31), (10, 10, 220, 216))


'''
sxrsi1_b = lambda sif:sxfrsi(sif.close,sif.close,7,19,sif.i_cof)
sxrsi1_s = lambda sif:sxfrsi(sif.close,sif.close,7,19,sif.i_cof,xx_down)
sxrsi3_b = lambda sif:sxfrsi(sif.close,sif.close3,7,19,sif.i_cof3)
sxrsi3_s = lambda sif:sxfrsi(sif.close,sif.close3,7,19,sif.i_cof3,xx_down)
sxrsi5_b = lambda sif:sxfrsi(sif.close,sif.close5,7,19,sif.i_cof5)
sxrsi5_s = lambda sif:sxfrsi(sif.close,sif.close5,7,19,sif.i_cof5,xx_down)
sxrsi10_b = lambda sif:sxfrsi(sif.close,sif.close10,7,19,sif.i_cof10)
sxrsi10_s = lambda sif:sxfrsi(sif.close,sif.close10,7,19,sif.i_cof10,xx_down)
sxrsi15_b = lambda sif:sxfrsi(sif.close,sif.close15,7,19,sif.i_cof15)
sxrsi15_s = lambda sif:sxfrsi(sif.close,sif.close15,7,19,sif.i_cof15,xx_down)
sxrsi30_b = lambda sif:sxfrsi(sif.close,sif.close30,7,19,sif.i_cof30)    #奇异
sxrsi30_s = lambda sif:sxfrsi(sif.close,sif.close30,7,19,sif.i_cof30,xx_down)
sxrsi60_b = lambda sif:sxfrsi(sif.close,sif.close60,7,19,sif.i_cof60)
sxrsi60_s = lambda sif:sxfrsi(sif.close,sif.close60,7,19,sif.i_cof60,xx_down)

add_funcs(test_funcs,'sxrsi')    #包括macd/ma

def sxfroc(sclose,source,sindics,length=12,malength=6,sfunc=xx_up):
    sr = sroc(source,length)
    msr = ma(sr,malength)
    sx = sfunc(sr,msr)
    signal = np.zeros_like(sclose)
    signal[sindics] = sx
    return signal

'''
可做多的没有
空:
>>> ev.evaluate2_s(i00,ev.sxroc30_b(i00),60,uplimit=80,begin=945,end=1414)
((30, 191, -84, 22, 31), (-29, 38, -598, 486), ([(-80, 30), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 1), (20
, 1), (30, 0), (40, 1), (50, 0), (60, 1), (70, 2), (80, 0), (90, 16)],))
>>> ev.evaluate2_s(i00,ev.sxroc30_b(i00),120,uplimit=80,begin=945,end=1314)
((63, 305, -85, 11, 18), (-18, 24, -792, 888), ([(-80, 18), (-80, 0), (-70, 0),
(-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20
, 0), (30, 0), (40, 0), (50, 1), (60, 1), (70, 0), (80, 0), (90, 9)],))

>>> ev.evaluate2_s(i00,ev.sxroc15_b(i00),60,uplimit=90,begin=945,end=1414)  ####
((38, 196, -88, 51, 64), (-56, 70, -682, 1076), ([(-90, 58), (-90, 0), (-80, 0),
 (-70, 0), (-60, 0), (-50, 0), (-40, 1), (-30, 3), (-20, 2), (-10, 0), (0, 3), (
10, 1), (20, 1), (30, 0), (40, 1), (50, 1), (60, 1), (70, 6), (80, 1), (90, 36)]
,))
>>> ev.evaluate2_s(i00,ev.sxroc10_b(i00),120,uplimit=90,begin=945,end=1314)     ####
((62, 285, -93, 47, 68), (-66, 78, -1142, 1452), ([(-90, 66), (-90, 0), (-80, 0)
, (-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 1), (0, 1),
(10, 1), (20, 0), (30, 1), (40, 2), (50, 3), (60, 1), (70, 2), (80, 1), (90, 35)
],))
>>> ev.evaluate2_s(i00,ev.sxroc5_b(i00),120,uplimit=90,begin=945,end=1314)
((38, 302, -92, 63, 128), (-120, 135, -1142, 1492), ([(-90, 121), (-90, 0), (-80
, 0), (-70, 1), (-60, 1), (-50, 0), (-40, 1), (-30, 1), (-20, 3), (-10, 0), (0,
2), (10, 1), (20, 1), (30, 1), (40, 1), (50, 0), (60, 2), (70, 3), (80, 2), (90,
 50)],))
>>> ev.evaluate2_s(i00,ev.sxroc3_b(i00),120,uplimit=80,begin=945,end=1314)
((37, 272, -84, 104, 201), (-194, 221, -1142, 1204), ([(-80, 196), (-80, 0), (-7
0, 0), (-60, 0), (-50, 2), (-40, 1), (-30, 0), (-20, 1), (-10, 1), (0, 2), (10,
2), (20, 1), (30, 5), (40, 4), (50, 1), (60, 6), (70, 4), (80, 4), (90, 75)],))
>>> ev.evaluate2_s(i00,ev.sxroc3_b(i00),60,uplimit=80,begin=945,end=1414)
((30, 185, -81, 205, 286), (-257, 302, -1006, 1054), ([(-80, 263), (-80, 0), (-7
0, 0), (-60, 1), (-50, 3), (-40, 8), (-30, 0), (-20, 4), (-10, 7), (0, 3), (10,
7), (20, 13), (30, 6), (40, 7), (50, 7), (60, 8), (70, 3), (80, 9), (90, 142)],)

>>> ev.evaluate(i00,ev.sxroc1_b(i00),10)
((-7, 57, -62, 558, 658), (225, 298, 616, 408))
>>> ev.evaluate(i00,ev.sxroc1_s(i00),10)
((-3, 62, -64, 584, 628), (252, 261, 454, 458))
>>> ev.evaluate(i00,ev.sxroc3_b(i00),10)
((-7, 55, -56, 291, 368), (113, 146, 484, 366))
>>> ev.evaluate(i00,ev.sxroc3_s(i00),10)
((1, 60, -60, 339, 327), (141, 110, 678, 392))
>>> ev.evaluate(i00,ev.sxroc5_b(i00),10)
((-6, 53, -59, 193, 217), (60, 86, 474, 432))
>>> ev.evaluate(i00,ev.sxroc5_s(i00),10)
((3, 66, -55, 202, 220), (88, 83, 580, 358))
>>> ev.evaluate(i00,ev.sxroc10_b(i00),10)
((-2, 63, -56, 106, 128), (39, 48, 488, 366))
>>> ev.evaluate(i00,ev.sxroc10_s(i00),10)
((-1, 58, -56, 116, 124), (40, 44, 406, 358))
>>> ev.evaluate(i00,ev.sxroc15_b(i00),10)
((-16, 64, -63, 62, 107), (25, 33, 474, 458))
>>> ev.evaluate(i00,ev.sxroc15_s(i00),10)
((-1, 56, -60, 86, 82), (24, 31, 566, 346))
>>> ev.evaluate(i00,ev.sxroc30_b(i00),10)
((-21, 44, -63, 32, 50), (12, 19, 284, 382))
>>> ev.evaluate(i00,ev.sxroc30_s(i00),10)
((-9, 45, -58, 38, 41), (10, 17, 220, 256))
>>> ev.evaluate(i00,ev.sxroc60_b(i00),10)
((-28, 60, -69, 14, 30), (7, 10, 284, 268))
>>> ev.evaluate(i00,ev.sxroc60_s(i00),10)
((14, 68, -43, 22, 21), (7, 9, 380, 200))

#添加sma30，貌似无效

多：无
空
>>> ev.evaluate2_s(i00,ev.sxroc30_b(i00),60,uplimit=90,end=1414)        ####
((39, 181, -92, 26, 28), (-25, 41, -598, 558), ([(-90, 26), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 0), (-40, 1), (-30, 0), (-20, 0), (-10, 0), (0, 1), (1
0, 1), (20, 1), (30, 0), (40, 1), (50, 1), (60, 1), (70, 2), (80, 1), (90, 17)],
))
>>> ev.evaluate2_s(i00,ev.sxroc3_s(i00),60,uplimit=90,end=1414)
((31, 208, -90, 105, 153), (-138, 157, -766, 990), ([(-90, 139), (-90, 0), (-80,
 1), (-70, 0), (-60, 2), (-50, 1), (-40, 5), (-30, 1), (-20, 2), (-10, 2), (0, 4
), (10, 7), (20, 3), (30, 5), (40, 2), (50, 3), (60, 6), (70, 2), (80, 3), (90,
70)],))
>>> ev.evaluate2_s(i00,ev.sxroc30_s(i00),60,uplimit=90,end=1414)        ####
((47, 164, -86, 26, 23), (-19, 36, -822, 488), ([(-90, 20), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 2), (-20, 0), (-10, 1), (0, 3), (1
0, 1), (20, 1), (30, 1), (40, 2), (50, 1), (60, 1), (70, 0), (80, 0), (90, 16)],
))




>>> ev.evaluate(i00,ev.sxroc1_b(i00),10)
((-9, 62, -62, 244, 328), (113, 150, 616, 366))
>>> ev.evaluate(i00,ev.sxroc1_s(i00),10)
((-6, 53, -70, 312, 286), (115, 132, 444, 458))
>>> ev.evaluate(i00,ev.sxroc3_b(i00),10)
((-9, 58, -50, 120, 192), (53, 67, 304, 366))
>>> ev.evaluate(i00,ev.sxroc3_s(i00),10)
((-8, 53, -71, 166, 163), (60, 69, 412, 392))
>>> ev.evaluate(i00,ev.sxroc5_b(i00),10)
((-4, 55, -47, 77, 107), (24, 32, 376, 258))
>>> ev.evaluate(i00,ev.sxroc5_s(i00),10)
((-5, 57, -55, 93, 114), (34, 45, 580, 358))
>>> ev.evaluate(i00,ev.sxroc10_b(i00),10)
((-3, 57, -51, 67, 84), (22, 29, 310, 366))
>>> ev.evaluate(i00,ev.sxroc10_s(i00),10)
((-2, 49, -49, 74, 80), (17, 25, 406, 358))
>>> ev.evaluate(i00,ev.sxroc15_b(i00),10)
((-16, 53, -58, 50, 80), (18, 22, 320, 382))
>>> ev.evaluate(i00,ev.sxroc15_s(i00),10)
((-11, 43, -63, 66, 69), (14, 28, 278, 346))
>>> ev.evaluate(i00,ev.sxroc30_b(i00),10)
((-21, 50, -64, 26, 43), (10, 17, 284, 382))
>>> ev.evaluate(i00,ev.sxroc30_s(i00),10)
((-8, 42, -52, 30, 35), (7, 13, 220, 256))


'''
sxroc1_b = lambda sif:sxfroc(sif.close,sif.close,sif.i_cof)
sxroc1_s = lambda sif:sxfroc(sif.close,sif.close,sif.i_cof,sfunc=xx_down)
sxroc3_b = lambda sif:sxfroc(sif.close,sif.close3,sif.i_cof3)
sxroc3_s = lambda sif:sxfroc(sif.close,sif.close3,sif.i_cof3,sfunc=xx_down)
sxroc5_b = lambda sif:sxfroc(sif.close,sif.close5,sif.i_cof5)
sxroc5_s = lambda sif:sxfroc(sif.close,sif.close5,sif.i_cof5,sfunc=xx_down)
sxroc10_b = lambda sif:sxfroc(sif.close,sif.close10,sif.i_cof10)
sxroc10_s = lambda sif:sxfroc(sif.close,sif.close10,sif.i_cof10,sfunc=xx_down)
sxroc15_b = lambda sif:sxfroc(sif.close,sif.close15,sif.i_cof15)
sxroc15_s = lambda sif:sxfroc(sif.close,sif.close15,sif.i_cof15,sfunc=xx_down)
sxroc30_b = lambda sif:sxfroc(sif.close,sif.close30,sif.i_cof30)    #奇异
sxroc30_s = lambda sif:sxfroc(sif.close,sif.close30,sif.i_cof30,sfunc=xx_down)
sxroc60_b = lambda sif:sxfroc(sif.close,sif.close60,sif.i_cof60)
sxroc60_s = lambda sif:sxfroc(sif.close,sif.close60,sif.i_cof60,sfunc=xx_down)

add_funcs(test_funcs,'sxroc')    #包括macd/ma

def sxfmfi(sclose,xhigh,xlow,xclose,xvol,sindics,length=14,slimit=400,sfunc=xx_up):
    xmfi = mfi((xhigh+xlow+xclose)/3,xvol,length)
    sx = sfunc(xmfi,cached_ints(len(xclose),slimit))
    signal = np.zeros_like(sclose)
    signal[sindics] = sx
    return signal

'''
多
>>> ev.evaluate2_b(i00,ev.sxmfi30_s(i00),60,end=1414,downlimit=80)  ####
((52, 276, -84, 11, 18), (19, -17, 856, -406), ([(-80, 17), (-80, 0), (-70, 1),
(-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20
, 0), (30, 1), (40, 0), (50, 2), (60, 1), (70, 0), (80, 1), (90, 6)],))
>>> ev.evaluate2_b(i00,ev.sxmfi30_b(i00,300),60,begin=944,end=1414,downlimit=90)
((65, 362, -95, 7, 13), (10, -13, 918, -558), ([(-90, 13), (-90, 0), (-80, 0), (
-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10
, 0), (20, 1), (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_b(i00,ev.sxmfi30_s(i00,200),60,begin=944,end=1414,downlimit=90)
((166, 297, -95, 4, 2), (4, -2, 820, -466), ([(-90, 2), (-90, 0), (-80, 0), (-70
, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0
), (20, 0), (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_b(i00,ev.sxmfi3_b(i00,800),60,begin=944,end=1414,downlimit=90) ####
((66, 218, -92, 29, 28), (38, -25, 1006, -562), ([(-90, 25), (-90, 1), (-80, 0),
 (-70, 0), (-60, 2), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (
10, 0), (20, 1), (30, 2), (40, 1), (50, 0), (60, 0), (70, 1), (80, 1), (90, 22)]
,))
>>> ev.evaluate2_b(i00,ev.sxmfi3_b(i00,900),60,begin=944,end=1414,downlimit=90) ####
((120, 243, -95, 7, 4), (10, -3, 918, -222), ([(-90, 4), (-90, 0), (-80, 0), (-7
0, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10,
0), (20, 0), (30, 0), (40, 1), (50, 1), (60, 0), (70, 0), (80, 1), (90, 4)],))


>>> ev.evaluate2_b(i00,ev.sxmfi5_s(i00,200),60,begin=944,end=1414,downlimit=90)
((25, 225, -89, 17, 30), (27, -27, 828, -780), ([(-90, 27), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 0), (-40, 0), (-30, 1), (-20, 1), (-10, 0), (0, 0), (1
0, 2), (20, 0), (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 14)],
>>> ev.evaluate2_b(i00,ev.sxmfi1_b(i00,850),60,begin=944,end=1414,downlimit=90) ####
((72, 254, -82, 34, 40), (54, -31, 926, -456), ([(-90, 31), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 2), (-40, 4), (-30, 2), (-20, 0), (-10, 0), (0, 1), (1
0, 0), (20, 1), (30, 3), (40, 0), (50, 0), (60, 0), (70, 2), (80, 1), (90, 26)],
))
>>> ev.evaluate2_b(i00,ev.sxmfi1_s(i00,850),60,begin=944,end=1414,downlimit=90) 
((68, 234, -89, 37, 39), (56, -35, 914, -460), ([(-90, 35), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 2), (-30, 2), (-20, 0), (-10, 0), (0, 3), (1
0, 1), (20, 0), (30, 1), (40, 0), (50, 3), (60, 0), (70, 1), (80, 1), (90, 27)],
>>> ev.evaluate2_b(i00,ev.sxmfi1_b(i00,800),60,begin=944,end=1414,downlimit=90)
((48, 238, -85, 77, 110), (119, -92, 988, -658), ([(-90, 92), (-90, 0), (-80, 0)
, (-70, 1), (-60, 3), (-50, 2), (-40, 3), (-30, 2), (-20, 5), (-10, 2), (0, 1),
(10, 0), (20, 5), (30, 3), (40, 3), (50, 1), (60, 2), (70, 2), (80, 4), (90, 56)
],))
>>> ev.evaluate2_b(i00,ev.sxmfi5_b(i00,800),60,begin=944,end=1414,downlimit=90) ####
((76, 227, -89, 25, 23), (33, -20, 894, -636), ([(-90, 21), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 1), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (1
0, 1), (20, 0), (30, 1), (40, 0), (50, 0), (60, 2), (70, 0), (80, 1), (90, 20)],
))
>>> ev.evaluate2_b(i00,ev.sxmfi5_s(i00,800),60,begin=944,end=1414,downlimit=90)
((63, 210, -90, 24, 23), (29, -21, 498, -586), ([(-90, 21), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 1), (-30, 1), (-20, 0), (-10, 0), (0, 1), (1
0, 0), (20, 1), (30, 0), (40, 1), (50, 0), (60, 1), (70, 0), (80, 0), (90, 20)],
))
>>> ev.evaluate2_b(i00,ev.sxmfi15_b(i00,600),60,begin=944,end=1414,downlimit=80)    ####

((72, 230, -78, 20, 21), (26, -18, 932, -450), ([(-80, 18), (-80, 0), (-70, 0),
(-60, 1), (-50, 0), (-40, 1), (-30, 0), (-20, 1), (-10, 0), (0, 1), (10, 1), (20
, 0), (30, 1), (40, 1), (50, 0), (60, 1), (70, 0), (80, 1), (90, 14)],))


空
>>> ev.evaluate2_s(i00,ev.sxmfi1_s(i00,200),60,begin=944,end=1414,uplimit=90)   ####
((48, 219, -86, 112, 142), (-120, 155, -806, 854), ([(-90, 122), (-90, 0), (-80,
 0), (-70, 1), (-60, 3), (-50, 3), (-40, 2), (-30, 3), (-20, 5), (-10, 3), (0, 1
), (10, 3), (20, 4), (30, 5), (40, 4), (50, 1), (60, 6), (70, 1), (80, 3), (90,
84)],))
>>>ev.evaluate2_s(i00,ev.sxmfi1_b(i00,200),60,begin=944,end=1414,uplimit=90)
((45, 211, -89, 114, 142), (-126, 162, -802, 860), ([(-90, 127), (-90, 0), (-80,
 2), (-70, 0), (-60, 1), (-50, 1), (-40, 1), (-30, 4), (-20, 3), (-10, 3), (0, 3
), (10, 4), (20, 6), (30, 3), (40, 4), (50, 6), (60, 3), (70, 0), (80, 1), (90,
84)],))
>>> ev.evaluate2_s(i00,ev.sxmfi3_b(i00,200),60,begin=944,end=1414,uplimit=90)   ###
((47, 215, -91, 37, 45), (-41, 54, -800, 856), ([(-90, 41), (-90, 0), (-80, 1),
(-70, 0), (-60, 0), (-50, 0), (-40, 2), (-30, 0), (-20, 1), (-10, 0), (0, 2), (1
0, 3), (20, 2), (30, 0), (40, 2), (50, 0), (60, 2), (70, 1), (80, 2), (90, 23)],
))
>>> ev.evaluate2_s(i00,ev.sxmfi5_s(i00,200),60,begin=944,end=1414,uplimit=90)   ####
((63, 294, -93, 19, 28), (-27, 27, -828, 780), ([(-90, 27), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (1
0, 0), (20, 1), (30, 0), (40, 2), (50, 0), (60, 0), (70, 0), (80, 0), (90, 16)],
))
>>> ev.evaluate2_s(i00,ev.sxmfi10_b(i00,200),60,begin=944,end=1414,uplimit=90)  ###
((156, 356, -78, 14, 12), (-9, 19, -604, 1076), ([(-90, 9), (-90, 0), (-80, 0),
(-70, 0), (-60, 0), (-50, 1), (-40, 0), (-30, 1), (-20, 0), (-10, 1), (0, 0), (1
0, 0), (20, 0), (30, 1), (40, 0), (50, 0), (60, 0), (70, 1), (80, 0), (90, 12)],
))
>>> ev.evaluate2_s(i00,ev.sxmfi10_s(i00,200),60,begin=944,end=1414,uplimit=90)  ###
((105, 282, -88, 12, 11), (-10, 12, -590, 880), ([(-90, 10), (-90, 0), (-80, 0),
 (-70, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (
10, 1), (20, 0), (30, 0), (40, 1), (50, 1), (60, 0), (70, 0), (80, 1), (90, 8)],
>>> ev.evaluate2_s(i00,ev.sxmfi15_s(i00,200),60,begin=944,end=1414,uplimit=90)  ###
((148, 419, -85, 6, 7), (-6, 8, -324, 664), ([(-90, 6), (-90, 0), (-80, 0), (-70
, 0), (-60, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0
), (20, 0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 6)],))






>>> ev.evaluate(i00,ev.sxmfi5_s(i00),10)
((-3, 49, -58, 129, 120), (26, 48, 460, 310))
>>> ev.evaluate(i00,ev.sxmfi5_b(i00),10)
((-3, 57, -54, 112, 133), (42, 43, 356, 458))
>>> ev.evaluate(i00,ev.sxmfi1_b(i00),10)
((-3, 56, -56, 581, 641), (199, 246, 508, 368))
>>> ev.evaluate(i00,ev.sxmfi1_s(i00),10)
((0, 56, -56, 607, 619), (205, 212, 684, 404))

>>> ev.evaluate(i00,ev.sxmfi3_b(i00),10)
((-8, 52, -57, 176, 216), (55, 76, 486, 384))
>>> ev.evaluate(i00,ev.sxmfi3_s(i00),10)
((-10, 47, -57, 180, 216), (48, 72, 224, 482))
>>> ev.evaluate(i00,ev.sxmfi10_s(i00),10)
((-1, 49, -62, 69, 56), (20, 23, 262, 366))
>>> ev.evaluate(i00,ev.sxmfi10_b(i00),10)
((-12, 54, -59, 54, 76), (17, 32, 566, 302))
>>> ev.evaluate(i00,ev.sxmfi15_b(i00),10)
((-22, 61, -60, 28, 63), (12, 19, 266, 366))
>>> ev.evaluate(i00,ev.sxmfi15_s(i00),10)
((2, 49, -49, 47, 43), (14, 13, 216, 238))
>>> ev.evaluate(i00,ev.sxmfi30_s(i00),10)
((-27, 48, -72, 15, 25), (6, 10, 176, 344))
>>> ev.evaluate(i00,ev.sxmfi30_b(i00),10)
((13, 70, -59, 25, 20), (9, 10, 466, 214))

'''
sxmfi1_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high,sif.low,sif.close,sif.vol,sif.i_cof,slimit=slimit)
sxmfi1_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high,sif.low,sif.close,sif.vol,sif.i_cof,sfunc=xx_down,slimit=slimit)

sxmfi5_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high5,sif.low5,sif.close5,sif.vol5,sif.i_cof5,slimit=slimit)
sxmfi5_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high5,sif.low5,sif.close5,sif.vol5,sif.i_cof5,sfunc=xx_down,slimit=slimit)

sxmfi3_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high3,sif.low3,sif.close3,sif.vol3,sif.i_cof3,slimit=slimit)
sxmfi3_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high3,sif.low3,sif.close3,sif.vol3,sif.i_cof3,slimit,sfunc=xx_down)

sxmfi10_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high10,sif.low10,sif.close10,sif.vol10,sif.i_cof10,slimit=slimit)
sxmfi10_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high10,sif.low10,sif.close10,sif.vol10,sif.i_cof10,sfunc=xx_down,slimit=slimit)

sxmfi15_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high15,sif.low15,sif.close15,sif.vol15,sif.i_cof15,slimit=slimit)
sxmfi15_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high15,sif.low15,sif.close15,sif.vol15,sif.i_cof15,sfunc=xx_down,slimit=slimit)

sxmfi30_b = lambda sif,slimit=400:sxfmfi(sif.close,sif.high30,sif.low30,sif.close30,sif.vol30,sif.i_cof30,slimit=slimit)
sxmfi30_s = lambda sif,slimit=400:sxfmfi(sif.close,sif.high30,sif.low30,sif.close30,sif.vol30,sif.i_cof30,sfunc=xx_down,slimit=slimit)

add_funcs(test_funcs,'sxmfi')    #包括macd/ma


def sxfxud_b(sclose,xhigh,xlow,xopen,xclose,sindics):
    mxc = xc0c(xopen,xclose,xhigh,xlow,13)>0
    signal = np.zeros_like(sclose)
    signal[sindics] = mxc
    return signal

def sxfxud_s(sclose,xhigh,xlow,xopen,xclose,sindics):
    mxc = xc0c(xopen,xclose,xhigh,xlow,13)<0
    signal = np.zeros_like(sclose)
    signal[sindics] = mxc
    return signal

'''
>>> ev.evaluate(i00,ev.sxxud1_b(i00),10)
((-4, 56, -59, 1391, 1526), (518, 571, 616, 436))
>>> ev.evaluate(i00,ev.sxxud1_s(i00),10)
((-4, 59, -58, 1348, 1565), (537, 554, 430, 490))
>>> ev.evaluate(i00,ev.sxxud3_b(i00),10)
((-3, 57, -56, 383, 439), (136, 141, 582, 408))
>>> ev.evaluate(i00,ev.sxxud3_s(i00),10)
((-1, 57, -56, 394, 427), (144, 155, 446, 512))
>>> ev.evaluate(i00,ev.sxxud5_b(i00),10)
((-8, 55, -54, 209, 282), (69, 89, 376, 496))
>>> ev.evaluate(i00,ev.sxxud5_s(i00),10)
((-2, 57, -54, 238, 265), (83, 87, 460, 344))
>>> ev.evaluate(i00,ev.sxxud10_b(i00),10)
((-5, 60, -57, 109, 138), (37, 46, 310, 496))
>>> ev.evaluate(i00,ev.sxxud10_s(i00),10)
((-1, 49, -53, 134, 125), (37, 38, 460, 264))
>>> ev.evaluate(i00,ev.sxxud15_b(i00),10)
((-11, 57, -57, 69, 101), (30, 35, 320, 382))
>>> ev.evaluate(i00,ev.sxxud15_s(i00),10)
((7, 52, -58, 105, 73), (29, 29, 356, 344))
>>> ev.evaluate(i00,ev.sxxud30_b(i00),10)
((9, 80, -44, 34, 46), (13, 9, 466, 170))
>>> ev.evaluate(i00,ev.sxxud30_s(i00),10)
((-9, 39, -60, 40, 38), (6, 15, 176, 282))

>>> ev.evaluate2_b(i00,ev.sxxud30_b(i00),60,begin=945,downlimit=80,end=1414)
((24, 195, -80, 19, 31), (30, -28, 610, -636), ([(-80, 28), (-80, 0), (-70, 0),
(-60, 1), (-50, 0), (-40, 0), (-30, 1), (-20, 1), (-10, 0), (0, 0), (10, 0), (20
, 0), (30, 2), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 16)],))


#添加sma30条件
多无
空
>>> ev.evaluate2_s(i00,ev.sxxud15_b(i00),60,uplimit=90,end=1414)
((23, 178, -92, 43, 58), (-51, 57, -1020, 554), ([(-90, 54), (-90, 0), (-80, 1),
 (-70, 1), (-60, 0), (-50, 0), (-40, 1), (-30, 1), (-20, 0), (-10, 0), (0, 0), (
10, 2), (20, 0), (30, 2), (40, 0), (50, 3), (60, 1), (70, 3), (80, 2), (90, 30)]
,))
>>> ev.evaluate2_s(i00,ev.sxxud10_s(i00),60,uplimit=90,end=1414)
((23, 147, -86, 61, 70), (-59, 76, -580, 654), ([(-90, 60), (-90, 0), (-80, 0),
(-70, 0), (-60, 1), (-50, 1), (-40, 2), (-30, 2), (-20, 3), (-10, 1), (0, 1), (1
0, 2), (20, 5), (30, 4), (40, 2), (50, 5), (60, 5), (70, 1), (80, 0), (90, 36)],
))
>>> ev.evaluate2_s(i00,ev.sxxud3_b(i00),60,uplimit=90,end=1414)
((25, 168, -87, 158, 202), (-173, 221, -1052, 872), ([(-90, 176), (-90, 0), (-80
, 1), (-70, 2), (-60, 2), (-50, 1), (-40, 5), (-30, 2), (-20, 5), (-10, 8), (0,
2), (10, 8), (20, 6), (30, 2), (40, 3), (50, 6), (60, 10), (70, 6), (80, 3), (90
, 112)],))
>>> ev.evaluate2_s(i00,ev.sxxud1_s(i00),60,uplimit=90,end=1414)
((23, 171, -87, 481, 652), (-551, 694, -936, 1084), ([(-90, 568), (-90, 1), (-80
, 2), (-70, 2), (-60, 8), (-50, 7), (-40, 14), (-30, 17), (-20, 11), (-10, 22),
(0, 19), (10, 28), (20, 25), (30, 26), (40, 21), (50, 19), (60, 26), (70, 20), (
80, 30), (90, 267)],))



>>> ev.evaluate(i00,ev.sxxud1_b(i00),10)
((-1, 64, -58, 646, 735), (295, 262, 616, 338))
>>> ev.evaluate(i00,ev.sxxud1_s(i00),10)
((-10, 50, -65, 675, 729), (218, 300, 364, 490))
>>> ev.evaluate(i00,ev.sxxud3_b(i00),10)
((-7, 58, -56, 190, 257), (77, 81, 582, 384))
>>> ev.evaluate(i00,ev.sxxud3_s(i00),10)
((-7, 51, -63, 172, 175), (54, 71, 428, 512))
>>> ev.evaluate(i00,ev.sxxud5_b(i00),10)
((-8, 57, -51, 114, 173), (39, 48, 376, 366))
>>> ev.evaluate(i00,ev.sxxud5_s(i00),10)
((-4, 56, -57, 113, 129), (39, 43, 406, 344))
>>> ev.evaluate(i00,ev.sxxud10_b(i00),10)
((3, 68, -47, 75, 96), (30, 28, 310, 370))
>>> ev.evaluate(i00,ev.sxxud10_s(i00),10)
((-6, 40, -52, 81, 78), (16, 25, 276, 264))
>>> ev.evaluate(i00,ev.sxxud15_b(i00),10)
((-9, 61, -55, 48, 74), (21, 25, 320, 382))
>>> ev.evaluate(i00,ev.sxxud15_s(i00),10)
((10, 51, -56, 84, 52), (20, 20, 356, 344))
>>> ev.evaluate(i00,ev.sxxud30_b(i00),10)
((9, 80, -45, 34, 45), (13, 9, 466, 170))
>>> ev.evaluate(i00,ev.sxxud30_s(i00),10)
((-9, 39, -60, 40, 38), (6, 15, 176, 282))



'''

sxxud1_b = lambda sif:sxfxud_b(sif.close,sif.high,sif.low,sif.open,sif.close,sif.i_cof)
sxxud1_s = lambda sif:sxfxud_s(sif.close,sif.high,sif.low,sif.open,sif.close,sif.i_cof)
sxxud3_b = lambda sif:sxfxud_b(sif.close,sif.high3,sif.low3,sif.open3,sif.close3,sif.i_cof3)
sxxud3_s = lambda sif:sxfxud_s(sif.close,sif.high3,sif.low3,sif.open3,sif.close3,sif.i_cof3)
sxxud5_b = lambda sif:sxfxud_b(sif.close,sif.high5,sif.low5,sif.open5,sif.close5,sif.i_cof5)
sxxud5_s = lambda sif:sxfxud_s(sif.close,sif.high5,sif.low5,sif.open5,sif.close5,sif.i_cof5)
sxxud10_b = lambda sif:sxfxud_b(sif.close,sif.high10,sif.low10,sif.open10,sif.close10,sif.i_cof10)
sxxud10_s = lambda sif:sxfxud_s(sif.close,sif.high10,sif.low10,sif.open10,sif.close10,sif.i_cof10)
sxxud15_b = lambda sif:sxfxud_b(sif.close,sif.high15,sif.low15,sif.open15,sif.close15,sif.i_cof15)
sxxud15_s = lambda sif:sxfxud_s(sif.close,sif.high15,sif.low15,sif.open15,sif.close15,sif.i_cof15)
sxxud30_b = lambda sif:sxfxud_b(sif.close,sif.high30,sif.low30,sif.open30,sif.close30,sif.i_cof30)
sxxud30_s = lambda sif:sxfxud_s(sif.close,sif.high30,sif.low30,sif.open30,sif.close30,sif.i_cof30)

add_funcs(test_funcs,'sxxud')    #包括macd/ma

###macd1的参数测试, 
macd1b_tests = []

macd1x_tests = []

def macd1bt(sif,ifast,islow,idiff):
    diff,dea = cmacd(sif.close * 10,ifast=ifast,islow=islow,idiff=idiff)
    signal = gand(cross(dea,diff)>0,strend2(diff)>0)
    return signal
    
for ishort in range(1,60,4):
    for ilong in range(1,270,8):
        for ie in range(1,30,6):
            macd1x_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd1bt,ifast=ishort,islow=ilong,idiff=ie)))

from wolfox.foxit.base.tutils import linelog
def tev_tests(sif,efunc,tests):
    results = []
    length = len(tests)
    for ix in range(len(tests)):
        name,tfunc = tests[ix][0],tests[ix][1]
        linelog(u'总%s个,第 %s 个, name=%s'% (length,ix,name))
        results.append((name,efunc(sif,signal=tfunc(sif))))
    return results


def macd1x(sif,ifast=17,islow=33,idiff=25):
    ''' 
        17-65-13
        9-49-7  #
        5-41-13 #
        29-153-19   #
        17-33-25
        57-257-13   #
        45-265-19
        57-105-13   #
        49-121-13
        37-129-19   #
        33-257-7    #
        33-177-7    #
        48-137-13   #
        57-161/153-7    ##
        21-250-13
        45-129-13   #
        5-233-7 #?#

                
    '''
    diff,dea = cmacd(sif.close * 10,ifast=ifast,islow=islow,idiff=idiff)
    signal = gand(cross(dea,diff)>0,strend2(diff)>0)
    signal = gand(signal
                ,sif.s30>0
                ,strend2(sif.ma30)>0
                ,sif.xatr<sif.mxatr
                ,strend2(sif.mxatr30x)<0
                )
    return signal
macd1x.direction = XBUY
macd1x.priority = 1500

def macd1xs(sif,ifast=17,islow=33,idiff=25):
    ''' 
    '''
    diff,dea = cmacd(sif.close * 10,ifast=ifast,islow=islow,idiff=idiff)
    signal = gand(cross(dea,diff)<0,strend2(diff)<0)
    signal = gand(signal
                #,sif.s15<0
                ,strend2(sif.ma30)<0
                ,strend2(sif.mxatr15x)<0
                ,sif.xatr15x>5000
                ,sif.ltrend<0
                )
    return signal * macd1xs.direction
macd1xs.direction = XSELL
macd1xs.priority = 1500

macd1xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd1xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd1xs,ifast=ishort,islow=ilong,idiff=ie)))

'''
results_t = ev.tev_tests(i00,evf_s,ev.macd1xs_tests)
ev.ev_output(results_t,'d:/temp/macd1xs_test.txt',evf_s)

        ,strend2(sif.ma30)<0
        ,strend2(sif.mxatr30x)<0
        ,sif.xatr30x>9000
        ,sif.ltrend<0
35-100/10
44-88/22
27-152/23   ##
59-104/6

'''
m1ts = fcustom(macd1xs,ifast=51,islow=148,idiff=18)




def macdn(sif,sclose,source,sindics,ifast=12,islow=26,idiff=9,xlimit=6000):
    ''' 
        变周期计算               
    '''
    diff,dea = cmacd(source * 10,ifast=ifast,islow=islow,idiff=idiff)
    xsignal = gand(cross(dea,diff)>0,strend2(diff)>0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma30)>0
                #,sif.xatr30x<sif.mxatr30x
                ,sif.xatr30x<xlimit
                #,strend2(sif.mxatr30x)<0
                )
    return signal
macdn.direction = XBUY
macdn.priority = 1500

def macdns(sif,sclose,source,sindics,ifast=12,islow=26,idiff=9,xlimit=6000):
    ''' 
        变周期计算               
    '''
    diff,dea = cmacd(source * 10,ifast=ifast,islow=islow,idiff=idiff)
    xsignal = gand(cross(dea,diff)<0,strend2(diff)<0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30<0
                #,sif.ltrend<0
                #,strend2(sif.ma30)<0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                ,sif.xatr<sif.mxatr
                #,sif.xatr30x > 7000
                #,sif.xatr>1000
                )
    return signal * macdns.direction
macdns.direction = XSELL
macdns.priority = 1500


def smacdn(sif,sclose,source,sindics,ifast=12,islow=26,idiff=9,xlimit=6000):
    ''' 
        变周期计算               
    '''
    diff,dea = cmacd(source * 10,ifast=ifast,islow=islow,idiff=idiff)
    xsignal = gand(strend2(diff-dea)==2)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma30)>0
                #,sif.xatr30x<sif.mxatr30x
                #,sif.xatr30x<xlimit
                #,strend2(sif.mxatr30x)<0
                )
    return signal
macdn.direction = XBUY
macdn.priority = 1500

smacdxb = lambda sif,ifast=12,islow=26,idiff=9:smacdn(sif,sif.close,sif.close,sif.i_cof,ifast,islow,idiff)
smacdxb.direction = XBUY
smacdxb.priority = 1500

smacdxb_tests = []
for ishort in range(1,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,4):
            smacdxb_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(smacdxb,ifast=ishort,islow=ilong,idiff=ie)))





macd3xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close3,sif.i_cof3,ifast,islow,idiff)
macd3xb.direction = XBUY
macd3xb.priority = 1500

macd3xb_tests = []
for ishort in range(1,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,4):
            macd3xb_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd3xb,ifast=ishort,islow=ilong,idiff=ie)))


macd3xs = lambda sif,ifast=12,islow=26,idiff=9:macdns(sif,sif.close,sif.close3,sif.i_cof3,ifast,islow,idiff)
macd3xs.direction = XSELL
macd3xs.priority = 1500

macd3xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd3xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd3xs,ifast=ishort,islow=ilong,idiff=ie)))

'''
evf_s = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90)
results_t = ev.tev_tests(i00,evf_s,ev.macd3xs_tests)
ev.ev_output(results_t,'d:/temp/macd3xs_test.txt',evf_s)

                ,sif.s30<0
                #,sif.ltrend<0
                ,strend2(sif.ma30)<0
                ,sif.xatr30x<sif.mxatr30x
                #,sif.xatr30x<xlimit
                ,strend2(sif.mxatr30x)<0
                ,sif.xatr30x<7000
43-88/22
51-76/26
35-100/26
55-90/18

                ,sif.ltrend<0
                ,strend2(sif.ma30)<0
                ,sif.xatr30x<sif.mxatr30x
                ,strend2(sif.mxatr30x)<0
                ,sif.xatr30x<7000
51-76/26
55-90/18
'''
m3ts = fcustom(macd3xs,ifast=35,islow=100,idiff=26)


macd5xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close5,sif.i_cof5,ifast,islow,idiff)
macd5xb.direction = XBUY
macd5xb.priority = 1500

macd5xb_tests = []
for ishort in range(1,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,3):
            macd5xb_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd5xb,ifast=ishort,islow=ilong,idiff=ie)))


macd5xs = lambda sif,ifast=12,islow=26,idiff=9:macdns(sif,sif.close,sif.close5,sif.i_cof5,ifast,islow,idiff)
macd5xs.direction = XSELL
macd5xs.priority = 1500

macd5xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd5xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd5xs,ifast=ishort,islow=ilong,idiff=ie)))


'''
evf_s = fcustom(ev.evaluate2_s,interval=60,begin=944,end=1414,uplimit=90)
results_t = ev.tev_tests(i00,evf_s,ev.macd5xs_tests)
ev.ev_output(results_t,'d:/temp/macd5xs_test.txt',evf_s)

                ,sif.ltrend<0
                ,sif.xatr30x<sif.mxatr30x
                ,sif.xatr<sif.mxatr

31-78/18
                ,sif.ltrend<0
                ,strend2(sif.ma30)<0
                ,sif.xatr30x<sif.mxatr30x
                ,strend2(sif.mxatr30x)<0
                ,sif.xatr>sif.mxatr
27-128/18
43-120/10
35-132/14
'''
m5ts = fcustom(macd5xs,ifast=59,islow=96,idiff=6)


macd10xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close10,sif.i_cof10,ifast,islow,idiff)
macd10xb.direction = XBUY
macd10xb.priority = 1500

macd10xb_tests = []
for ishort in range(1,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,3):
            macd10xb_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd10xb,ifast=ishort,islow=ilong,idiff=ie)))


macd10xs = lambda sif,ifast=12,islow=26,idiff=9:macdns(sif,sif.close,sif.close10,sif.i_cof10,ifast,islow,idiff)
macd10xs.direction = XBUY
macd10xs.priority = 1500

macd10xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd10xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd10xs,ifast=ishort,islow=ilong,idiff=ie)))

m10ts = fcustom(macd10xs,ifast=59,islow=160,idiff=10)
'''
results_t = ev.tev_tests(i00,evf_s,ev.macd10xs_tests)
ev.ev_output(results_t,'d:/temp/macd10xs_test.txt',evf_s)

                ,sif.ltrend<0
                ,strend2(sif.mxatr30x)<0
59-224/6
                ,sif.s30<0
                ,strend2(sif.ma30)<0
                ,sif.xatr<sif.mxatr
27-184/22


results_t = ev.tev_tests(i00,evf_s,ev.macd15xs_tests)
ev.ev_output(results_t,'d:/temp/macd15xs_test.txt',evf_s)
results_t = ev.tev_tests(i00,evf_s,ev.macd30xs_tests)
ev.ev_output(results_t,'d:/temp/macd30xs_test.txt',evf_s)

'''



macd15xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close15,sif.i_cof15,ifast,islow,idiff)
macd15xb.direction = XBUY
macd15xb.priority = 1500

macd15xb_tests = []
for ishort in range(5,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,3):
            macd15xb_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd15xb,ifast=ishort,islow=ilong,idiff=ie)))


macd15xs = lambda sif,ifast=12,islow=26,idiff=9:macdns(sif,sif.close,sif.close15,sif.i_cof15,ifast,islow,idiff)
macd15xs.direction = XSELL
macd15xs.priority = 1500

macd15xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd15xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd15xs,ifast=ishort,islow=ilong,idiff=ie)))


m15ts = fcustom(macd15xs,ifast=27,islow=152,idiff=6)
'''
           ,sif.xatr30x > 6000
59-160/10
55-266/26
'''


'''
                ,sif.xatr<sif.mxatr
47-94/10
'''

macd30xb = lambda sif,ifast=12,islow=26,idiff=9,xlimit=6000:macdn(sif,sif.close,sif.close30,sif.i_cof30,ifast,islow,idiff,xlimit)
macd30xb.direction = XBUY
macd30xb.priority = 1500


macd30xb_tests = []
for ishort in range(5,60,4):
    for ilong in range(ishort*3/2,270,8):
        for ie in range(6,30,3):
            for xlimit in range(5000,10000,1000):
                macd30xb_tests.append(('%s-%s/%s-%s'%(ishort,ilong,ie,xlimit),fcustom(macd30xb,ifast=ishort,islow=ilong,idiff=ie,xlimit=xlimit)))


macd30xs = lambda sif,ifast=12,islow=26,idiff=9:macdns(sif,sif.close,sif.close30,sif.i_cof30,ifast,islow,idiff)
macd30xs.direction = XSELL
macd30xs.priority = 1500

m30ts = fcustom(macd30xs,ifast=47,islow=94,idiff=10)


macd30xs_tests = []
for ishort in range(3,60,4):
    for ilong in range(ishort*3/2,270,8):
        mie = min(30,ishort*3/2)
        for ie in range(6,mie,4):
            macd30xs_tests.append(('%s-%s/%s'%(ishort,ilong,ie),fcustom(macd30xs,ifast=ishort,islow=ilong,idiff=ie)))


macd45xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close45,sif.i_cof45,ifast,islow,idiff)
macd45xb.direction = XBUY
macd45xb.priority = 1500

macd60xb = lambda sif,ifast=12,islow=26,idiff=9:macdn(sif,sif.close,sif.close60,sif.i_cof60,ifast,islow,idiff)
macd60xb.direction = XBUY
macd60xb.priority = 1500

'''
macd1xs:

macd3:
                ,sif.s30>0
                ,strend2(sif.ma30)>0)

33/29-89/25
37-73/25
53-113/25,57-105/25
21-153/25
19-153/19
29-145/19
33-105/19
41-81/19
41-121/13

macd3X2:
                ,sif.s30>0
                ,strend2(sif.ma30)>0
                ,sif.xatr3x<2500
45-155/21
57-133/18
49-73/18
45-83/15/17
49-97/27
37-87/21
33-73/24
29-139/18
25-141/21
21-129/27
41-85/18    #
37-95/21
29-75/27
'''
m3t = fcustom(macd3xb,ifast=49,islow=121,idiff=9)


'''
macd5b:
                ,sif.s30>0
                ,sif.xatr30x<sif.mxatr30x
37-191/27
45-219/27
37-87/12
29-59/21
'''
m5t = fcustom(macd5xb,ifast=29,islow=235,idiff=9)

'''
                ,sif.s30>0
                ,sif.xatr30x<sif.mxatr30x

21-87-15
25-101-6    #
17-41-6
17-121-12
21-39-12
37-79-6
12-183-6
29-163-6
13-171-9    #

                ,sif.s30>0
                ,sif.xatr30x>sif.mxatr30x
                ,sif.xatr30x<7000

41-261-24
57-109-27
'''
m10t = fcustom(macd10xb,ifast=57,islow=229,idiff=18)


'''
                ,sif.s30>0
                ,sif.xatr30x<sif.mxatr30x
17-81-9
25-53-9
21-71-6
13-67-12
13-35-12
13-75-18
9-12-6
'''
m15t = fcustom(macd15xb,ifast=17,islow=97,idiff=6)


'''
                ,sif.xatr30x<xlimit

33-177-24-8000
'''
m30t = fcustom(macd30xb,ifast=45,islow=227,idiff=21,xlimit=8000)

'''    
evf_b = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90)
evf_s = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90)
results_b = ev.tev_tests(i00,evf_b,ev.macd1b_tests)
results_s = ev.tev_tests(i00,evf_s,ev.macd1s_tests)
ev.ev_output(results_b,'d:/temp/macd1bt_test.txt',evf_b)
ev.ev_output(results_s,'d:/temp/macd1st_test.txt',evf_s)

ufilter30 = strend2(i00.ma30)>0
evf_b_s13_30 = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90,filter=ufilter13_30)
results_b = ev.tev_tests(i00,evf_b_s13_30,ev.macd1b_tests)
ev.ev_output(results_b,'d:/temp/macd1bts_test.txt',evf_b_s13_30)

results_t = ev.tev_tests(i00,evf_b,ev.macd1x_tests)
ev.ev_output(results_t,'d:/temp/macd1xb_test.txt',evf_b)

results_t = ev.tev_tests(i00,evf_b,ev.macd3xb_tests)
ev.ev_output(results_t,'d:/temp/macd3xb_test.txt',evf_b)

results_t = ev.tev_tests(i00,evf_b,ev.macd5xb_tests)
ev.ev_output(results_t,'d:/temp/macd5xb_test.txt',evf_b)

results_t = ev.tev_tests(i00,evf_b,ev.macd10xb_tests)
ev.ev_output(results_t,'d:/temp/macd10xb_test.txt',evf_b)

results_t = ev.tev_tests(i00,evf_b,ev.macd15xb_tests)
ev.ev_output(results_t,'d:/temp/macd15xb_test.txt',evf_b)

results_t = ev.tev_tests(i00,evf_b,ev.macd30xb_tests)
ev.ev_output(results_t,'d:/temp/macd30xb_test.txt',evf_b)
'''

##测试ma
def xmanb(sif,sclose,source,sindics,length=20,xlen=1):
    ''' 
        变周期计算               
    '''
    lma = ma(source,length)
    xsignal = equals(strend2(lma),xlen)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                ,strend2(sif.ma30)>0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                #,sif.ltrend>0
                #,sif.xatr<sif.mxatr
                ,sif.xatr30x<8000
                #,sif.s10>0
                )
    return signal
xmanb.direction = XBUY
xmanb.priority = 1500

def xmans(sif,sclose,source,sindics,length=20,xlen=1):
    ''' 
        变周期计算               
    '''
    lma = ma(source,length)
    xsignal = equals(strend2(lma), -xlen)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30<0
                #,sif.ltrend<0
                #,strend2(sif.ma30)<0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x < 6000
                #,sif.xatr<1000
                )
    return signal * xmans.direction
xmans.direction = XSELL
xmans.priority = 1500

xmaxb = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close,sif.i_cof,length,xlen)
xmaxb.direction = XBUY
xmaxb.priority = 1500

xmaxb_tests = []
for ilength in range(3,600,2):
    xmaxb_tests.append(('%s'%(ilength),fcustom(xmaxb,length=ilength)))


xman1b = fcustom(xmaxb,length=500,xlen=3)
'''
                ,strend2(sif.ma30)>0
                ,sif.xatr30x<sif.mxatr30x
                ,sif.ltrend>0
                ,sif.xatr<sif.mxatr
280,xlen=3
                ,strend2(sif.ma30)>0
                ,sif.xatr30x<sif.mxatr30x
                ,sif.xatr<sif.mxatr
                ,sif.xatr30x<6000
253,1
                ,strend2(sif.ma30)>0
                ,sif.xatr30x<8000
500,3

'''
xmaxs = lambda sif,length=20,xlen=3:xmans(sif,sif.close,sif.close,sif.i_cof,length,xlen)
xmaxs.direction = XSELL
xmaxs.priority = 1500

xmaxs_tests = []
for ilength in range(3,600,2):
    xmaxs_tests.append(('%s'%(ilength),fcustom(xmaxs,length=ilength)))


xman1s = fcustom(xmaxs,length=180,xlen=23)
'''
                ,strend2(sif.mxatr30x)<0
                ,sif.xatr30x > 7000
440,7
60,9
40,9
'''



xmax3b = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close3,sif.i_cof3,length,xlen)
xmax3b.direction = XBUY
xmax3b.priority = 1500

xmax3b_tests = []
for ilength in range(3,300,2):
    xmax3b_tests.append(('%s'%(ilength),fcustom(xmax3b,length=ilength)))

xman3b = fcustom(xmax3b,length=150,xlen=3)
'''
                ,sif.xatr<sif.mxatr
                ,sif.xatr30x<7000
253,3
                ,strend2(sif.ma30)>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr30x<6000
80,5
60,5
'''
xmax3s = lambda sif,length=20,xlen=3:xmans(sif,sif.close,sif.close3,sif.i_cof3,length,xlen)
xmax3s.direction = XSELL
xmax3s.priority = 1500

xmax3s_tests = []
for ilength in range(3,600,2):
    xmax3s_tests.append(('%s'%(ilength),fcustom(xmax3s,length=ilength)))


xman3s = fcustom(xmax3s,length=140,xlen=3)
'''
540,1
210,3

                ,sif.xatr>sif.mxatr
                ,sif.xatr30x < 6000
140,5
                ,sif.ltrend<0
                ,sif.xatr>sif.mxatr
                ,sif.xatr30x < 6000
                ,sif.xatr<1000
45,5
90,3
'''



xmax5b = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close5,sif.i_cof5,length,xlen)
xmax5b.direction = XBUY
xmax5b.priority = 1500

xmax5b_tests = []
for ilength in range(3,300,2):
    xmax5b_tests.append(('%s'%(ilength),fcustom(xmax5b,length=ilength)))

xman5b = fcustom(xmax5b,length=30,xlen=5)
'''
                ,sif.xatr30x<8000
137,5
'''
xmax5s = lambda sif,length=20,xlen=3:xmans(sif,sif.close,sif.close5,sif.i_cof5,length,xlen)
xmax5s.direction = XSELL
xmax5s.priority = 1500

xmax5s_tests = []
for ilength in range(3,600,2):
    xmax5s_tests.append(('%s'%(ilength),fcustom(xmax5s,length=ilength)))


xman5s = fcustom(xmax5s,length=200,xlen=1)
'''
327,3
569,3
                ,strend2(sif.ma30)<0
                ,sif.xatr30x < 6000
120,3
30,11
200,1
'''



xmax10b = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close10,sif.i_cof10,length,xlen)
xmax10b.direction = XBUY
xmax10b.priority = 1500

xmax10b_tests = []
for ilength in range(3,300,2):
    xmax10b_tests.append(('%s'%(ilength),fcustom(xmax10b,length=ilength)))

xman10b = fcustom(xmax10b,length=140,xlen=5)
'''
                ,sif.xatr30x<8000
273,5
71,3
50,5
'''

xmax10s = lambda sif,length=20,xlen=3:xmans(sif,sif.close,sif.close10,sif.i_cof10,length,xlen)
xmax10s.direction = XSELL
xmax10s.priority = 1500

xmax10s_tests = []
for ilength in range(3,600,2):
    xmax10s_tests.append(('%s'%(ilength),fcustom(xmax10s,length=ilength)))


xman10s = fcustom(xmax10s,length=100,xlen=3)
'''
无
'''


xmax15b = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close15,sif.i_cof15,length,xlen)
xmax15b.direction = XBUY
xmax15b.priority = 1500

xmax15b_tests = []
for ilength in range(3,300,2):
    xmax15b_tests.append(('%s'%(ilength),fcustom(xmax15b,length=ilength)))

xman15b = fcustom(xmax15b,length=23,xlen=3)
'''
                ,sif.xatr30x<8000
243,3
45,3
'''

xmax15s = lambda sif,length=20,xlen=3:xmans(sif,sif.close,sif.close15,sif.i_cof15,length,xlen)
xmax15s.direction = XSELL
xmax15s.priority = 1500

xmax15s_tests = []
for ilength in range(3,600,2):
    xmax15s_tests.append(('%s'%(ilength),fcustom(xmax15s,length=ilength)))


xman15s = fcustom(xmax15s,length=250,xlen=3)
'''
300,1
200,1
                ,sif.ltrend<0
                ,sif.xatr<sif.mxatr

25,1
                ,sif.s30<0
                ,strend2(sif.ma30)<0
40,1
67,1
'''



xmax30b = lambda sif,length=20,xlen=3:xmanb(sif,sif.close,sif.close30,sif.i_cof30,length,xlen)
xmax30b.direction = XBUY
xmax30b.priority = 1500

xmax30b_tests = []
for ilength in range(3,300,2):
    xmax30b_tests.append(('%s'%(ilength),fcustom(xmax30b,length=ilength)))

xman30b = fcustom(xmax30b,length=100,xlen=3)
'''
                ,sif.xatr30x<8000
120,3
'''

xmax30s = lambda sif,length=20,xlen=1:xmans(sif,sif.close,sif.close30,sif.i_cof30,length,xlen)
xmax30s.direction = XSELL
xmax30s.priority = 1500

xmax30s_tests = []
for ilength in range(3,600,2):
    xmax30s_tests.append(('%s'%(ilength),fcustom(xmax30s,length=ilength)))


xman30s = fcustom(xmax30s,length=200,xlen=1)
'''
101,1
75,1
                ,strend2(sif.ma30)<0
                ,sif.xatr<sif.mxatr
15,1

'''

##测试收盘上ma
def xman2b(sif,sclose,source,sindics,length=20):
    ''' 
        变周期计算               
    '''
    lma = ma(source,length)
    xsignal = gand(cross(lma,source)>0,strend(lma)>0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma13)>0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)>0
                #,sif.mtrend>0
                #,sif.ltrend>0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x>8000
                #,sif.xatr<1000
                #,strend2(sif.diff1-sif.dea1)>0
                #,sif.s15>0
                
                )
    return signal
xman2b.direction = XBUY
xman2b.priority = 1500

def xman2s(sif,sclose,source,sindics,length=20,xlen=1):
    ''' 
        变周期计算               
    '''
    lma = ma(source,length)
    xsignal = gand(cross(lma,source)<0,strend(lma)<0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30<0
                #,sif.ltrend<0
                #,strend2(sif.ma30)<0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x < 6000
                #,sif.xatr<1000
                )
    return signal * xmans.direction
xman2s.direction = XSELL
xman2s.priority = 1500

xma2xb = lambda sif,length=20:xman2b(sif,sif.close,sif.close,sif.i_cof,length)
xma2xb.direction = XBUY
xma2xb.priority = 1500

xma2xb_tests = []
for ilength in range(3,600,2):
    xma2xb_tests.append(('%s'%(ilength),fcustom(xma2xb,length=ilength)))


xma2n1b = fcustom(xma2xb,length=200) 
'''
                ,sif.xatr30x<8000
                ,sif.xatr>1000
                #,strend2(sif.diff1-sif.dea1)>0
                ,sif.s15>0
240
            ,sif.xatr30x<sif.mxatr30x
            ,sif.ltrend>0
            ,sif.xatr>sif.mxatr
            ,sif.xatr30x<8000
480
                ,strend2(sif.ma13)>0
                ,strend2(sif.mxatr30x)>0
                ,sif.mtrend>0
                ,sif.xatr30x<8000
                ,sif.xatr>600

50
                ,sif.mtrend>0
                ,sif.ltrend>0
                ,sif.xatr>800
                ,strend2(sif.diff1-sif.dea1)>0
30
                ,sif.s30>0
                ,strend2(sif.ma13)>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr<1000
                ,sif.s10>0
10
                ,strend2(sif.mxatr30x)>0
                ,sif.mtrend>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr<1000
                ,sif.s15>0
15
'''



xma2xs = lambda sif,length=20:xma2ns(sif,sif.close,sif.close,sif.i_cof,length)
xma2xs.direction = XSELL
xma2xs.priority = 1500

xma2xs_tests = []
for ilength in range(3,600,2):
    xma2xs_tests.append(('%s'%(ilength),fcustom(xma2xs,length=ilength)))


xman21s = fcustom(xma2xs,length=180)


xma2x3b = lambda sif,length=20:xman2b(sif,sif.close,sif.close3,sif.i_cof3,length)
xma2x3b.direction = XBUY
xma2x3b.priority = 1500

xma2x3b_tests = []
for ilength in range(3,600,2):
    xma2x3b_tests.append(('%s'%(ilength),fcustom(xma2x3b,length=ilength)))


xma2n3b = fcustom(xma2x3b,length=90) 
'''
            ,strend2(sif.ma13)>0
360
            ,sif.xatr30x<sif.mxatr30x
430
                ,sif.xatr30x<8000
                ,sif.s15>0
210
'''

xma2x5b = lambda sif,length=20:xman2b(sif,sif.close,sif.close5,sif.i_cof5,length)
xma2x5b.direction = XBUY
xma2x5b.priority = 1500

xma2x5b_tests = []
for ilength in range(3,600,2):
    xma2x5b_tests.append(('%s'%(ilength),fcustom(xma2x5b,length=ilength)))


xma2n5b = fcustom(xma2x5b,length=200) 
'''
200
                ,sif.xatr<sif.mxatr
                ,sif.s15>0
90
'''

xma2x10b = lambda sif,length=20:xman2b(sif,sif.close,sif.close10,sif.i_cof10,length)
xma2x10b.direction = XBUY
xma2x10b.priority = 1500

xma2x10b_tests = []
for ilength in range(3,600,2):
    xma2x10b_tests.append(('%s'%(ilength),fcustom(xma2x10b,length=ilength)))


xma2n10b = fcustom(xma2x10b,length=300) 
'''
100
'''

xma2x15b = lambda sif,length=20:xman2b(sif,sif.close,sif.close15,sif.i_cof15,length)
xma2x15b.direction = XBUY
xma2x15b.priority = 1500

xma2x15b_tests = []
for ilength in range(3,600,2):
    xma2x15b_tests.append(('%s'%(ilength),fcustom(xma2x15b,length=ilength)))


xma2n15b = fcustom(xma2x15b,length=20) 
'''
67
'''


xma2x30b = lambda sif,length=20:xman2b(sif,sif.close,sif.close15,sif.i_cof15,length)
xma2x30b.direction = XBUY
xma2x30b.priority = 1500
xma2n30b = fcustom(xma2x30b,length=100) 


#双线交叉
def x2mab(sif,sclose,source,sindics,len1=3,len2=20):
    ''' 
        变周期计算               
    '''
    lma1 = ma(source,len1)
    lma2 = ma(source,len2)    
    xsignal = gand(cross(lma2,lma1)>0,strend(lma1)>0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma13)>0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)>0
                #,sif.mtrend>0
                #,sif.ltrend>0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x<8000
                #,sif.xatr<1200
                #,strend2(sif.diff1-sif.dea1)>0
                #,sif.s15>0
                
                )
    return signal
x2mab.direction = XBUY
x2mab.priority = 1500

def x2mas(sif,sclose,source,sindics,len1=3,len2=20):
    ''' 
        变周期计算               
    '''
    lma1 = ma(source,len1)
    lma2 = ma(source,len2)    
    xsignal = gand(cross(lma2,lma1)<0,strend(lma1)<0)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30<0
                #,sif.ltrend<0
                #,strend2(sif.ma30)<0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x < 6000
                #,sif.xatr<1000
                #,sif.s15<0
                )
    return signal * xmans.direction
x2mas.direction = XSELL
x2mas.priority = 1500

x2ma1b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close,sif.i_cof,len1,len2)
x2ma1b.direction = XBUY
x2ma1b.priority = 1500

x2ma1b_tests = []
for ilen1 in range(3,300,4):
    for ilen2 in range(3,500,7):
        x2ma1b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma1b,len1=ilen1,len2=ilen2)))


x2mab1 = fcustom(x2ma1b,len1=23,len2=288) 
'''
95-493

'''
x2ma1s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close,sif.i_cof,len1,len2)
x2ma1s.direction = XSELL
x2ma1s.priority = 1500

x2ma1s_tests = []
for ilen1 in range(3,300,4):
    for ilen2 in range(ilen1,500,7):
        x2ma1s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma1s,len1=ilen1,len2=ilen2)))


x2mas1 = fcustom(x2ma1s,len1=143,len2=437) 



x2ma3b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close3,sif.i_cof3,len1,len2)
x2ma3b.direction = XBUY
x2ma3b.priority = 1500

x2ma3b_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(3,200,7):
        x2ma3b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma3b,len1=ilen1,len2=ilen2)))


x2mab3 = fcustom(x2ma3b,len1=9,len2=33) 
'''
99-192
49-199
11-192
7-199
                ,sif.xatr30x<sif.mxatr30x
                ,sif.s15>0
87-178
                ,sif.s30>0
                ,sif.xatr30x<8000
                ,sif.xatr<1200
27-185
                ,sif.xatr30x<sif.mxatr30x
                ,sif.xatr<sif.mxatr
                ,sif.s15>0
11-33
'''
x2ma3s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close3,sif.i_cof3,len1,len2)
x2ma3s.direction = XSELL
x2ma3s.priority = 1500

x2ma3s_tests = []
for ilen1 in range(3,300,4):
    for ilen2 in range(ilen1,300,7):
        x2ma3s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma3s,len1=ilen1,len2=ilen2)))


x2mas3 = fcustom(x2ma3s,len1=27,len2=185) 
'''
115-220
71-259
                ,sif.xatr30x<sif.mxatr30x
                ,sif.xatr<sif.mxatr
11-158
                ,sif.xatr<sif.mxatr
7-175

'''


x2ma5b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close5,sif.i_cof5,len1,len2)
x2ma5b.direction = XBUY
x2ma5b.priority = 1500

x2ma5b_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma5b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma5b,len1=ilen1,len2=ilen2)))


x2mab5 = fcustom(x2ma5b,len1=71,len2=171) 
'''
43-171
47-94
7-122
11-143
'''

x2ma5s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close5,sif.i_cof5,len1,len2)
x2ma5s.direction = XSELL
x2ma5s.priority = 1500

x2ma5s_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,300,7):
        x2ma5s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma5s,len1=ilen1,len2=ilen2)))


x2mas5 = fcustom(x2ma5s,len1=11,len2=33) 
'''
59-283
63-287
59-255
83-202
103-250
7-143
                ,sif.xatr30x<sif.mxatr30x
                ,sif.xatr30x < 6000
7-84


'''



x2ma10b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close10,sif.i_cof10,len1,len2)
x2ma10b.direction = XBUY
x2ma10b.priority = 1500

x2ma10b_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma10b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma10b,len1=ilen1,len2=ilen2)))


x2mab10 = fcustom(x2ma10b,len1=3,len2=59) 
'''
19-173
3-59    ###
3-185
'''

x2ma10s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close10,sif.i_cof10,len1,len2)
x2ma10s.direction = XSELL
x2ma10s.priority = 1500

x2ma10s_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma10s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma10s,len1=ilen1,len2=ilen2)))


x2mas10 = fcustom(x2ma10s,len1=15,len2=57) 
'''
31-143  ##
31-150  ##

                ,sif.xatr<sif.mxatr
3-45/52
11-81
7-70
                ,sif.xatr>sif.mxatr
11-67
'''

x2ma15b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close15,sif.i_cof15,len1,len2)
x2ma15b.direction = XBUY
x2ma15b.priority = 1500

x2ma15b_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma15b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma15b,len1=ilen1,len2=ilen2)))


x2mab15 = fcustom(x2ma15b,len1=3,len2=150) 
'''
11-109
'''

x2ma15s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close15,sif.i_cof15,len1,len2)
x2ma15s.direction = XSELL
x2ma15s.priority = 1500

x2ma15s_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma15s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma15s,len1=ilen1,len2=ilen2)))


x2mas15 = fcustom(x2ma15s,len1=7,len2=56) 
'''
59-178
55-174
47-166
99-155
35-91
23-44
19-47   ###

                ,sif.xatr<sif.mxatr
3-31
'''


x2ma30b = lambda sif,len1=3,len2=20:x2mab(sif,sif.close,sif.close30,sif.i_cof30,len1,len2)
x2ma30b.direction = XBUY
x2ma30b.priority = 1500

x2ma30b_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma30b_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma30b,len1=ilen1,len2=ilen2)))


x2mab30 = fcustom(x2ma30b,len1=11,len2=151) 
'''
7-77
11-144
'''

x2ma30s = lambda sif,len1=3,len2=20:x2mas(sif,sif.close,sif.close30,sif.i_cof30,len1,len2)
x2ma30s.direction = XSELL
x2ma30s.priority = 1500

x2ma30s_tests = []
for ilen1 in range(3,200,4):
    for ilen2 in range(ilen1,200,7):
        x2ma30s_tests.append(('%s-%s'%(ilen1,ilen2),fcustom(x2ma30s,len1=ilen1,len2=ilen2)))


x2mas30 = fcustom(x2ma30s,len1=11,len2=25) 
'''
11-123  ##
11-25   ##
15-120  ##
7-182
7-63
3-199
'''

'''
evf_b = fcustom(ev.evaluate3_b,interval=60,begin=944,end=1414,downlimit=90)
evf_s = fcustom(ev.evaluate3_s,interval=60,begin=944,end=1414,uplimit=90)

results_t = ev.tev_tests(i00,evf_b,ev.xmaxb_tests)
ev.ev_output(results_t,'d:/temp/xmaxb_test.txt',evf_b)



'''

#svama close>ma
def svxb(sif,sclose,svap,v2i,vlen,sindics,len1=20):
    ''' 
        svama计算               
    '''

    svma1 = ma(svap,len1)
    xvap = gand(cross(svma1,svap)>0,strend(svma1)>0)
    xsignal = transform(xvap,v2i,vlen)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma13)>0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)>0
                #,sif.mtrend>0
                #,sif.ltrend>0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x<8000
                #,sif.xatr<1200
                #,strend2(sif.diff1-sif.dea1)>0
                #,sif.s15>0
                )
    return signal
svxb.direction = XBUY
svxb.priority = 1500

def svxs(sif,sclose,svap,v2i,vlen,sindics,len1=20):
    ''' 
        svama计算               
    '''
    svma1 = ma(svap,len1)
    xvap = gand(cross(svma1,svap)<0,strend(svma1)<0)
    xsignal = transform(xvap,v2i,vlen)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30<0
                #,sif.ltrend<0
                #,strend2(sif.ma30)<0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)<0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x < 6000
                #,sif.xatr<1000
                #,sif.s15<0
                )
    return signal * svxs.direction
svxs.direction = XSELL
svxs.priority = 1500

svxb1 = lambda sif,len1=20:svxb(sif,sif.close,sif.svap1,sif.v2i1,len(sif.vol),sif.i_cof,len1)
svxb1.direction = XBUY
svxb1.priority = 1500

svxb1_tests = []
for ilen1 in range(3,300,2):
    svxb1_tests.append(('%s'%(ilen1,),fcustom(svxb1,len1=ilen1)))


svxb3 = lambda sif,len1=20:svxb(sif,sif.close,sif.svap3,sif.v2i3,len(sif.vol3),sif.i_cof3,len1)
svxb3.direction = XBUY
svxb3.priority = 1500

svxb3_tests = []
for ilen1 in range(3,300,2):
    svxb3_tests.append(('%s'%(ilen1,),fcustom(svxb3,len1=ilen1)))

svxb10 = lambda sif,len1=20:svxb(sif,sif.close,sif.svap10,sif.v2i10,len(sif.vol10),sif.i_cof10,len1)
svxb10.direction = XBUY
svxb10.priority = 1500

svxb10_tests = []
for ilen1 in range(3,300,2):
    svxb10_tests.append(('%s'%(ilen1,),fcustom(svxb10,len1=ilen1)))


svxb15 = lambda sif,len1=20:svxb(sif,sif.close,sif.svap15,sif.v2i15,len(sif.vol15),sif.i_cof15,len1)
svxb15.direction = XBUY
svxb15.priority = 1500

svxb15_tests = []
for ilen1 in range(3,300,2):
    svxb15_tests.append(('%s'%(ilen1,),fcustom(svxb15,len1=ilen1)))


svxb30 = lambda sif,len1=20:svxb(sif,sif.close,sif.svap30,sif.v2i30,len(sif.vol30),sif.i_cof30,len1)
svxb30.direction = XBUY
svxb30.priority = 1500

svxs30 = lambda sif,len1=20:svxs(sif,sif.close,sif.svap30,sif.v2i30,len(sif.vol30),sif.i_cof30,len1)
svxs30.direction = XSELL
svxs30.priority = 1500


svxb1e = fcustom(svxb1,len1=99) 
svxb3e = fcustom(svxb3,len1=12) 
svxb30e = fcustom(svxb30,len1=41) 
svxs30e = fcustom(svxs30,len1=90) 
'''
svxb1e
                ,strend2(sif.ma13)>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr<1200
                ,strend2(sif.diff1-sif.dea1)>0
                ,sif.s15>0
83
                ,sif.s30>0
                ,strend2(sif.ma13)>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr30x<8000
                ,sif.xatr<1200
61

svxb3e
                ,strend2(sif.ma13)>0
                ,sif.xatr<sif.mxatr
                ,sif.xatr<1200
                ,strend2(sif.diff1-sif.dea1)>0
                ,sif.s15>0
130

svxb30e
                ,strend2(sif.ma13)>0
                ,sif.ltrend>0
                ,sif.xatr<1200
                ,sif.s15>0
13

svxs30e
                ,sif.xatr30x < 6000
                ,sif.xatr<1000
                ,sif.s15<0
13
'''

def svx2b(sif,sclose,svap,v2i,vlen,sindics,len1=3,len2=20):
    ''' 
        svama交叉计算   
    '''

    svma1 = ma(svap,len1)
    svma2 = ma(svap,len2)
    xvap = gand(cross(svma2,svma2)>0,strend(svma2)>0)
    xsignal = transform(xvap,v2i,vlen)
    signal = np.zeros_like(sclose)
    signal[sindics] = xsignal
    signal = gand(signal
                #,sif.s30>0
                #,strend2(sif.ma13)>0
                #,sif.xatr30x<sif.mxatr30x
                #,strend2(sif.mxatr30x)>0
                #,sif.mtrend>0
                #,sif.ltrend>0
                #,sif.xatr<sif.mxatr
                #,sif.xatr30x<8000
                #,sif.xatr<1200
                #,strend2(sif.diff1-sif.dea1)>0
                #,sif.s15>0
                )
    return signal
svx2b.direction = XBUY
svx2b.priority = 1500

svx2b1 = lambda sif,len1=3,len2=20:svx2b(sif,sif.close,sif.svap1,sif.v2i1,len(sif.vol),sif.i_cof,len1,len2)
svx2b1.direction = XBUY
svx2b1.priority = 1500

svx2b1_tests=[]
for ilen1 in range(3,300,2):
    for ilen2 in range(ilen1*3/2,300,4):
        svx2b1_tests.append(('%s,%s'%(ilen1,ilen2),fcustom(svx2b1,len1=ilen1,len2=ilen2)))

svx2b1e = fcustom(svxb1,len1=3,len2=20) 

'''
对现有算法的回顾
>>> ev.evaluate2_b(i00,ifuncs2.rsi_long_x(i00),60,begin=945,downlimit=80,end=141
((123, 208, -82, 22, 9), (27, -8, 614, -202), ([(-80, 8), (-80, 0), (-70, 0), (-
60, 1), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
0), (30, 1), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 21)],))
>>> ev.evaluate2_b(i00,ifuncs2.rsi_long_xx(i00),60,begin=945,downlimit=80,end=14
((222, 257, -56, 8, 1), (8, 0, 614, -78), ([(-80, 0), (-80, 0), (-70, 0), (-60,
1), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
(30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 8)],))
>>> ev.evaluate2_b(i00,ifuncs2.rsi_long_x2(i00),60,begin=945,downlimit=80,end=14
((146, 404, -75, 6, 7), (8, -5, 748, -336), ([(-80, 5), (-80, 0), (-70, 1), (-60
, 0), (-50, 0), (-40, 1), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 6)],))
>>> ev.evaluate2_b(i00,ifuncs2.macd_long_x2(i00),60,begin=945,downlimit=80,end=1
((72, 198, -85, 5, 4), (5, -4, 402, -366), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.macd_long_x3(i00),60,begin=945,downlimit=80,end=1
((125, 252, -85, 5, 3), (6, -3, 372, -250), ([(-80, 3), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_b(i00,ifuncs2.acd_ua(i00),60,begin=945,downlimit=80,end=1414)
((234, 341, -58, 11, 4), (12, -2, 992, -372), ([(-80, 2), (-80, 0), (-70, 0), (-
60, 0), (-50, 1), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (10, 0), (20,
0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 11)],))
>>> ev.evaluate2_b(i00,ifuncs2.acd_ua_sz(i00),60,begin=945,downlimit=80,end=1414
((253, 389, -63, 7, 3), (7, -2, 992, -372), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 7)],))
>>> ev.evaluate2_b(i00,ifuncs2.acd_ua_sz_b(i00),60,begin=945,downlimit=80,end=14
((170, 298, -85, 2, 1), (2, -1, 638, -212), ([(-80, 1), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 1), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 1)],))
>>> ev.evaluate2_b(i00,ifuncs2.br30(i00),60,begin=945,downlimit=80,end=1414)
((102, 149, -85, 8, 2), (10, -2, 442, -122), ([(-80, 2), (-80, 0), (-70, 0), (-6
0, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1), (20, 0
), (30, 0), (40, 0), (50, 1), (60, 1), (70, 0), (80, 1), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.xma_long(i00),60,begin=945,downlimit=80,end=1414)
((185, 252, -85, 4, 1), (4, -1, 466, -90), ([(-80, 1), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 1), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_b(i00,ifuncs2.xdma_long(i00),60,begin=945,downlimit=80,end=1414
((149, 384, -85, 2, 2), (2, -2, 588, -148), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_b(i00,ifuncs2.macd_long_x(i00),60,begin=945,downlimit=80,end=14
((-4, 133, -85, 3, 5), (3, -5, 596, -404), ([(-80, 5), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 1),
 (30, 0), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 1)],))
>>> ev.evaluate2_b(i00,ifuncs2.k5_lastup(i00),60,begin=945,downlimit=80,end=1414
((91, 298, -74, 4, 5), (6, -4, 438, -614), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 1), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.ipmacd_long_devi1(i00),60,begin=945,downlimit=80,
((30, 30, 0, 1, 0), (1, 0, 190, -16), ([(-80, 0), (-80, 0), (-70, 0), (-60, 0),
(-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 1), (30,
 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 0)],))

>>> ev.evaluate2_b(i00,ifuncs2.dnr1_dd_b(i00),60,begin=945,downlimit=80,end=1414
((46, 144, -85, 8, 6), (12, -6, 430, -590), ([(-80, 6), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (10, 0), (20, 0)
, (30, 1), (40, 0), (50, 0), (60, 0), (70, 1), (80, 0), (90, 5)],))
>>> ev.evaluate2_b(i00,ifuncs2.dnr1_uu_b(i00),60,begin=945,downlimit=80,end=1414
((132, 241, -85, 4, 2), (4, -2, 404, -292), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.dnr1_ud_b(i00),60,begin=945,downlimit=80,end=1414
((93, 192, -85, 9, 5), (11, -5, 460, -602), ([(-80, 5), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 8)],))
>>> ev.evaluate2_b(i00,ifuncs2.dpt_ux_b(i00),60,begin=945,downlimit=80,end=1414)
((152, 251, -85, 12, 5), (14, -5, 932, -602), ([(-80, 5), (-80, 0), (-70, 0), (-
60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20,
0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 12)],))
>>> ev.evaluate2_b(i00,ifuncs2.dp_uu_b(i00),60,begin=945,downlimit=80,end=1414)
((219, 372, -85, 4, 2), (5, -2, 742, -222), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.dp_ud_b(i00),60,begin=945,downlimit=80,end=1414)
((37, 190, -85, 4, 5), (6, -5, 526, -316), ([(-80, 5), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_b(i00,ifuncs2.n30pt_dud_b(i00),60,begin=945,downlimit=80,end=1414)
((449, 449, 0, 8, 0), (8, 0, 1034, -30), ([(-80, 0), (-80, 0), (-70, 0), (-60, 0
), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (
30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 8)],))
>>> ev.evaluate2_b(i00,ifuncs2.n15pt_dd_b(i00),60,begin=945,downlimit=80,end=1414)
((91, 268, -85, 4, 4), (7, -4, 476, -232), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_b(i00,ifuncs2.n60pt_uu_b(i00),60,begin=945,downlimit=80,end=1414)
((109, 476, -75, 3, 6), (7, -5, 748, -446), ([(-80, 5), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))

>>> ev.evaluate2_b(i00,ifuncs2.n60pt_uud_b(i00),60,begin=945,downlimit=80,end=1414)
((108, 140, -85, 6, 1), (6, -1, 348, -90), ([(-80, 1), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 1),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 1), (90, 4)],))
>>> ev.evaluate2_b(i00,ifuncs2.n60pt_dd_b(i00),60,begin=945,downlimit=80,end=1414)
((63, 262, -85, 3, 4), (5, -4, 598, -212), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 1), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_b(i00,ifuncs2.xud30b(i00),60,begin=945,downlimit=80,end=1414)
((167, 184, -22, 11, 1), (11, 0, 610, -74), ([(-80, 0), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 1), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 9)],))
>>> ev.evaluate2_b(i00,ifuncs2.ma1x(i00),60,begin=945,downlimit=80,end=1414)
((120, 223, -85, 6, 3), (7, -3, 374, -186), ([(-80, 3), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 6)],))


#空头
>>> ev.evaluate2_s(i00,ifuncs2.rsi_short_x(i00),60,begin=945,uplimit=80,end=1414)
((171, 311, -63, 10, 6), (-4, 13, -172, 856), ([(-80, 4), (-80, 0), (-70, 0), (-
60, 0), (-50, 0), (-40, 1), (-30, 0), (-20, 0), (-10, 1), (0, 0), (10, 0), (20,
0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 2), (80, 1), (90, 7)],))
>>> ev.evaluate2_s(i00,ifuncs2.rsi_short_x2x(i00),60,begin=945,uplimit=80,end=1414)
((226, 287, -70, 49, 10), (-8, 52, -438, 856), ([(-80, 8), (-80, 0), (-70, 0), (
-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 1), (-10, 1), (0, 1), (10, 1), (20,
 2), (30, 1), (40, 3), (50, 0), (60, 1), (70, 1), (80, 1), (90, 38)],))
>>> ev.evaluate2_s(i00,ifuncs2.rsi_short_x3(i00),60,begin=945,uplimit=80,end=1414)
((122, 231, -85, 23, 12), (-11, 30, -180, 602), ([(-80, 12), (-80, 0), (-70, 0),
 (-60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (2
0, 0), (30, 1), (40, 0), (50, 0), (60, 1), (70, 1), (80, 2), (90, 18)],))
>>> ev.evaluate2_s(i00,ifuncs2.macd_short_x(i00),60,begin=945,uplimit=80,end=1414)
((147, 245, -73, 18, 8), (-5, 22, -512, 740), ([(-80, 6), (-80, 0), (-70, 0), (-
60, 0), (-50, 1), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 2), (10, 0), (20,
1), (30, 1), (40, 0), (50, 0), (60, 0), (70, 0), (80, 1), (90, 13)],))
>>> ev.evaluate2_s(i00,ifuncs2.macd_short_xx(i00),60,begin=945,uplimit=80,end=1414)
((270, 398, -72, 8, 3), (-1, 9, -326, 740), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 1), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 8)],))
>>> ev.evaluate2_s(i00,ifuncs2.macd_short_5(i00),60,begin=945,uplimit=80,end=1414)
((193, 308, -76, 21, 9), (-7, 26, -200, 750), ([(-80, 8), (-80, 0), (-70, 0), (-
60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 1), (0, 1), (10, 1), (20,
0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 19)],))
>>> ev.evaluate2_s(i00,ifuncs2.down01(i00),60,begin=945,uplimit=80,end=1414)
((78, 200, -85, 4, 3), (-3, 5, -122, 506), ([(-80, 3), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 1), (90, 3)],))
>>> ev.evaluate2_s(i00,ifuncs2.down01x(i00),60,begin=945,uplimit=80,end=1414)
((71, 149, -85, 8, 4), (-4, 6, -122, 506), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 1), (20, 1),
 (30, 0), (40, 1), (50, 0), (60, 0), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_s(i00,ifuncs2.ma60_short(i00),60,begin=945,uplimit=80,end=1414)
((108, 219, -85, 7, 4), (-4, 7, -828, 566), ([(-80, 4), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 1), (90, 5)],))
>>> ev.evaluate2_s(i00,ifuncs2.ama_short(i00),60,begin=945,uplimit=80,end=1414)
((225, 225, 0, 7, 0), (0, 6, -60, 612), ([(-80, 0), (-80, 0), (-70, 0), (-60, 0)
, (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (10, 0), (20, 0), (3
0, 0), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_s(i00,ifuncs2.godown(i00),60,begin=945,uplimit=80,end=1414)
((128, 235, -85, 8, 4), (-4, 9, -172, 780), ([(-80, 4), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (10, 0), (20, 1)
, (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_s(i00,ifuncs2.acd_da(i00),60,begin=945,uplimit=80,end=1414)
((111, 308, -85, 5, 5), (-5, 4, -262, 552), ([(-80, 5), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 1), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_s(i00,ifuncs2.acd_da_sz_b(i00),60,begin=945,uplimit=80,end=1414)
((149, 383, -85, 2, 2), (-2, 2, -222, 560), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))

>>> ev.evaluate2_s(i00,ifuncs2.xma_short(i00),60,begin=945,uplimit=80,end=1414)
((236, 397, -85, 2, 1), (-1, 2, -190, 566), ([(-80, 1), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_s(i00,ifuncs2.xdma_short(i00),60,begin=945,uplimit=80,end=1414)
((96, 278, -85, 3, 3), (-3, 3, -196, 480), ([(-80, 3), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))

>>> ev.evaluate2_s(i00,ifuncs2.k15_lastdown(i00),60,begin=945,uplimit=80,end=1414)
((135, 163, -85, 8, 1), (-1, 9, -116, 424), ([(-80, 1), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 1)
, (30, 0), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 6)],))
>>> ev.evaluate2_s(i00,ifuncs2.k15_lastdown_s(i00),60,begin=945,uplimit=80,end=1414)
((187, 187, 0, 4, 0), (0, 4, -40, 438), ([(-80, 0), (-80, 0), (-70, 0), (-60, 0)
, (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (3
0, 1), (40, 0), (50, 0), (60, 1), (70, 0), (80, 0), (90, 2)],))
>>> ev.evaluate2_s(i00,ifuncs2.ipmacd_short_devi1(i00),60,begin=945,uplimit=80,end=1414)
((260, 490, -85, 3, 2), (-2, 5, -134, 612), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_s(i00,ifuncs2.ipmacd_short_devi1x(i00),60,begin=945,uplimit=80,end=1414)
((228, 291, -85, 5, 1), (-1, 5, -84, 716), ([(-80, 1), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 1), (80, 0), (90, 4)],))

>>> ev.evaluate2_s(i00,ifuncs2.xud30s_r(i00),60,begin=945,uplimit=80,end=1414)
((234, 234, 0, 3, 0), (0, 3, -72, 540), ([(-80, 0), (-80, 0), (-70, 0), (-60, 0)
, (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0), (3
0, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_s(i00,ifuncs2.dpt_uu_s(i00),60,begin=945,uplimit=80,end=1414)
((60, 165, -71, 5, 4), (-3, 4, -202, 716), ([(-80, 3), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 1),
 (30, 0), (40, 2), (50, 1), (60, 0), (70, 0), (80, 0), (90, 1)],))
>>> ev.evaluate2_s(i00,ifuncs2.n30pt_du_s(i00),60,begin=945,uplimit=80,end=1414)
((36, 133, -62, 6, 6), (-4, 9, -112, 604), ([(-80, 4), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 1), (-20, 0), (-10, 1), (0, 1), (10, 1), (20, 1),
 (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 3)],))
>>> ev.evaluate2_s(i00,ifuncs2.n15pt_du_s(i00),60,begin=945,uplimit=80,end=1414)
((76, 173, -85, 5, 3), (-3, 6, -564, 434), ([(-80, 3), (-80, 0), (-70, 0), (-60,
 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),
 (30, 0), (40, 0), (50, 1), (60, 0), (70, 0), (80, 0), (90, 4)],))
>>> ev.evaluate2_s(i00,ifuncs2.n60pt_duu_s(i00),60,begin=945,uplimit=80,end=1414)
((120, 214, -85, 13, 6), (-5, 12, -456, 550), ([(-80, 6), (-80, 0), (-70, 0), (-
60, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 2), (10, 0), (20,
0), (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 11)],))
>>> ev.evaluate2_s(i00,ifuncs2.nr30s(i00),60,begin=945,uplimit=80,end=1414)
((166, 418, -85, 5, 5), (-5, 6, -416, 750), ([(-80, 5), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 0), (80, 0), (90, 5)],))
>>> ev.evaluate2_s(i00,ifuncs2.nr30b(i00),60,begin=945,uplimit=80,end=1414)
((116, 216, -85, 4, 2), (-2, 4, -228, 460), ([(-80, 2), (-80, 0), (-70, 0), (-60
, 0), (-50, 0), (-40, 0), (-30, 0), (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0)
, (30, 0), (40, 0), (50, 0), (60, 0), (70, 1), (80, 0), (90, 3)],))


'''

