from django.db import models
from django.contrib.auth.models import User

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, related_name="mensajes_enviados", on_delete=models.CASCADE)
    receptor = models.ForeignKey(User, related_name="mensajes_recibidos", on_delete=models.CASCADE)
    mensaje = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.remitente} a {self.receptor} en {self.timestamp}"
