from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

def image_upload(instance, filename):
    return f'uploads/{uuid.uuid4().hex.upper()}.png'

# Define un usuario de la aplicación, el cual tendrá una clave pública 
# guardada en el servidor
class User(AbstractUser):
    public_key = models.TextField(null=True, blank=True)

# Define las imágenes a subir en el tablero de la página principal
class Image(models.Model):
    image = models.ImageField(upload_to=image_upload)
    timestamp = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
