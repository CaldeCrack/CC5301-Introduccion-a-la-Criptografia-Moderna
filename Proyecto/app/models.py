from django.db import models
from django.contrib.auth.models import User

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, related_name="mensajes_enviados", on_delete=models.CASCADE)
    receptor = models.ForeignKey(User, related_name="mensajes_recibidos", on_delete=models.CASCADE)
    mensaje = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.remitente} a {self.receptor} en {self.timestamp}"

class ChatKey(models.Model):
    usuario1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatkeys_usuario1')
    usuario2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatkeys_usuario2')
    clave = models.BinaryField()

    class Meta:
        unique_together = ('usuario1', 'usuario2')

    def __str__(self):
        return f"ChatKey entre {self.usuario1.username} y {self.usuario2.username}"