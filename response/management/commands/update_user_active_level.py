from django.core.management.base import BaseCommand, CommandError
import logging
import json
import memcache
import urllib2
from models import *

logger = logging.getLogger('django')
memCache_path = "127.0.0.1:11211"

class Command(BaseCommand):
    def handle(self, *args, **options):
	logger.info("Finish the user active level update")

    user_list = Users.objects()

    active_level_days = 30
    
    for the_user in user_list:
        this_user_vms = virtualmachines.objects(supervessel_account = the_user.supervessel_account)
        active_level = 0
        for this_user_vm in this_user_vms:
            if (len(this_user_vm.cpu_usage_list <= active_level_days)):
                active_level = active_level + sum(this_user_vm.cpu_usage_list)
            else:
                active_level = active_level + 
                        sum(this_user_vm.cpu_usage_list[(-1 - active_level_days) : -1])
#            active_level = active_level + this_user_vm.cpu_usage_list[-1]
        Users.objects(supervessel_account=the_user.supervessel_account).update_one(
            set__active_level=active_level)
        logger.info(active_level)




    
