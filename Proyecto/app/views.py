vistas para el chat
# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Mensaje
from .forms import MensajeForm
from .utils import cifrar_mensaje, descifrar_mensaje, ocultar_mensaje_imagen, extraer_mensaje_imagen, generar_clave, generar_hmac, verificar_hmac
import base64

def index(request):
	if request.method == 'GET':
		return render(request, 'app/chat.html')

@login_required
def chat(request, usuario_id):
    receptor = User.objects.get(id=usuario_id)
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            # Encriptamos el mensaje
            mensaje_original = form.cleaned_data['mensaje']
            clave_secreta = generar_clave()
            mensaje_cifrado = cifrar_mensaje(mensaje_original, clave_secreta)
            mensaje_base64 = base64.b64encode(mensaje_cifrado).decode()

            # Generamos el HMAC
            hmac_secreto = generar_hmac(mensaje_base64, clave_secreta)
            mensaje_completo = mensaje_base64 + hmac_secreto
            
            # Ocultamos el mensaje en la imagen
            imagen_path = "imagen_original.png"  # La imagen original
            ocultar_mensaje_imagen(imagen_path, mensaje_completo)
            
            # Guardamos en la base de datos (se guarda la imagen, pero solo el ID de la imagen o path)
            mensaje = Mensaje(remitente=request.user, receptor=receptor, mensaje=mensaje_completo)
            mensaje.save()
            return redirect('chat', usuario_id=usuario_id)
    else:
        form = MensajeForm()
    
    # Mostramos los mensajes enviados y recibidos
    mensajes = Mensaje.objects.filter(
        (models.Q(remitente=request.user) & models.Q(receptor=receptor)) | 
        (models.Q(remitente=receptor) & models.Q(receptor=request.user))
    ).order_by('timestamp')

    mensajes_descifrados = []
    for mensaje in mensajes:
        # Extraemos el mensaje y lo verificamos
        longitud_bits = len(mensaje.mensaje) * 8
        mensaje_extraido = extraer_mensaje_imagen(imagen_path, longitud_bits)
        
        # Extraemos el mensaje cifrado y el HMAC
        mensaje_cifrado_extraido = mensaje_extraido[:-64]
        hmac_extraido = mensaje_extraido[-64:]

        if verificar_hmac(mensaje_cifrado_extraido, hmac_extraido, clave_secreta):
            mensaje_descifrado = descifrar_mensaje(base64.b64decode(mensaje_cifrado_extraido), clave_secreta)
            mensajes_descifrados.append(mensaje_descifrado)
        else:
            mensajes_descifrados.append("Error: El HMAC no coincide. El mensaje ha sido alterado.")
    
    return render(request, 'chat.html', {'form': form, 'mensajes_descifrados': mensajes_descifrados, 'receptor': receptor})
