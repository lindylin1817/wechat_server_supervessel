from django.core.management.base import BaseCommand, CommandError
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    def handle(self, *args, **options):
	logger.info("I'm here")
	self.stdout.write("I'm here")


