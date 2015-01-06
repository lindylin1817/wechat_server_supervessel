from django.core.management.base import BaseCommand, CommandError
import logging
import urllib2
import json

logger = logging.getLogger('django')
token_file = "/root/wechat_server/files/token_file.txt"
APPSECRET = "1322de6faef0680c4ee3cd2f922e58fb"  #for Wechat
APPID = "wx882aec4c013c1ab0" #for Wechat

class Command(BaseCommand):
    def handle(self, *args, **options):
	logger.info("Start to get token ...")

        try:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + APPID +"&secret=" + APPSECRET
            logger.info(url)
            request = urllib2.Request(url)
        except urllib2.HTTPError, e:
            logger.error("The server couldn't fulfill the request")
            logger.error("Error code is ", e.code)
        except urllib2.URLError, e:
            logger.error("Failed to reach server")
            logger.error("Reasons ", e.reason)
        else:
            try:
                response = urllib2.urlopen(request)
            except urllib2.URLError, e:
                if hasattr(e, 'reason'):
                    logger.error("We failed to reach a server.")
                    logger.error("Reason: ", e.reason)
                elif hasattr(e, 'code'):
                    logger.error("The server couldn/'t fulfill the request.")
                    logger.error("Error code: ", e.code)
            else:
                token_info = response.read()
                logger.info(token_info)
                stream = json.loads(token_info)
                ACCESS_TOKEN = stream["access_token"]
		file_obj = open(token_file,"w")
		file_obj.write(ACCESS_TOKEN)
		file_obj.close




