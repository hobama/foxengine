# -*- coding: utf-8 -*-


'''
    采用吕总类似的系统
    考虑
    1. 最低/最高点策略
    2. 收盘价策略 
    3. 下午考虑最近120分钟

'''

from wolfox.fengine.ifuture.ibase import *
import wolfox.fengine.ifuture.iftrade as iftrade
import wolfox.fengine.ifuture.fcontrol as control
from wolfox.fengine.ifuture.xfuncs import *

def nhh(sif):
    #使用最高点
    return gand(
            #cross(rollx(sif.dhigh+30),sif.high)>0
            sif.high > rollx(sif.dhigh+30),
        )
 
def nhc(sif):
    #使用收盘价
    return gand(
            #cross(rollx(sif.dhigh-30),sif.close)>0
            sif.close > rollx(sif.dhigh-30),
        )

def nll(sif):
    #使用最低点
    return gand(
            #cross(rollx(sif.dlow-30),sif.low)<0
            sif.low < rollx(sif.dlow-30),
        )

def nlc(sif):
    #使用收盘价,而且是前面倒数第三次的dlow
    return gand(
            #cross(rollx(sif.dlow+30,3),sif.close)<0
            sif.close < rollx(sif.dlow+30,3),
        )

def nhc_fake(sif):  
    #使用收盘价并且用条件单时，必须面对的假突破。即盘中突破收盘拉回
    return gand(
            #cross(rollx(sif.dhigh-30),sif.close)>0
            sif.high > rollx(sif.dhigh-30),
            sif.close < rollx(sif.dhigh-30),
        )


def nlc_fake(sif):  
    #使用收盘价并且用条件单时，必须面对的假突破。即盘中突破收盘拉回
    return gand(
            #cross(rollx(sif.dlow+30),sif.low)<0,
            sif.low   <  rollx(sif.dlow+30,3),            
            sif.close >  rollx(sif.dlow+30,3)
        )


def na2000(sif):
    return gand(
                sif.atr < 8000,
                sif.atr5x < 15000,
                sif.atr30x < 30000,
            )

  
#用atr的绝对值效果不行
nbreak_nhh = BXFuncA(fstate=gofilter,fsignal=nhh,fwave=gofilter,ffilter=nfilter)
nbreak_nll = SXFuncA(fstate=gofilter,fsignal=nll,fwave=gofilter,ffilter=nfilter)
nbreak_nhc = BXFuncA(fstate=gofilter,fsignal=nhc,fwave=gofilter,ffilter=nfilter)  
nbreak_nlc = SXFuncA(fstate=gofilter,fsignal=nlc,fwave=gofilter,ffilter=nfilter)  

nbreak = [nbreak_nhh,nbreak_nll]

break_nhh = BXFuncA(fstate=gofilter,fsignal=nhh,fwave=nx2000X,ffilter=nfilter)
break_nhh.name = u'向上突破新高'
break_nll = SXFuncA(fstate=gofilter,fsignal=nll,fwave=nx2000X,ffilter=nfilter)

break_nhc = BXFuncA(fstate=gofilter,fsignal=nhc,fwave=nx2000X,ffilter=nfilter)  #F1好
break_nlc = SXFuncA(fstate=gofilter,fsignal=nlc,fwave=nx2000X,ffilter=nfilter)  #F1效果明显，但总收益下降

break_nhc_fake = BXFuncA(fstate=gofilter,fsignal=nhc_fake,fwave=nx2000X,ffilter=nfilter)  #F1好
break_nlc_fake = SXFuncA(fstate=gofilter,fsignal=nlc_fake,fwave=nx2000X,ffilter=nfilter)  #F1效果明显，但总收益下降

abreak_nhh = BXFuncA(fstate=gofilter,fsignal=nhh,fwave=na2000,ffilter=nfilter)
abreak_nll = SXFuncA(fstate=gofilter,fsignal=nll,fwave=na2000,ffilter=nfilter)

abreak_nhc = BXFuncA(fstate=gofilter,fsignal=nhc,fwave=na2000,ffilter=nfilter)  #F1好
abreak_nlc = SXFuncA(fstate=gofilter,fsignal=nlc,fwave=na2000,ffilter=nfilter)  #F1效果明显，但总收益下降

def sdown(sif):
    return gand(
            sif.t120 < 30,
        )

#顶部分没办法加优化
#def sup(sif):
#    return gand(
#            strend2(sif.ma30) > 0,
#        )

#sbreak_nhh = BXFuncA(fstate=sup,fsignal=nhh,fwave=nx2000X,ffilter=nfilter)
#sbreak_nhc = BXFuncA(fstate=sup,fsignal=nhc,fwave=nx2000X,ffilter=nfilter)

sbreak_nll = SXFuncA(fstate=sdown,fsignal=nll,fwave=nx2000X,ffilter=nfilter)    #这个R高，但是次数少
sbreak_nll.name = u'向下突破'
sbreak_nlc = SXFuncA(fstate=sdown,fsignal=nlc,fwave=nx2000X,ffilter=nfilter)    #这个R小，次数多
sbreak_nlc.name = u'即将向下突破'

