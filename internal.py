# -*- coding: utf-8 -*-

#fengine内部引用类的集合

import wolfox.fengine.core.source as cs
import wolfox.fengine.core.d1 as d1
import wolfox.fengine.core.d1ex as d1e
import wolfox.fengine.core.d1idiom as d1id
import wolfox.fengine.core.d1indicator as d1in
import wolfox.fengine.core.d1catalog as d1c
import wolfox.fengine.core.d1kline as d1k
import wolfox.fengine.core.d1match as d1m
import wolfox.fengine.core.d2 as d2
import wolfox.fengine.core.pmanager as pm
import wolfox.fengine.core.mediator as mdtr
import wolfox.fengine.core.trade as trade
import wolfox.fengine.core.evaluate as ev
import wolfox.fengine.core.utils as utils

from wolfox.fengine.core.utils import fcustom,names,get_null_obj_number,get_obj_number
from wolfox.fengine.core.d1 import band,bor,gand,gor,greater,smooth,smooth2,roll0,rollx,cached_zeros,cached_ints
from wolfox.fengine.core.d1ex import ma,trend,strend,cross,sfollow,syntony,transform,msum2,scover,hour2day,devi
from wolfox.fengine.core.d1indicator import vap_pre,vap2_pre,svap_ma,svap2_ma,tracelimit,psy,emv,cmacd
from wolfox.fengine.core.d1idiom import up_under,upconfirm,downup,swingin,atr_seller,atr_seller_factory,atr_xseller_factory,sellers_wrapper
from wolfox.fengine.core.d2 import dispatch,cdispatch,posort,percent_sort,npercent,percent,nincrease,c_posort,d_posort,dummy_catalogs,sud,vud
from wolfox.fengine.core.base import BaseObject,CommonObject,get_all_catalogs
from wolfox.fengine.core.base import OPEN,CLOSE,HIGH,LOW,AVG,AMOUNT,VOLUME,T_SECTORS
from wolfox.fengine.core.d1catalog import calc_index,calc_indices_base,calc_indices_avg,catalog_signal,catalog_signal_cs,catalog_signal_cs_and,catalog_signal_c,catalog_signal_m
from wolfox.fengine.core.source import get_ref_dates,prepare_data,get_codes,get_codes_startswith,get_hour
from wolfox.fengine.core.d1match import make_trade_signal
from wolfox.fengine.core.trade import make_trades,last_trade
from wolfox.fengine.core.evaluate import evaluate,gevaluate,evaluate_all
from wolfox.fengine.core.mediator import Mediator,MM_Mediator,Mediator10,CMediator10,OMediator10,mediator_factory,oo_pricer,cl_pricer,ol_pricer,co_pricer
from wolfox.fengine.core.mediator import NMediator,NMediator10,CNMediator10,ONMediator10,nmediator_factory
from wolfox.fengine.core.pmanager import Position,AdvancedPosition,PositionManager,AdvancedPositionManager,AdvancedATRPositionManager,AdvancedATRPositionManager2000,StepPositionManager,AdvancedStepPositionManager,AdvancedATRStepPositionManager,AdvancedATRStepPositionManager2000,XDateManager
