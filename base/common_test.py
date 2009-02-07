# -*- coding: gbk -*-

import unittest
import wolfox.fengine.base.common as common

class ModuleTest(unittest.TestCase):
    pass

class TradeTest(unittest.TestCase):
    def test_normal(self):
        self.assertEquals(0,common.Trade(1,1,1000,0).ttax)        
        self.assertEquals(0,common.Trade(1,1,1000.0,0).ttax)    #�۸񸡵����Σ�ʵ����Ӧ���������
        self.assertEquals(8,common.Trade(1,1,1000,-1).ttax)
        self.assertEquals(8,common.Trade(1,1,1000,1).ttax)
        self.assertEquals(8,common.Trade(1,1,1040,1).ttax)
        self.assertEquals(9,common.Trade(1,1,1075,1).ttax)
        self.assertEquals(105,common.Trade(1,1,1050,1,10).ttax)
        self.assertEquals(10010,common.Trade(1,1,1001,1000,100).ttax)
        self.assertEquals(100,common.Trade(1,1,1001,10,100).ttax)
        self.assertEquals(11,common.Trade(1,1,1050,10,1000).ttax)
        str(common.Trade(1,1,1050,10,1000))
        strtest = str(common.Trade(1,1,1050,10,1000))  #����__repr__
        self.assertTrue(True)

    def test_set_volume(self):    #�Ѿ��̺���testNormal����
        pass 

    def test_calc(self):
        trade = common.Trade(1,1,1000,-12,100)
        self.assertEquals(1000*12 - 1000*12/100,trade.calc())
        trade = common.Trade(1,1,1000,12,100)
        self.assertEquals(-1000*12 - 1000*12/100,trade.calc())
        trade = common.Trade(1,1,1000,-1)
        self.assertEquals(1000 - 1000/125,trade.calc())
        trade = common.Trade(1,1,1000,1)
        self.assertEquals(-1000 - 1000/125,trade.calc())

    def test_balanceIt(self):
        trade1 = common.Trade(1,20050101,1000,1000,100)
        trade2 = common.Trade(1,20050101,800,500,100)
        trade3 = common.Trade(1,20050101,600,-500,100)
        trade4 = common.Trade(1,20050101,1200,-1000,100)
        self.assertEquals(71000,common.Trade.balanceit([trade1,trade2,trade3,trade4]))

class EvaluationTest(unittest.TestCase):
    def test_normal(self):   #ʵ���ϲ�����calcwinlost,sumrate
        trade = common.Trade(1,2,3,4)
        trade1 = common.Trade(1,1,1000,1000,100)
        trade2 = common.Trade(1,2,1500,-1000,100)
        trade3 = common.Trade(2,1,2000,1000,100)
        trade4 = common.Trade(2,2,1500,-1000,100)
        trade5 = common.Trade(3,1,2970,1000,100)
        trade6 = common.Trade(3,2,3030,-1000,100)
        ev = common.Evaluation([[trade1,trade2],[trade3,trade4],[trade5,trade6]])
        self.assertEquals([[trade1,trade2],[trade3,trade4],[trade5,trade6]],ev.matchedtrades)
        #����calcwinlost
        self.assertEquals(1,ev.wincount)
        self.assertEquals(470,ev.winamount)
        self.assertEquals(1,ev.lostcount)
        self.assertEquals(265,ev.lostamount)
        self.assertEquals(3,ev.count)
        self.assertEquals(205,ev.balance)
        self.assertEquals(1,ev.deucecount)
        #����ratesum��rateavg
        self.assertEquals(205,ev.ratesum)
        self.assertEquals(68,ev.rateavg)
        self.assertEquals(333,ev.winrate)
        strtest = str(ev) #����__repr__
        self.assertTrue(True)

    def test_sum_trades(self):
        trade1 = common.Trade(1,1,1000,1000,100)
        trade2 = common.Trade(1,2,1500,-1000,100)
        trade3 = common.Trade(1,3,2000,1000,100)
        trade4 = common.Trade(1,4,1500,-1000,100)
        trades = (trade1,trade2,trade3,trade4)
        self.assertEquals(3030000,common.Evaluation.sumtrades(trades))
    
    def test_sum_trades_zero(self):
        trade1 = common.Trade(1,1,0,1000,100)
        trade2 = common.Trade(1,2,1500,-1000,100)
        trades = (trade1,trade2)
        self.assertEquals(99999999,common.Evaluation.sumtrades(trades))

    def test_empty(self):    #����û���쳣
        ev = common.Evaluation([])
        self.assertEquals(0,ev.winrate)
        self.assertTrue(True)

    def test_lt_gt(self): #Ϊ�򵥣�ֱ���޸�����
        ev1 = common.Evaluation([])
        ev2 = common.Evaluation([])
        ev1.R = 100
        ev2.R = 101
        self.assertTrue(ev1 < ev2 and ev2 > ev1)


if __name__ == "__main__":
    unittest.main()
