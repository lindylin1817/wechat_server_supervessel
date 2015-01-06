from django.core.management.base import BaseCommand, CommandError
import logging
import urllib2
import json
from .basic import *

logger = logging.getLogger('django')
token_file = "/root/wechat_server/files/token_file.txt"

wechat_token = "mytoken"

class Command(BaseCommand):
    def handle(self, *args, **options):
	logger.info("Start to send message ...")

	wechat = WechatBasic(token=wechat_token)
        ACCESS_TOKEN = wechat.get_access_token()
	data = {"touser":"orJ1ruFQPF98rVxIFsP4HDpqt-V4", "msgtype":"text", "text": { "content":"Hello World" }}
	data_json = json.dumps(data)
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + ACCESS_TOKEN
        logger.info(url)
        request = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})
	f = urllib2.urlopen(request)
	response = f.read()
	logger.info(response)
	f.close




