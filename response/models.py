from django.db import models
from mongoengine import *
from wechat_server.settings import DBNAME
import logging

# Create your models here.
logger = logging.getLogger('django')
try:
	logger.info('Connecting to wechat_db')
	connect('wechat_db',
        host='mongodb://dbadmin:wechatdb4supervessel@182.92.229.136/wechat_db',
        port=27017)
except:
	logging.debug("DB remote connect error")


class Users(Document):
    wechat_user_id = StringField(max_length = 120, required = True)
    supervessel_account = StringField(max_length = 120, required = False)
    openstack_tenant_id = StringField(max_length = 100, required = False)
    user_property = StringField(max_length = 120, required = True)
    active_level = IntField(required = True)
    experience_points = IntField(required = True)
    
class virtualmachines(Document):
    vm_id = StringField(max_length = 100, required = True)
    vm_name = StringField(max_length = 1000, required = True)
    supervessel_account = StringField(max_length = 120, required = True)
#    cpu_usage = IntField(required = False)
    cpu_usage_list = ListField(IntField(required = False))
#    network_usage = IntField(required = False)
    network_usage_out_list = ListField(IntField(required = False))
    network_usage_in_list = ListField(IntField(required = False))
    start_date = ListField(IntField(required = False))
