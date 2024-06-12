# activities/management/commands/delete_fake_data.py
from django.core.management.base import BaseCommand
from site_settings.models import SiteSettings

class Command(BaseCommand):
    help = 'Delete all fake data'

    def handle(self, *args, **kwargs):
        # Delete all instances of your models
        SiteSettings.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all fake data'))