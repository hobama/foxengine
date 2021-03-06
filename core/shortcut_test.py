# -*- coding: utf-8 -*-

import sys
import unittest
from wolfox.fengine.core.base import CommonObject
from wolfox.fengine.core.shortcut import *

class ModuleTest(unittest.TestCase):    #只测试通道
    def test_signals_maker(self):
        buyer1 = lambda stock:np.array([0,1,1])
        buyer2 = lambda stock:np.array([1,0,1])
        buyer3 = lambda stock:np.array([0,0,1])
        a = np.array([(1,2,1),(1,3,4),(1,5,6),(1,7,8),(1,9,10),(1,11,12),(1,13,14)])
        sa = CommonObject(id=3,transaction=a)
        m1 = signals_maker([buyer1,buyer2])
        self.assertEquals([1,1,1],m1(sa).tolist())
        m2 = signals_maker([buyer1,buyer3])
        self.assertEquals([0,1,1],m2(sa).tolist())        
        m3 = signals_maker([buyer2,buyer3])
        self.assertEquals([1,0,1],m3(sa).tolist())        

    def test_csc_func(self):
        a = np.array([(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14)])
        sa = CommonObject(id=3,transaction=a)
        bs = np.array([0,1])
        csc_func(sa,bs)
        self.assertTrue(True)
        #空测试
        a = np.array([(),(),(),(),(),(),()])
        sa = CommonObject(id=3,transaction=a)
        bs = np.array([])
        csc_func(sa,bs)
        self.assertTrue(True)

    def test_create_evaluator(self): #只测试通路
        evf = create_evaluator()
        evf([],{})
        self.assertTrue(True)

    def test_normal_evaluate(self):    #只测试通路
        normal_evaluate([],{})
        self.assertTrue(True)

    def test_prepare_catalogs(self):    #只测试通路
        a = np.array([(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14)])
        b = np.array([(11,12),(13,14),(15,16),(17,18),(19,110),(111,112),(113,114)])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        ctree,catalogs = prepare_catalogs(sdata)
        #self.assertEquals(2,len(sa.g60))
        #self.assertEquals(2,len(sb.g60))

    def test_prepare_gbjg(self):    #这里实际上没有测试循环内通道
        a = np.array([(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14)])
        b = np.array([(11,12),(13,14),(15,16),(17,18),(19,110),(111,112),(113,114)])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=4,code='test2',transaction=b)
        sdata = {3:sa,4:sb}
        prepare_gbjg(sdata) #测试stock_id不在sdata数据中
        self.assertTrue(True)
        sc = CommonObject(id=20,code='test2',transaction=b)
        sdata = {3:sa,4:sb,20:sc}
        prepare_gbjg(sdata) #测试stock_id不在sdata数据中
        sdata[20].ag = 500
        sdata[20].zgb = 1000
        sdata[20].last_date = 200101

    def test_calc_trades(self):
        a = np.array([(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14)])
        b = np.array([(11,12),(13,14),(15,16),(17,18),(19,110),(111,112),(113,114)])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        dates = np.array([20010101,20010102])
        buyer = lambda x:x.transaction[CLOSE]
        name,trades = calc_trades(buyer,atr_seller,sdata,dates,20010101)
        #print name
        self.assertTrue(name)

    def test_batch(self):
        dummy = range(45)
        a = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        b = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        dates = np.arange(20010101,20010146)    #45个采样点，避免在计算CSHARP中线形回归的时候报警
        batch([],sdata,dates,20010101)    #空测试
        self.assertTrue(True)
        pman = AdvancedPositionManager()
        dman = XDateManager(range(20010101,20010215))
        buyer = lambda x:np.ones(45,int)
        c1 = BaseObject(buyer=buyer,seller=atr_seller,pman=pman,dman=dman)
        c2 = BaseObject(buyer=buyer,seller=atr_seller,pman=pman,dman=dman)
        batch([c1,c2],sdata,dates,20010101)
        self.assertTrue(c1.name)
        self.assertEquals(c1.name,c2.name)
        self.assertTrue(True)

    def test_batch_except(self):
        pass    #计算内部的异常已经在mediator._calc中吸收了

    def test_batch_last(self):
        dummy = range(45)
        a = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        b = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        dates = np.arange(20010101,20010146)    #45个采样点，避免在计算CSHARP中线形回归的时候报警
        batch_last([],sdata,dates,20010101)    #空测试
        self.assertTrue(True)
        buyer = lambda x:np.ones(45,int)
        buyer2 = lambda x:np.ones(40,int)
        buyer.__name__ = 'buyer1'
        buyer2.__name__ = 'buyer2'
        c1 = BaseObject(buyer=buyer,seller=atr_seller)
        c2 = BaseObject(buyer=buyer2,seller=atr_seller)
        ts = batch_last([c1,c2],sdata,dates,20010101)
        self.assertTrue(True)

    def test_mm_batch(self):
        dummy = range(45)
        a = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        b = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        sa = CommonObject(id=3,code='test1',transaction=a,atr=dummy)
        sb = CommonObject(id=3,code='test2',transaction=b,atr=dummy)
        sdata = {'sa':sa,'sb':sb}
        dates = np.arange(20010101,20010146)    #45个采样点，避免在计算CSHARP中线形回归的时候报警
        mm_batch([],sdata,dates,20010101)    #空测试
        self.assertTrue(True)
        buyer = lambda x:np.ones(45,int)
        c1 = BaseObject(buyer=buyer,seller=atr_seller,pman=None,dman=None)
        c2 = BaseObject(buyer=buyer,seller=atr_seller,pman=None,dman=None)
        mm_batch([c1,c2],sdata,dates,20010101)
        self.assertTrue(c1.name)
        self.assertEquals(c1.name,c2.name)
        self.assertTrue(True)

    def test_merge(self):
        pman = AdvancedPositionManager()
        dman = XDateManager(range(20010101,20010215))
        dummy = range(45)
        a = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        b = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        dates = np.arange(20010101,20010146)    #45个采样点，避免在计算CSHARP中线形回归的时候报警
        r1,s1 = merge([],sdata,dates,20010101,pman,dman)    #空测试
        self.assertEquals(0,r1.pre_ev.count)
        self.assertEquals(0,r1.g_ev.count)        
        self.assertTrue(True)
        buyer = lambda x:np.ones(45,int)
        c1 = BaseObject(buyer=buyer,seller=atr_seller,pman=pman,dman=dman)
        c2 = BaseObject(buyer=buyer,seller=atr_seller,pman=pman,dman=dman)
        r2,s2 = merge([c1,c2],sdata,dates,20010101,pman,dman)
        self.assertEquals(0,r2.pre_ev.count)
        self.assertEquals(0,r2.g_ev.count)        
        self.assertTrue(True)

    def test_save_configs(self):
        result = BaseObject(RPR=1,CSHARP=0,AVGRANGE=(1,2),MAXRANGE=(3,4),income_rate=123,pre_ev=[1,2],g_ev=[3,4])
        config = BaseObject(name='test',result=result,strade='test strade',mm=(100,80,80,5))
        import os
        save_configs('test_save_configs.txt',[],20010101,20050101)
        save_configs('test_save_configs.txt',[config,config],20010101,20050101)
        os.remove('test_save_configs.txt')

    def test_save_last(self):
        from wolfox.fengine.base.common import Trade
        trades1 = [Trade('test',1,1,1),Trade('test2',2,2,2)]
        trades2 = [Trade('test3',1,1,1),Trade('test4',2,2,2)]
        import os
        save_last('test_save_last.txt',{},20010101,20050101,20041220)
        save_last('test_save_last.txt',{'t1':trades1,'t2':trades2},20010101,20050101,20041220)
        os.remove('test_save_last.txt')

    def test_save_mm_configs(self):
        config = BaseObject(name='test',mm=(100,80,80,5))
        import os
        save_mm_configs('test_save_mm_configs.txt',[],20010101,20050101)
        save_mm_configs('test_save_mm_configs.txt',[config,config],20010101,20050101)
        os.remove('test_save_mm_configs.txt')

    def test_save_merged(self):
        result = BaseObject(RPR=1,CSHARP=0,AVGRANGE=(1,2),MAXRANGE=(3,4),income_rate=123,pre_ev=[1,2],g_ev=[3,4])
        strade='test strade'
        import os
        save_merged('test_save_merged.txt',result,strade,20010101,20050101)
        os.remove('test_save_merged.txt')

    def test_dlimit(self):
        dummy = range(45)
        a = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        b = np.array([dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        sdata = {'sa':sa,'sb':sb}
        print sum(a)
        self.assertEquals(7920,np.sum(a))
        dlimit(sdata.values(),0)
        self.assertEquals(7920,np.sum(a))
        dlimit(sdata.values(),20)
        self.assertEquals(7920+210*5,np.sum(a))
        dlimit(sdata.values(),100)
        self.assertEquals(4500*5+990*3,np.sum(a))
        self.assertTrue(True)

    def test_prepare_all(self):#只测试通路
        import wolfox.fengine.core.shortcut as sc
        fold = sc.prepare_catalogs
        sc.prepare_catalogs = lambda s:([],[])
        dates,sdata,idata,catalogs = prepare_all(20010101,20010102,['SH600000'],['SH000001'])
        #print sc.prepare_catalogs,fold
        sc.prepare_catalogs = fold
        self.assertTrue(True)

    def test_rate_mfe_mae(self):
        self.assertEquals((1,0,0,0),rate_mfe_mae({}))        
        s1 = BaseObject(mfe_sum=100,mae_sum=50,mm_count=10)
        s2 = BaseObject(mfe_sum=1000,mae_sum=500,mm_count=20)
        self.assertEquals((2000,1100,550,30),rate_mfe_mae({'s1':s1,'s2':s2}))
        s3 = BaseObject(mfe_sum=100,mae_sum=0,mm_count=10)
        s4 = BaseObject(mfe_sum=1000,mae_sum=0,mm_count=20)
        self.assertEquals((1000000000,1100,0,30),rate_mfe_mae({'s3':s3,'s4':s4}))

    #------------------------------------------------------------------------------------------------
    #以下是已经deprecated的函数的测试，也相当于deprecated
    def test_normal_calc_template_deprecated(self):
        a = np.array([(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14)])
        b = np.array([(11,12),(13,14),(15,16),(17,18),(19,110),(111,112),(113,114)])
        sa = CommonObject(id=3,code='test1',transaction=a)
        sb = CommonObject(id=3,code='test2',transaction=b)
        dates = np.array([1,2])
        sdata = {'sa':sa,'sb':sb}
        fbuy = lambda x:np.array([1,0])
        fsell = lambda x,y:np.array([0,1])
        ftrade = lambda x,y,z,a:(1,2)
        normal_calc_template_deprecated(sdata,dates,fbuy,fsell,ftrade)
        self.assertTrue(True)
        #测试异常包容性
        def fbuy(x): raise Exception
        se1 = CommonObject(id=3,code='test exception catch 1',transaction=a)
        se2 = CommonObject(id=3,code='test exception catch 2',transaction=b)
        dates = np.array([1,2])
        edata = {'se1':se1,'se2':se2}
        normal_calc_template_deprecated(edata,dates,fbuy,fsell,ftrade)
        self.assertTrue(True)

    def test_trade_func_deprecated(self):
        from wolfox.fengine.core.shortcut import _trade_func_deprecated
        a = np.array([(1,2,1),(3,4,3),(5,6,5),(7,8,7),(9,10,4),(11,12,3),(13,14,5)])      
        sa = CommonObject(id=3,code='TEST',transaction=a)        
        dates = np.array([1,2,3])
        sb = np.array([0,1,0])
        ss = np.array([0,0,1])
        _trade_func_deprecated(dates,sa,sb,ss,prepare_func=B0S0)
        self.assertTrue(True)
        #空测试
        a = np.array([(),(),(),(),(),(),()])        
        sa = CommonObject(id=3,code='TEST',transaction=a)        
        dates = np.array([])
        sb = np.array([])
        ss = np.array([])
        _trade_func_deprecated(dates,sa,sb,ss,prepare_func=B0S0)
        self.assertTrue(True)
 
    def test_normal_trade_func_deprecated(self):   #只测试通路
        a = np.array([(1,2,1),(3,4,3),(5,6,5),(7,8,7),(9,10,4),(11,12,3),(13,14,5)])      
        sa = CommonObject(id=3,code='TEST',transaction=a)        
        dates = np.array([1,2,3])
        sb = np.array([0,1,0])
        ss = np.array([0,0,1])
        normal_trade_func_deprecated(dates,sa,sb,ss)
        self.assertTrue(True)

    def test_trade_funcs(self):   #测试全部bMsN_trade_func,只测试通路
        a = np.array([(1,2,1),(3,4,3),(5,6,5),(7,8,7),(9,10,4),(11,12,3),(13,14,5)])      
        sa = CommonObject(id=3,code='TEST',transaction=a)
        dates = np.array([1,2,3])
        sb = np.array([0,1,0])
        ss = np.array([0,0,1])
        dummy_trade_func_deprecated(dates,sa,sb,ss)
        b0s0_trade_func_deprecated(dates,sa,sb,ss)
        b0s1_trade_func_deprecated(dates,sa,sb,ss)
        b1s0_trade_func_deprecated(dates,sa,sb,ss)
        b1s1_trade_func_deprecated(dates,sa,sb,ss)
        self.assertTrue(True)


if __name__ == "__main__":
    import logging
    logging.basicConfig(filename="test.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    unittest.main()
