from django.db import models
from mongoengine import *
from wechat_server.settings import DBNAME

# Create your models here.

connect(DBNAME)

class Users(Document):
    wechat_user_id = StringField(max_length = 120, required = True)
    supervessel_account = StringField(max_length = 120, required = False)


