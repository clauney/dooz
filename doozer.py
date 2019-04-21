import sys
#sys.path.append('../shared')
#import google_apis_client
sys.path.append('..')
import doozcreds
doozcreds.init('dooz') #loads values for ['s3_key_id', 's3_secret_key'] as env vars
import os
import boto3

#%%

class Dooz():
    def __init__(self, sheet_id, tab_name, creds_file):
        self.sheet_id = sheet_id
        self.tab_name = tab_name
#        self.client = google_apis_client.GoogleSheetsClient(self.api_name, self.api_ver, 'service_account', self.scope, creds_file=creds_file)
        self.client = FakeNewsClient()

class FakeNewsClient():
    def __init__(self, *args, **kwargs):
        self.datas = {}

class ToDooz(Dooz):
    aws_dyn_table = 'dooz'
    def get_doos(self, filters={}):
        pass


#%%
#s3svc = boto3.resource('s3', aws_access_key_id=os.environ.get('s3_key_id'), aws_secret_access_key=os.environ.get('s3_secret_key')) #, region_name=None, api_version=None, use_ssl=True, verify=None, endpoint_url=None, aws_session_token=None, config=None)
#b = s3svc.Bucket('dooz')
#%%

# IDEAS for data structure

doo_instance = {
        'catdoogory': 'instance',
        'whodoo': 'Chris',
        'doodate': '2019-03-20T16:19:44.112122',
        'doothis': 'Call for house contractor bids',
        'pri': 1

        }

doo_recur_pattern = {
        'catdoogory': 'instance',
        'whodoo': 'Chris',
        'doothis': 'Shower!',
        'pri': 1,
        'recur_on': 'day',
        }
'''
is_recurring	 recurrence_days 	due_date	 pri
TRUE	2	4/1/2019	3

'''
#for bucket in s3svc.buckets.all():
#    print(bucket.name)

#data = open('test.jpg', 'rb')
#s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)

