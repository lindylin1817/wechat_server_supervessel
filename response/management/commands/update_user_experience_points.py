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
	logger.info("Finish the user experience_points update")

    user_list = Users.objects()
    

    for the_user in user_list:
        experience_points = the_user.experience_points
        if (not the_user.experience_points):
            experience_points = 1
        logger.info("old points: " + str(experience_points))

        this_user_vms = virtualmachines.objects(
            supervessel_account = the_user.supervessel_account)
        for this_user_vm in this_user_vms:        
            experience_points = experience_points + int(this_user_vm.cpu_usage_list[-1])
        Users.objects(supervessel_account=the_user.supervessel_account).update_one(
            set__experience_points=experience_points)
        logger.info(experience_points)




    
