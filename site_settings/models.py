from django.db import models

# Create your models here.


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    logo = models.ImageField(
        upload_to="logo/users",
        default="default/default-user.jpg",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=15)
    short_description = models.TextField()
    facebook_url = models.URLField(blank=True, null=True, default="#")
    instagram_url = models.URLField(blank=True, null=True, default="#")

    class Meta:
        verbose_name = "SiteSettings"
        verbose_name_plural = "SiteSettings"
