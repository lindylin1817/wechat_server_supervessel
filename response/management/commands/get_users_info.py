from django.core.management.base import BaseCommand, CommandError
import logging
import json
import memcache
import urllib2
from models import *

logger = logging.getLogger('django')
memCache_path = "127.0.0.1:11211"
USER_PRO = "user"

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
                except :
                    logger.error("Not supported character for username " 
                        + user_info_json["username"])
                else:
                    the_user = Users.objects(supervessel_account = user_info_json["username"])
                    if (not the_user):
                        the_user = Users(wechat_user_id = "n/a",
                            supervessel_account = user_info_json["username"], 
                            user_property = USER_PRO,
                            active_level = 0)
                        the_user.save()
                        logger.info("saved new user" + user_info_json["username"])
                    else:
                        logger.info("user " + user_info_json["username"] + " already exist")
#                    this_user_vms = virtualmachines.objects(supervessel_account = user_info_json['username'])
#                    active_level = the_user.active_level
#                    for this_user_vm in this_user_vms:
#                        active_level = active_level + this_user_vm.cpu_usage_list[-1]
#                    Users.objects(supervessel_account=user_info_json['username']).update_one(
#                        set__active_level=active_level)
#                    logger.info(active_level)




    
