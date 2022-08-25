# =============================================================================
# import sys
# sys.path.append('../shared')
# import google_apis_client
# =============================================================================

# =============================================================================
# import sys
# sys.path.append('..')
# import doozcreds
# doozcreds.init('dooz') #loads values for ['s3_key_id', 's3_secret_key'] as env vars
# import boto3
# =============================================================================

#import os
import datetime
import pytz
import dateutil

class Doozer():
    def __init__(self, **kwargs):
        pass
    
    def get_data(self):
        pass
# =============================================================================
#         self.sheet_id = sheet_id
#         self.tab_name = tab_name
# =============================================================================
#        self.client = google_apis_client.GoogleSheetsClient(self.api_name, self.api_ver, 'service_account', self.scope, creds_file=creds_file)
# =============================================================================
#         self.client = FakeNewsClient()
# =============================================================================

class Doo():
    def __init__(self, **kwargs):
        self.pri = kwargs.get('pri')
        self.category = kwargs.get('category')
        self.who = kwargs.get('who')
        self.when = kwargs.get('when')
        self.when_end = kwargs.get('when_end')
        self.what = kwargs.get('what')

    def due(self):
        pass
    
    def daypart(self):
        if datetime.now().hour < 12:
            return ('AM','morning')
        else:
            return ('PM','evening')

    def conv_dtstr_to_dt(self, dtstr, from_tzname, to_tzname=None):
        '''
        For a given string in ISO8601 format in the timezone named from_tzname, converts it
        returns a TZ-AWARE object for that time. If to_tzname is supplied, converts the datetime
        to that timezone.
        
        conv_dtstr_to_dt('2019-12-25T12:35:19', 'US/Pacific', 'UTC')
        
        conv_dtstr_to_dt('2019-12-25T12:35:19', 'US/Pacific')

        '''
        try:
            from_tzobj = pytz.timezone(from_tzname)
            to_tzobj = pytz.timezone(to_tzname) if to_tzname else None
        except pytz.UnknownTimeZoneError:
            return None
        
        try:
            dt_naive = dateutil.parser.parse(dtstr.rstrip('Z')) # if time string is UTC 8601, should be specified in from_tzname
        except ValueError:
            return None

        dt_aware = from_tzobj.localize(dt_naive)
        if to_tzobj:
            return dt_aware.astimezone(to_tzobj)
        else:
            return dt_aware

class DooOnce(Doo):    
    def due(self):
        pass
    
class DooOver(Doo):    
    def __init__(self, **kwargs):
        super(DooOver, self).__init__(**kwargs)

#s3svc = boto3.resource('s3', aws_access_key_id=os.environ.get('s3_key_id'), aws_secret_access_key=os.environ.get('s3_secret_key')) #, region_name=None, api_version=None, use_ssl=True, verify=None, endpoint_url=None, aws_session_token=None, config=None)
#b = s3svc.Bucket('dooz')

# IDEAS for data structure

doo = { # a single to-do
        'pri': 1,
        'category': 'onetime',
        'doowho': 'Chris',
        'doowhen': '2020-01-03T16:19:44.112122',
        'doowhen_end': '2020-01-06T16:19:44.112122',
        'doowhat': 'Call for house contractor bids',
        }

doo_recur_pattern = {
        'recur_on': 'day', # day, daypart
        }
'''
is_recurring	 recurrence_days 	due_date	 pri
TRUE	2	4/1/2019	3

'''
#for bucket in s3svc.buckets.all():
#    print(bucket.name)

#data = open('test.jpg', 'rb')
#s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)

