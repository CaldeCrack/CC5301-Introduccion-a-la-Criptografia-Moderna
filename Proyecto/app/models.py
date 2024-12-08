from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    public_key = models.TextField(null=True, blank=True)

class Image(models.Model):
    image = models.ImageField(upload_to='uploads/')
    timestamp = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
