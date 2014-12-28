from django.db import models
from mongoengine import *
from wechat_server.settings import DBNAME

# Create your models here.

connect(DBNAME)

class Users(Document):
    wechat_user_id = StringField(max_length = 120, required = True)
    supervessel_account = StringField(max_length = 120, required = False)
    openstack_tenant_id = StringField(max_length = 100, required = False)
    
class virtualmachines(Document):
    vm_id = StringField(max_length = 100, required = True)
    vm_name = StringField(max_length = 1000, required = True)
    supervessel_account = StringField(max_length = 120, required = True)
    cpu_usage = IntField(required = False)
    network_usage = IntField(required = False)
