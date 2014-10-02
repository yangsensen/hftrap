

class ContractSpecification():
    def __init__(self, *argv):
        self.min_price_increment_ = 1.0
        self.numbers_to_dollars_ = 1.0
        self.exch_source_ = "INVALID"
        self.min_order_size_ = 1
        if len(argv) == 4 :
            self.min_price_increment_ = (float)(argv[0])
            self.numbers_to_dollars_ = (float)(argv[1])
            self.exch_source_ = argv[2]
            self.min_order_size_ = (int)(argv[3])
            
class SecurityDefinitions():
    
    @staticmethod
    def GetContractMinPriceIncrement( shortcode, yymmdd):
        return
    
    @staticmethod
    def GetContractMinOrderSize(shortcode, yymmdd):
        return
    @staticmethod
    def GetTradeBeforeQuote(shortcode, date):
        return  # not necessary to  implement ??
    
    @staticmethod
    def GetContractExchSource(shortcode, date):
        return

    @staticmethod
    def GetConfToMarketUpdateMsecs(shortcode, date):
        return
    
    
            