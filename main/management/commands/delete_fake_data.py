# activities/management/commands/delete_fake_data.py
from django.core.management.base import BaseCommand
from main.models import Activity, Lesson, Category
from userauths.models import User


class Command(BaseCommand):
    help = 'Delete all fake data'

    def handle(self, *args, **kwargs):
        # Delete all instances of your models
        Lesson.objects.all().delete()
        Activity.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all fake data'))
