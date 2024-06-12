# main/management/commands/generate_fake_data.py
from django.core.management.base import BaseCommand
from faker import Faker
from userauths.models import User
from main.models import Category, Lesson, Activity, Payment
from django.utils import timezone
import random


class Command(BaseCommand):
    help = "Generate fake data for models"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Generate fake categories
        categories = [Category.objects.create(name=fake.word()) for _ in range(5)]

        # Generate fake lessons
        lessons = []
        for category in categories:
            for _ in range(3):
                lesson_type = random.choice(["video", "worksheet", "ebook"])
                lesson = Lesson.objects.create(
                    title=fake.sentence(),
                    category=category,
                    lesson_type=lesson_type,
                    content=fake.paragraph(),
                    image=fake.image_url(),
                )
                lessons.append(lesson)

        # Generate fake users
        users = [
            User.objects.create(username=fake.user_name(), email=fake.email())
            for _ in range(10)
        ]

        # Generate fake activities
        activities = []
        for _ in range(20):
            user = random.choice(users)
            lesson = random.choice(lessons)
            activity = Activity.objects.create(
                user=user,
                lesson=lesson,
                purchase_date=fake.date_time_this_year(),
                image=fake.image_url(),
                description=fake.text(),
                activity_name=fake.word(),
            )
            activities.append(activity)

        # Generate fake payments
        for _ in range(30):
            user = random.choice(users)
            activity = random.choice(activities)
            Payment.objects.create(
                user=user,
                activity=activity,
                reference=fake.uuid4(),
                amount=fake.random_number(digits=4),
                date=timezone.now(),
                status=random.choice(["success", "pending", "failed"]),
            )

        self.stdout.write(self.style.SUCCESS("Fake data generated successfully."))
