from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

def image_upload(instance, filename):
    return f'uploads/{uuid.uuid4().hex.upper()}.png'

class User(AbstractUser):
    public_key = models.TextField(null=True, blank=True)

class Image(models.Model):
    image = models.ImageField(upload_to=image_upload)
    timestamp = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