sbreak_nlc_fake = SXFuncA(fstate=sdown,fsignal=nlc_fake,fwave=nx2000X,ffilter=nfilter)    #F1效果明显
sbreak_nlc_fake.name = u'向下假突破'    #假突破时需要马上平仓

lbreak = [break_nhh,break_nll]
lbreak2 = [break_nhc,break_nlc]

xbreak = [break_nhh,break_nlc]  #这个比较好，顶底不对称
xbreak2 = [break_nhc,break_nll]

zbreak = [break_nhh,sbreak_nlc,sbreak_nlc_fake,sbreak_nll] #这个最好,更加不对称,添加了假突破. 更加实盘化
zbreak2 = [break_nhh,sbreak_nll]    #这个效果好一些

lcandidate = [sbreak_nll]

xxx = zbreak#lbreak + lbreak2

#

def pinfo(sif,trades):
    ss = 0  
    mas = 0
    mis = 9999
    nn = 0
    for trade in trades:
        ia0 = trade.actions[0].index
        ia1 = trade.actions[1].index
        a0 = trade.actions[0]
        a1 = trade.actions[1]
        direction = a0.position
        topen = sif.open[ia0]
        thigh = sif.high[ia0]
        tlow = sif.low[ia0]
        tclose = sif.close[ia0]
        #滑点是与系统开仓价即止损基准价的差别
        #ia0-1是信号发生分钟，ia0-2是信号发生之前的dhigh/dlow基准
        if direction == LONG:
            tprice = sif.dhigh[ia0-2] + 30
            tskip = tprice - topen
        else:
            tprice = sif.dlow[ia0-2] + 30
            tskip = topen - tprice
        ss += tskip
        if tskip > mas:
            mas = tskip
        if tskip < mis:
            mis = tskip
        nn += 1
        print trade.profit,a0.date,a0.time,direction,a0.price,a1.time,a1.price,ia1-ia0,'|',tskip,tprice#,thigh,sif.dhigh[ia0-1]
    print u'总次数=%s,滑点总数=%s,最大滑点=%s,最大有利滑点=%s' % (nn,ss,mas,mis)
    


######考虑用tmax(60)
mlen = 120
def mhh(sif):
    #使用最高点
    return gand(
            sif.time>1115,
            cross(rollx(tmax(sif.high,mlen)+30),sif.high)>0
        )
 
def mhc(sif):
    #使用收盘价
    return gand(
            sif.time>1115,
            cross(rollx(tmax(sif.high,mlen)-30),sif.close)>0
        )

def mll(sif):
    #使用最低点
    return gand(
            sif.time>1115,
            cross(rollx(tmin(sif.low,mlen)-30),sif.low)<0
        )

def mlc(sif):
    #使用收盘价
    return gand(
            sif.time>1115,
            cross(rollx(tmin(sif.low,mlen)+30),sif.close)<0
        )

break_mhh = BXFuncA(fstate=gofilter,fsignal=mhh,fwave=nx2000X,ffilter=nfilter)  #差于nhh
break_mll = SXFuncA(fstate=gofilter,fsignal=mll,fwave=nx2000X,ffilter=nfilter)  #差于nll

break_mhc = BXFuncA(fstate=gofilter,fsignal=mhc,fwave=nx2000X,ffilter=nfilter)  #差于nhc
break_mlc = SXFuncA(fstate=gofilter,fsignal=mlc,fwave=nx2000X,ffilter=nfilter)  #差于nlc

sbreak_mll = SXFuncA(fstate=sdown,fsignal=mll,fwave=nx2000X,ffilter=nfilter)    #差于nll
sbreak_mlc = SXFuncA(fstate=sdown,fsignal=mlc,fwave=nx2000X,ffilter=nfilter)    #差于nlc


#mxxx = [break_mhh,break_mhc,break_mll,break_mlc]
mxxx = [break_mhh,sbreak_mll]   #这个叠加反效果

####添加老系统

wxxx = [xds,xdds3,k5_d3b,xuub,K1_DDD1,K1_UUX,K1_RU,Z5_P2,xmacd3s,xup01,ua_fa,FA_15_120]

wxxx_s = [xds,xdds3,k5_d3b,K1_DDD1,Z5_P2,xmacd3s,FA_15_120]
wxxx_b = [xuub,K1_UUX,K1_RU,xup01,ua_fa]

wxss = CSFuncF1(u'向下投机组合',*wxxx_s)
wxbs = CBFuncF1(u'向上投机组合',*wxxx_b)

wxfs = [wxss,wxbs]

xxx2 = xxx +wxfs #+ wxxx

for x in xxx2+mxxx:
    x.stop_closer = iftrade.atr5_uxstop_kF #60/120       
    x.cstoper = iftrade.F60  #初始止损,目前只在动态显示时用
