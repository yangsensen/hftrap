from time import gmtime
import time
from ExternalData.external_time_listener import ExternalTimeListener

'''
TODO: (1) Rename YYMMDD
'''

class Watch(ExternalTimeListener):
    
    def __init__(self, _trading_date_):
        self.trading_date_ = _trading_date_
        self.tv_sec_ = 0
        self.tv_usec_ = 0
        self.msecs_from_midnight_ = 0
#        self.prev_midnight_sec_ = 0
        self.big_time_period_listener_vec_ = [] # TimePeriodListener
        
    def tv(self):
        return self.tv_sec_
        
    def OnTimeReceived(self, _tv_sec_, _tv_usec_):
#         if (self.tv_sec_ == 0):
#             t_time = gmtime(_tv_sec_)
#             t_date = str(t_time.tm_year)+('0'+str(t_time.tm_mon))[-2:]+('0'+str(t_time.tm_mday))[-2:]
#             if (not t_date == self.trading_date_):
#                 print 'Warning: Trading Date not equal to Time Received'
#             self.msecs_from_midnight_ = (_tv_sec_ % 86400) * 1000
#             self.prev_midnight_msec_ = _tv_sec_ * 1000 - self.msecs_from_midnight_
#             self.tv_sec_ = _tv_sec_
#             self.tv_usec_ = _tv_usec_
#         else:
#             if (_tv_sec_ > self.tv_sec_ or (_tv_sec_ == self.tv_sec_ and _tv_usec_ > self.tv_usec_)):
#                 self.msecs_from_midnight_ = _tv_sec_ * 1000 + _tv_usec_ / 1000 - self.prev_midnight_msec_
#                 self.tv_sec_ = _tv_sec_
#                 self.tv_usec_ = _tv_usec_
#         
#         aashay_output = GetMsecsFromEpoch(_tv_sec_, _tv_usec_)
#         if (not aashay_output == self.msecs_from_midnight_):
#             print aashay_output
#             print self.msecs_from_midnight_
        self.tv_sec_ = _tv_sec_
        self.tv_usec_ = _tv_usec_
        self.msecs_from_midnight_ = Watch.GetMsecsFromEpoch(_tv_sec_, _tv_usec_)
        
    def GetMsecsFromMidnight(self):
        return self.msecs_from_midnight_
    
    def SubscribeBigTimePeriod(self, _this_listener_):
        if _this_listener_ is not None:
            if not self.big_time_period_listener_vec_.__contains__(_this_listener_):
                self.big_time_period_listener_vec_.append(_this_listener_)
                
    def TradingDate(self):
        return self.trading_date_
    
    # It takes the utc_time in 4 digit, and convert into total seconds from midnight    
    @staticmethod
    def GetMSecsFromUTC(utc_time):
        hr = (int)(utc_time/100)
        mins = (int)(utc_time%100)
        secs = hr * 60 * 60 + mins *60
        return secs*1000

    #return milli seconds from midnight
    @staticmethod
    def GetMsecsFromEpoch(_tv_sec_, _tv_usec_):
        epoch_time = _tv_sec_ + float(_tv_usec_) / 1000000
        msecs = int(1000*(epoch_time - (int)(epoch_time)))
        t = time.gmtime(epoch_time)
        hr = t.tm_hour
        mins = t.tm_min
        secs = t.tm_sec
        total_secs = hr*60*60 + mins *60 + secs
        total_msecs = total_secs * 1000 + msecs
        return total_msecs