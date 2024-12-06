from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.db import models
from .models import Mensaje
from .forms import MensajeForm, RegistroForm
from .covert import cifrar_mensaje, descifrar_mensaje, ocultar_mensaje_imagen, extraer_mensaje_imagen, generar_clave, generar_hmac, verificar_hmac
import base64

@login_required(login_url='/login/')
def index(request):
	if request.method == 'GET':
		return render(request, 'app/home.html')

def register(request):
	if request.method == 'POST':
		form = RegistroForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "¡Registro exitoso! Has iniciado sesión.")
			return redirect('chat')
		else:
			messages.error(request, "Hubo un error en el formulario.")
	else:
		form = RegistroForm()

	return render(request, 'app/register.html', {'form': form})

def login2(request):
	if request.method == 'GET':
		return render(request, 'app/login.html')

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			messages.success(request, "¡Has iniciado sesión correctamente!")
			return redirect('home')
		else:
			messages.error(request, "Nombre de usuario o contraseña incorrectos.")

def logout2(request):
	logout(request)
	return redirect('login2')


@login_required(login_url='/login/')
def home(request):
	usuarios = User.objects.exclude(id=request.user.id)
	return render(request, 'app/home.html', {'usuarios': usuarios})

@login_required(login_url='/login/')
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
	
	return render(request, 'app/chat.html', {'form': form, 'mensajes_descifrados': mensajes_descifrados, 'receptor': receptor})
