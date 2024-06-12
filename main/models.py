# models.py
from userauths.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video'),
        ('worksheet', 'Worksheet'),
        ('ebook', 'Ebook'),
    ]
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='lessons', on_delete=models.CASCADE)
    lesson_type = models.CharField(choices=LESSON_TYPES, max_length=10, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='lesson_images/')

    def __str__(self):
        return self.title

class Activity(models.Model):
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='activities', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='activity_images/')
    description = models.TextField()
    activity_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.lesson}'

class Payment(models.Model):
    user = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='payments', on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.user} - {self.reference} - {self.status}'

