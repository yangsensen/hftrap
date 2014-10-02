from CDef.defines import *
from basic_market_view import *
from normal_spread_manager import NormalSpreadManager
from CDef.security_definitions import SecurityDefinitions
from MarketAdapter.basic_market_view import BestBidAskInfo


#Keeping only 1 Level in the book
class OrderBook():  
    def __init__(self, bid_px, bid_sz, ask_px, ask_sz):
        self._bid_price_ = bid_px
        self._bid_size_ = bid_sz
        self._ask_price_ = ask_px
        self._ask_size_ = ask_sz
    
class PriceLevelInfo():
    def __init__(self, *argv):
        if len(argv) == 3 :
            self.limit_price_ = (float)(argv[0])
            self. limit_size_ = (int)(argv[1])
            self.limit_ordercount_ = (int)(argv[2])
        else :
            self.limit_price_ = 0.0
            self. limit_size_ = 0
            self.limit_ordercount_ = 0


class SecurityMarketView:
 
    def __init_(self, watch, shortcode, exchange_symbol, security_id):
        self.watch_ = watch
        self.min_price_increment_ = SecurityDefinitions.GetContractMinPriceIncrement(shortcode, watch.YYMMDD())
        self.min_order_size_ = SecurityDefinitions.GetContractMinOrderSize(shortcode, watch.YYMMDD())
        self.normal_spread_increments_ = NormalSpreadManager.GetNormalSpreadIncrements(watch.YYMMDD(), shortcode)
        self.normal_spread_ = 1
        self.is_ready_ = False
        self.computing_price_levels_ = False
        self.trade_before_quote_ = SecurityDefinitions.GetTradeBeforeQuote(shortcode,watch.YYMMDD())
        self.market_update_info_ = MarketUpdateInfo(shortcode, exchange_symbol,security_id, SecurityDefinitions.GetContractExchSource(shortcode, watch.YYMMDD()))
        self.trade_print_info_ = TradePrintInfo()
        self.l1_price_listeners = []
        self.l1_size_listeners = []
        self.onready_listeners_ = []
        self.price_type_subscribed = dict()
        self.use_order_level_book_ = False
        #following variables may not be needed
        self.conf_to_market_update_msecs_ = SecurityDefinitions.GetConfToMarketUpdateMsecs(shortcode, watch.YYMMDD())
        self.self_best_bid_ask_ = BestBidAskInfo()
        self.last_best_level_ = BestBidAskInfo()
        self.current_best_level_ = BestBidAskInfo()
        self.top_bid_level_to_mask_trades_on_ = 0
        self.top_ask_level_to_mask_trades_on_ = 0
        self.prev_bid_was_quote_ = True
        self.prev_ask_was_quote_ = True
        self.running_hit_size_vec_ = []
        self.running_lift_size_vec_ = []
        self.l1_changed_since_last_ = False
        self.last_message_was_trade_ = False
        self.min_priority_size_ = 10
        self.max_priority_size_ = 500
        self.suspect_book_correct_ = False
        self.using_order_level_data_ = False
        self.skip_listener_notification_end_time_ = 0.0
        self.process_market_data_ = True
        self.initial_book_constructed_ = False
        self.int_price_bid_book_ = []
        self.int_price_ask_book_ = []
        self.int_price_bid_skip_delete_ = []
        self.int_price_ask_skip_delete_ = []
        self.indexed_bid_book_ = []
        self.indexed_ask_book_ = []
        self.base_bid_index_ = 0
        self.base_ask_index_ = 0
        self.last_base_bid_index_ = 0
        self.last_base_ask_index_ = 0
        self.this_int_price_ = 0
        self.last_msg_was_quote_ = False
        self.running_lift_size_ = 0
        self.running_hit_size_ = 0
        self.lift_base_index_ = 0
        self.hit_base_index_ = 0
        self.last_raw_message_sequnece_applied_ = 0
        self.price_type_subscribed_["MktSizeWPrice"] = False
        self.normal_spread_ = self.normal_spread_increments_ * self.min_price_increment_
        self.running_hit_size_vec_ = []
        self.running_lift_size_vec_ = []
        i=0
        while i < DEF_MARKET_DEPTH :
            self.running_hit_size_vec_.append(0)
            self.running_lift_size_vec_.append(0)
            i = i+1
      
    def __eq__(self, obj):
        return self.shortcode() == obj.shortcode()
    
    def shortcode(self):
        return self.market_update_info_.shortcode_
    
    def secname(self):
        return self.market_update_info_.secname_
    
    def security_id(self):
        return self.market_update_info_.security_id_

    def min_price_increment(self):
        return self.min_price_increment_
    
    def  min_order_size(self):
        return self.min_order_size_
    
    def normal_spread_increments(self):
        return self.normal_spread_increments_
    
    def normal_spread(self):
        return self.normal_spread_
    
    def spread_increments(self):
        return self.market_update_info_.spread_increments_
    
    def SpreadWiderThanNormal(self):
        return self.market_update_info_.spread_increments_ > self.normal_spread_increments_
    
    def UseOrderLevelBook(self):
        return self.use_order_level_book_
    
    def SetUseOrderLevelBook(self):
        self.use_order_level_book_ = True
        
    def UnsetUseOrderLevelBook(self):
        self.use_order_level_book_ = False
            
    def subscribe_price_type (self, t_new_listener_, t_price_type_ ) :
        res = True
        if t_price_type_ == "MktSizeWPrice":
            self.price_type_subscribed[t_price_type_] = True
            if t_new_listener_ is not None :
                if not self.l1_price_listeners.__contains__(t_new_listener_) :
                    self.l1_price_listeners.append(t_new_listener_)
                if not self.l1_size_listeners.__contains__(t_new_listener_) :
                    self.l1_size_listeners.append(t_new_listener_)
        else :
            res = False
        return res
    
    def subscribe_L1_Only(self,t_new_listener_ ):
        if not self.l1_price_listeners.__contains__(t_new_listener_) :
            self.l1_price_listeners.append(t_new_listener_)
        if not self.l1_size_listeners.__contains__(t_new_listener_) :
            self.l1_size_listeners.append(t_new_listener_)
        
    def subscribe_OnReady(self, t_new_listener_):
        if not self.onready_listeners_.__contains__(t_new_listener_) :
            self.onready_listeners_.append(t_new_listener_)
        
    def OnL1PriceUpdate(self):
        self.UpdateL1Prices()
        self.NotifyL1PriceListeners()
        self.NotifyOnReadyListeners()
       
    def UpdateL1Prices(self):
        self.market_update_info_.mkt_size_weighted_price_ = ( self.market_update_info_.bestbid_price_ * self.market_update_info_.bestask_size_ + self.market_update_info_.bestask_price_ * self.market_update_info_.bestbid_size_ ) / ( self.market_update_info_.bestbid_size_ + self.market_update_info_.bestask_size_ ) ;

    def OnL1SizeUpdate(self):
        return

    def NotifyL1PriceListeners(self):
        return
    
    def NotifyOnReadyListeners(self):
        return
    
    def OnL1Trade (self, trade_price, trade_size, trade_type):
        return
    
    def OnTrade (self, trade_price, trade_size, trade_type):
        return
    
    def Uncross(self):
        return
    
    def ShowMarket(self):
        return
    
    def isL1Valid(self):
        return
    
    
    

    