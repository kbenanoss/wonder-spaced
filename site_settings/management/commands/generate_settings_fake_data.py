import random
from faker import Faker
from django.core.management.base import BaseCommand
from site_settings.models import SiteSettings


class Command(BaseCommand):
    help = "Generate fake data for site settings"

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(1):  # Change 10 to the desired number of fake records
            site_settings = SiteSettings(
                site_name=fake.company(),
                address=fake.address(),
                email=fake.email(),
                logo="logos/logo.png",  # Set a default logo path or leave it empty
                phone_number=fake.phone_number(),
                short_description=fake.text(),
                facebook_url=fake.uri(),
                instagram_url=fake.uri(),
            )
            site_settings.save()
            self.stdout.write(self.style.SUCCESS("Fake data created successfully!"))
