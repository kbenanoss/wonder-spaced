from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from shortuuid.django_fields import ShortUUIDField

import os
import uuid

GENDER = (
    ("female", "Female"),
    ("male", "Male"),
)



def user_directory_path(instance, filename):
    user = None
    
    if hasattr(instance, 'user') and instance.user:
        user = instance.user

    if user:
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (user.id, ext)
        return 'user_{0}/{1}'.format(user.id, filename)
    else:
        # Handle the case when user is None
        # You can return a default path or raise an exception, depending on your requirements.
        # For example, return a path with 'unknown_user' as the user ID:
        ext = filename.split('.')[-1]
        filename = "%s.%s" % ('file', ext)
        return 'user_{0}/{1}'.format('file', filename)
    

    
class User(AbstractUser):
    username = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500)
    videos_purchased = models.IntegerField(default=0)
    worksheets_purchased = models.IntegerField(default=0)
    ebooks_purchased = models.IntegerField(default=0)
   

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return self.email

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        email_username, mobile = self.email.split('@')
        if self.full_name == "" or self.full_name == None:
             self.full_name = self.email
        if self.username == "" or self.username == None:
             self.username = email_username
        super(User, self).save(*args, **kwargs)
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='accounts/users', default='default/default-user.jpg', null=True, blank=True)
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    about = models.TextField( null=True, blank=True)
    gender = models.CharField(max_length=500, choices=GENDER, null=True, blank=True)
    country = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    newsletter = models.BooleanField(default=False)
    type = models.CharField(max_length=500, choices=GENDER, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")


    class Meta:
        ordering = ["-date"]

    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)
    
    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
             self.full_name = self.user.full_name
        
        super(Profile, self).save(*args, **kwargs)
    
    
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)