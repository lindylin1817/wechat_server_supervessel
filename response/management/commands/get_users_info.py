from django.core.management.base import BaseCommand, CommandError
import logging
import json
import memcache
import urllib2

logger = logging.getLogger('django')
memCache_path = "127.0.0.1:11211"

class Command(BaseCommand):
    def handle(self, *args, **options):
	logger.info("Start to users information and put into memcache")

    try:
        mc = memcache.Client([memCache_path],debug=True)
        request = urllib2.Request(
                "https://www.ptopenlab.com/cloudlab/api/user/account")
    except HTTPError, e:
        logger.error("The server couldn't fulfill the request")
        logger.error("Error code is ", e.code)
    except URLError, e:
        logger.error("Failed to reach server")
        logger.error("Reasons ", e.reason)
    else:
	logger.info("Got the information ")
        try:
            response = urllib2.urlopen(request)
        except URLError, e:
            if hasattr(e, 'reason'):
                logger.error("We failed to reach a server.")
                logger.error("Reason: ", e.reason)
            elif hasattr(e, 'code'):
                logger.error("The server couldn/'t fulfill the request.")
                logger.error("Error code: ", e.code)
        else:
            users_info = response.read()
#            logger.info(users_info)

            users_info_json = json.loads(users_info)
            for user_info_json in users_info_json:
		try:
                    mc.set(str(user_info_json["username"]), user_info_json)
		except:
		    logger.error("Not supported characters in user name :" +
			user_info_json["username"])

    
