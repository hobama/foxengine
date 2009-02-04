# -*- coding: utf-8 -*-

import re
import unittest
from wolfox.fengine.core.d1indicator import *

class ModuleTest(unittest.TestCase):
    def test_expma(self):
        #print 'in expma'
        source = np.array([25000,24875,24781,24594,24500,24625,25219,27250])
        self.assertEquals([0,0,0,0,24698,24674,24855,25653],expma(source,333).tolist())   #相当于5日
 
    def test_cexpma(self):
        source = np.array([25000,24875,24781,24594,24500,24625,25219,27250])
        self.assertEquals([0,0,0,0,24698,24674,24855,25653],cexpma(source,5).tolist())   #相当于5日

    def test_macd(self):#因为是其它几个算法的集成，所以不测试实际数据，只测试可执行性
        source = np.array([63750,65625,63000,62750,63250,65375,66000,65000,64875,64750,64375,64375,64625,65375,64500,65250,67875,68000,66875,66250,65875,66000,65875,64750,63000,63375,63375,63375])
        #self.assertEquals(28,len(source))
        diff,signal = macd(source)
        #print diff
        source = np.array([63750,65625,63000,62750,63250,65375,66000])
        diff,dea = macd(source)
        self.assertTrue(True)

    def test_cmacd(self):#因为是其它几个算法的集成，所以不测试实际数据，只测试可执行性
        source = np.array([63750,65625,63000,62750,63250,65375,66000,65000,64875,64750,64375,64375,64625,65375,64500,65250,67875,68000,66875,66250,65875,66000,65875,64750,63000,63375,63375,63375])
        #self.assertEquals(28,len(source))
        diff,dea = cmacd(source)
        #print diff
        source = np.array([63750,65625,63000,62750,63250,65375,66000])
        diff,dea = cmacd(source)

    def test_downlimit(self):
        source = np.array([700,720,900,1100,1000,999,980,720,792,793,700,990])
        signal = np.array([0,1,0,0,0,1,0,0,1,-1,0,0])
        self.assertEquals([636,655,818,1000,1000,908,908,908,720,721,721,900],downlimit(source,signal,100).tolist())
        signal2 = np.array([1,1,0,0,0,1,0,0,1,-1,0,0])
        self.assertEquals([636,655,818,1000,1000,908,908,908,720,721,721,900],downlimit(source,signal2,100).tolist())
        self.assertEquals([6726],downlimit(np.array([7230]),np.array([1]),75).tolist())  #从实际情况中来的测试
        self.assertEquals([6726,6623,6437],downlimit(np.array([7230,7120,6920]),np.array([1,1,1]),75).tolist())

    def test_uplimit(self):
        source = np.array([700,720,640,600,800,999,780,720,792,680,800,990])
        signal = np.array([0,1,0,0,0,1,0,0,1,-1,0,0])
        self.assertEquals([770,792,704,660,660,1099,858,792,871,748,748,748],uplimit(source,signal,100).tolist())
        signal2 = np.array([1,1,0,0,0,1,0,0,1,-1,0,0])
        self.assertEquals([770,792,704,660,660,1099,858,792,871,748,748,748],uplimit(source,signal2,100).tolist())

    def test_tdownlimit(self):
        source = np.array([700,720,800,750,700,650,980,720,792,750,710,690])
        signal = np.array([0,1,1,1,0,1,0,0,1,1,0,1])
        #self.assertEquals([636,655,727,682,682,591,891,891,720,682,682,627],downlimit(source,signal,100))
        self.assertEquals([636,655,727,727,727,591,891,891,720,720,720,627],tdownlimit(source,signal,100).tolist())
        signal2 = np.array([0,1,1,1,1,1,0,0,1,1,0,1])
        self.assertEquals([636,655,727,727,727,591,891,891,720,720,720,627],tdownlimit(source,signal2,100).tolist())
        signal3 = np.array([1,1,0,0,0,1,0,0,1,-1,0,0])    #这个测试没有意义，聊以不删
        self.assertEquals([636, 655, 727, 727, 727, 591, 891, 891, 720, 682, 682, 682],downlimit(source,signal3,100).tolist())
        self.assertEquals([636, 655, 727, 727, 727, 591, 891, 891, 720, 720, 720, 720],tdownlimit(source,signal3,100).tolist())

    def test_tuplimit(self):
        source = np.array([700,720,750,700,800,999,1200,720,800,680,800,990])
        signal = np.array([0,1,1,1,0,1,1,0,1,1,0,0])
        #self.assertEquals([770, 792, 825, 770, 770, 1099, 1320, 792, 880, 748, 748, 748],uplimit(source,signal,100))
        self.assertEquals([770,792,792,770,770,1099,1099,792,880,748,748,748],tuplimit(source,signal,100).tolist())
        signal2 = np.array([1,1,0,0,0,1,0,0,1,1,0,0])
        self.assertEquals([770, 792, 792, 770, 770, 1099, 1099, 792, 880, 748, 748, 748],uplimit(source,signal2,100).tolist())
        self.assertEquals([770, 770, 770, 770, 770, 1099, 1099, 792, 880, 748, 748, 748],tuplimit(source,signal2,100).tolist())

    def test_zigzag(self):
        source = np.array([700,720,900,1100,1000,999,980,720,792,793,800,990])
        points,boundary = zigzag(source,100)
        self.assertEquals([0,0,0,0,0,-1,0,0,0,1,0,0],points.tolist())
        self.assertEquals([0,0,655,818,1000,1000,1099,1078,792,792,721,727],boundary.tolist())

    def test_wms(self):
        tclose = np.array([800,800,800,800,800,800,800,800,800,800,800,800])
        thigh =  np.array([800,900,900,900,900,900,900,900,1000,900,1200,900])
        tlow = np.array([800,600,600,600,600,600,600,600,500,500,400,400])
        self.assertEquals([BASE,BASE*2/3,BASE*2/3,BASE*2/3,BASE*2/3,BASE*2/3,BASE*2/3,BASE*2/3,BASE*3/5,BASE*3/5,BASE/2,BASE/2],wms(tclose,thigh,tlow,9).tolist())

    def test_kdj(self):
        tclose = np.array([800,800,800,800,800,800,800,800,800,800,800,800])
        thigh =  np.array([800,900,900,900,900,900,900,900,1000,900,1200,900])
        tlow =  np.array([800,600,600,600,600,600,600,600,500,500,400,400])
        k,d,j = kdj(tclose,thigh,tlow)
        self.assertEquals([667,667,667,667,667,667,667,667,645,630,587,558],k.tolist())
        self.assertEquals([556, 593, 618, 634, 645, 652, 657, 660, 655, 647,627,604],d.tolist())
        self.assertEquals([334, 445, 520, 568, 601, 622, 637, 646, 675, 681,707,696],j.tolist())
        rsv = wms(tclose,thigh,tlow,9)
        k2,d2,j2 = kdj(tclose,thigh,tlow,rsv)
        self.assertEquals([667,667,667,667,667,667,667,667,645,630,587,558],k2.tolist())
        self.assertEquals([556, 593, 618, 634, 645, 652, 657, 660, 655, 647,627,604],d2.tolist())
        self.assertEquals([334, 445, 520, 568, 601, 622, 637, 646, 675, 681,707,696],j2.tolist())

    def test_ckdj(self):
        tclose = np.array([800,800,800,800,800,800,800,800,800,800,800,800])
        thigh =  np.array([800,900,900,900,900,900,900,900,1000,900,1200,900])
        tlow =  np.array([800,600,600,600,600,600,600,600,500,500,400,400])
        k,d,j = ckdj(tclose,thigh,tlow)
        self.assertEquals([667,667,667,667,667,667,667,667,645,630,587,558],k.tolist())
        self.assertEquals([556, 593, 618, 634, 645, 652, 657, 660, 655, 647,627,604],d.tolist())
        self.assertEquals([889, 815, 765, 733, 711, 697, 687, 681, 625, 596, 507, 466],j.tolist())
        rsv = wms(tclose,thigh,tlow,9)
        k2,d2,j2 = ckdj(tclose,thigh,tlow,rsv)
        self.assertEquals([667,667,667,667,667,667,667,667,645,630,587,558],k2.tolist())
        self.assertEquals([556, 593, 618, 634, 645, 652, 657, 660, 655, 647,627,604],d2.tolist())
        self.assertEquals([889, 815, 765, 733, 711, 697, 687, 681, 625, 596, 507, 466],j2.tolist())

    def test_obv(self):
        tclose = np.array([1000,1010,1020,1030,1020,1030,1000,1000,1020,1030,1020,1030])
        tvolume = np.array([100,100,100,100,100,100,100,100,100,100,100,100])
        self.assertEquals([0,100,200,300,200,300,200,200,300,400,300,400],obv(tclose,tvolume).tolist())
        self.assertEquals(np.cumsum(trend(tclose)*tvolume).tolist(),obv(tclose,tvolume).tolist())   #与组合算法比较

    def test_roc(self):
        self.assertEquals([0,1000,1000,500,500,1000,333,666],roc(np.array([1,2,4,6,9,18,24,40])).tolist())
        self.assertEquals([0,0,1500,1000,625,1000,833,611],roc(np.array([1,2,4,6,9,18,24,40]),2).tolist())
        self.assertEquals([0,0,0,0,0],roc(np.array([1,2,4,6,9]),5).tolist())
        self.assertEquals([0,0,0,0,2000],roc(np.array([1,2,4,6,9]),4).tolist())

    def test_pvt(self):
        tclose = np.array([1000,1010,1020,1030,1020,1030,1000,1000,1020,1030,1020,1030])
        tvolume = np.array([100,100,100,100,100,100,100,100,100,100,100,100])
        self.assertEquals([0, 1000, 1990, 2970, 1999, 2979, 66, 66, 2066, 3046, 2075, 3055],pvt(tclose,tvolume).tolist())
        #self.assertEquals(np.cumsum(roc(tclose) * tvolume).tolist(),pvt(tclose,tvolume).tolist())   #与组合算法比较，有四舍五入顺序上的区别，故此结果有较大的误差

    def test_rsi(self):
        source = np.array([100,120,130,120,100,120,150,180,160,160,140,150])
        self.assertEquals([0,0,0,750,250,400,714,1000,750,600,0,333],rsi(source,3).tolist())

    def test_uplines(self):
        self.assertEquals([0,1,1,1,1,0,0,0,0],uplines(np.array([1,2,3,4,5,5,4,3,2])).tolist())
        self.assertEquals([0,0,1,1,0,0,1,1],uplines(np.array([0,2,4,8,6,4,8,10]),np.array([1,2,3,4,5,6,7,8])).tolist())
        self.assertEquals([0,0,1,0,0,0,1,1],uplines(np.array([1,3,5,7,5,7,9,11]),np.array([0,2,4,8,6,4,8,10]),np.array([1,2,3,4,5,6,7,8])).tolist())
        self.assertEquals([0,0,1,0,0,0,1,0],uplines(np.array([2,4,6,8,6,8,10,8]),np.array([1,3,5,7,5,7,9,11]),np.array([0,2,4,8,6,4,8,10]),np.array([1,2,3,4,5,6,7,8])).tolist())
        self.assertEquals([0,0,1,0,0,0,0,0],uplines(np.array([10,20,30,40,30,20,10,45]),np.array([2,4,6,8,6,8,10,8]),np.array([1,3,5,7,5,7,9,11]),np.array([0,2,4,8,6,4,8,10]),np.array([1,2,3,4,5,6,7,8])).tolist())

    def test_efficientRate(self):
        source = np.array([10,20,15,18,16,19,25,22,18,27,30])
        self.assertEquals([0,0,0,0,0,0,0,0,0,0,416],efficient_rate(source).tolist())
        self.assertEquals([0,1000,-1000,1000,-1000,1000,1000,-1000,-1000,1000,1000],efficient_rate(source,1).tolist())
        self.assertEquals([0,0,333,-250,200,200,1000,333,-1000,384,1000],efficient_rate(source,2).tolist())
        self.assertEquals([0,0,0,0,0,9000/23,5000/19,7000/17,0,11000/25,11000/25],efficient_rate(source,5).tolist())
        self.assertEquals([0,0,0,0,0,0,0,0,0,17000/45,10000/38],efficient_rate(source,9).tolist())
        self.assertRaises(AssertionError,efficient_rate,source,0)

    def test_amaMaker(self):
        ama = ama_maker()
        self.assertEquals([0,0,0,0,0,0,0,0,0,0,6174,6189,6188,6192,6192],ama(np.array([6063,6041,6065,6078,6114,6121,6106,6101,6166,6169,6195,6222,6186,6214,6185])).tolist())
        self.assertEquals([0,0,0,0,0],ama(np.array([6063,6041,6065,6078,6114])).tolist())

    def test_emv(self):
        self.assertEquals([],emv(np.array([]),np.array([]),np.array([])).tolist())
        self.assertEquals([0],emv(np.array([10]),np.array([5]),np.array([300])).tolist())
        self.assertEquals([0,4000,-33334],emv(np.array([1100,1200,1000]),np.array([1000,1100,800]),np.array([2000,2500,1500])).tolist())

    def test_semv(self):
        self.assertEquals([],semv(np.array([]),np.array([]),np.array([])).tolist())
        self.assertEquals([0],semv(np.array([10]),np.array([5]),np.array([300]),1).tolist())
        self.assertEquals([0,19052],semv(np.array([1000,1020]),np.array([985,996]),np.array([30000,40000]),1).tolist())
        self.assertEquals([0,-7306],semv(np.array([1000,998]),np.array([985,974]),np.array([30000,40000]),1).tolist())
        self.assertEquals([0,0,9676],semv(np.array([1000,1020,1050]),np.array([985,996,1000]),np.array([30000,40000,150000]),2).tolist())
        high = low = volume = np.array([1000]*10)
        self.assertEquals([0]*10,semv(high,low,volume).tolist())
        high = low = volume = np.array([1000]*13)
        self.assertEquals([0]*13,semv(high,low,volume).tolist())

    def test_vap(self):
        r1,v1 = vap(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),100)
        self.assertEquals(([11,22,22,33,33,33,44,44,55,55,55],[0,1,1,2,2,2,3,3,4,4,4]),(r1.tolist(),v1.tolist()))
        r2,v2 = vap(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),100)
        self.assertEquals(([11,22,22,33,33,33,44,44,55,55,55],[0,1,1,2,2,2,3,3,4,4,4]),(r2.tolist(),v2.tolist()))

    def test_vap2(self):
        r1,v1 = vap2(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),200)
        self.assertEquals(([22,33,33,44,55],[1,2,2,3,4]),(r1.tolist(),v1.tolist()))
        r2,v2 = vap2(np.array([201,258,341,280,330]),np.array([11,22,33,44,55]),200)
        self.assertEquals(([11,22,33,33,44,55,55],[0,1,2,2,3,4,4]),(r2.tolist(),v2.tolist()))

    def test_svap(self):
        r1,v1 = svap(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([100,100,100,100,100]))
        self.assertEquals(([11,22,22,33,33,33,44,44,55,55,55],[0,1,1,2,2,2,3,3,4,4,4]),(r1.tolist(),v1.tolist()))
        r2,v2 = svap(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),np.array([100,100,100,100,100]))
        self.assertEquals(([11,22,22,33,33,33,44,44,55,55,55],[0,1,1,2,2,2,3,3,4,4,4]),(r2.tolist(),v2.tolist()))
        r3,v3 = svap(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([100,200,300,200,300]))
        self.assertEquals(([11,22,33,44,55],[0,1,2,3,4]),(r3.tolist(),v3.tolist()))
        r4,v4 = svap(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),np.array([100,200,300,100,100]))
        self.assertEquals(([11,22,33,44,44,55,55,55],[0,1,2,3,3,4,4,4]),(r4.tolist(),v4.tolist()))
        r5,v5 = svap(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([0,0,100,200,100]))
        self.assertEquals(([11,22,33,33,33,44,55,55,55],[0,1,2,2,2,3,4,4,4]),(r5.tolist(),v5.tolist()))
        r6,v6 = svap(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),np.array([0,0,100,200,100]))
        self.assertEquals(([11,22,33,33,33,44,55,55,55],[0,1,2,2,2,3,4,4,4]),(r6.tolist(),v6.tolist()))
        r7,v7 = svap(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),np.array([0,0,0,0,0]))
        self.assertEquals(([],[]),(r7.tolist(),v7.tolist()))

    def test_svap2(self):
        r1,v1 = svap2(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([200,200,200,200,200]))
        self.assertEquals(([22,33,33,44,55],[1,2,2,3,4]),(r1.tolist(),v1.tolist()))
        r2,v2 = svap2(np.array([201,258,341,280,330]),np.array([11,22,33,44,55]),np.array([200,200,200,200,200]))
        self.assertEquals(([11,22,33,33,44,55,55],[0,1,2,2,3,4,4]),(r2.tolist(),v2.tolist()))
        r3,v3 = svap2(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([200,300,200,300,200]))
        self.assertEquals(([22,33,44,55],[1,2,3,4]),(r3.tolist(),v3.tolist()))
        r4,v4 = svap2(np.array([201,258,341,280,330]),np.array([11,22,33,44,55]),np.array([200,300,200,300,200]))
        self.assertEquals(([11,33,33,33,55,55,55],[0,2,2,2,4,4,4]),(r4.tolist(),v4.tolist()))
        r5,v5 = svap2(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),np.array([0,0,200,300,200]))
        self.assertEquals(([33,44,55],[2,3,4]),(r5.tolist(),v5.tolist()))
        r6,v6 = svap2(np.array([201,258,341,280,330]),np.array([11,22,33,44,55]),np.array([0,0,200,300,200]))
        self.assertEquals(([33,44,55,55],[2,3,4,4]),(r6.tolist(),v6.tolist()))
        r7,v7 = svap2(np.array([50,101,299,104,250]),np.array([11,22,33,44,55]),np.array([0,0,0,0,0]))
        self.assertEquals(([],[]),(r7.tolist(),v7.tolist()))

    def test_svap_ma(self):   #只测试通路
        svap_ma(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),3)
        self.assertTrue(True)

    def test_svap2_ma(self):  #只测试通路
        svap2_ma(np.array([100,200,300,200,300]),np.array([11,22,33,44,55]),3)
        self.assertTrue(True)

    def test_index2v(self):
        self.assertEquals([1,1,1,0,1,0,1],index2v(np.array([11,21,31,41,51]),np.array([0,4,6,2,1]),7).tolist())
        self.assertEquals([1,1,1,0,1,0,1],index2v(np.array([11,21,31,41,51,61]),np.array([0,4,6,2,1,4]),7).tolist())
        self.assertEquals([1,1,1,0,1,0,1],index2v(np.array([0,21,31,41,51,61,71]),np.array([0,4,6,2,1,4,0]),7).tolist())
        try:    
            self.assertEquals([1,1,1,0,1,0,1],index2v(np.array([11,21,31,41,51]),np.array([0,4,6,2,1]),6).tolist())
        except: 
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_fill_price(self):
        from wolfox.fengine.core.d1indicator import _fill_price
        r1,v1 = _fill_price(np.array([11,22,33]),np.array([1,2,3]))
        self.assertEquals(([11,22,22,33,33,33],[0,1,1,2,2,2]),(r1.tolist(),v1.tolist()))
        r2,v2 = _fill_price(np.array([]),np.array([]))
        self.assertEquals(([],[]),(r2.tolist(),v2.tolist()))

    def test_find_first_nonzero_index(self):
        from wolfox.fengine.core.d1indicator import _find_first_nonzero_index
        self.assertEquals(-1,_find_first_nonzero_index(np.array([0,0,0])))
        self.assertEquals(0,_find_first_nonzero_index(np.array([1,0,0])))
        self.assertEquals(0,_find_first_nonzero_index(np.array([1,0,1])))
        self.assertEquals(1,_find_first_nonzero_index(np.array([0,1,1])))
        self.assertEquals(2,_find_first_nonzero_index(np.array([0,0,1])))


if __name__ == "__main__":
    import logging
    logging.basicConfig(filename="test.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    
    unittest.main()