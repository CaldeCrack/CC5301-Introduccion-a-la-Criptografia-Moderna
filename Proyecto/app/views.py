from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.db import models
from .models import *
from .forms import MensajeForm, RegistroForm
from .covert import cifrar_mensaje, descifrar_mensaje, ocultar_mensaje_imagen, generar_clave, generar_hmac, verificar_hmac
import base64

SECRET_KEY_CIFRADO = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

@login_required(login_url='/login/')
def index(request):
	if request.method == 'GET':
		return render(request, 'app/home.html')

def register(request):
	if request.method == 'GET':
		form = RegistroForm()
		return render(request, 'app/register.html', {'form': form})

	if request.method == 'POST':
		form = RegistroForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "¡Registro exitoso! Has iniciado sesión.")
			return redirect('login2')
		else:
			messages.error(request, "Hubo un error en el formulario.")
			return render(request, 'app/register.html', {'form': form})

def login2(request):
	if request.method == 'GET':
		return render(request, 'app/login.html')

	if request.method == 'POST':
		form = RegistroForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			messages.success(request, "¡Has iniciado sesión correctamente!")
			return redirect('home')
		else:
			messages.error(request, "Nombre de usuario o contraseña incorrectos.")
			return render(request, 'app/login.html', {'form': form})

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
	if receptor.id == request.user.id:
		return redirect('home')

	# Asegurar un orden consistente, por ejemplo, siempre ordenamos por id:
	user1, user2 = sorted([request.user, receptor], key=lambda u: u.id)

	# Intentar obtener la clave
	chat_key, created = ChatKey.objects.get_or_create(
		usuario1=user1,
		usuario2=user2,
		defaults={'clave': generar_clave()}
	)

	clave_secreta = chat_key.clave  # Esto es la clave compartida para este par

	if request.method == 'POST':
		form = MensajeForm(request.POST)
		if form.is_valid():
			mensaje_original = form.cleaned_data['mensaje']
			mensaje_cifrado = cifrar_mensaje(mensaje_original, clave_secreta)
			mensaje_base64 = base64.b64encode(mensaje_cifrado).decode()
			hmac_secreto = generar_hmac(mensaje_base64, clave_secreta)
			mensaje_completo = mensaje_base64 + hmac_secreto

			# Ocultamos el mensaje en la imagen
			imagen_path = "imagen_original.png"
			ocultar_mensaje_imagen(imagen_path, mensaje_completo)

			# Guardar en la base de datos
			mensaje = Mensaje(remitente=request.user, receptor=receptor, mensaje=mensaje_completo)
			mensaje.save()
			return redirect('chat', usuario_id=usuario_id)
	else:
		form = MensajeForm()

	mensajes = Mensaje.objects.filter(
		(models.Q(remitente=request.user) & models.Q(receptor=receptor)) |
		(models.Q(remitente=receptor) & models.Q(receptor=request.user))
	).order_by('timestamp')

	mensajes_descifrados = []
	for mensaje in mensajes:
		# Evitamos volver a extraer de la imagen en cada mensaje, ya que tenemos mensaje_completo en la BD
		mensaje_completo = mensaje.mensaje
		mensaje_cifrado_extraido = mensaje_completo[:-64]
		hmac_extraido = mensaje_completo[-64:]

		if verificar_hmac(mensaje_cifrado_extraido, hmac_extraido, clave_secreta):
			mensaje_descifrado = descifrar_mensaje(base64.b64decode(mensaje_cifrado_extraido), clave_secreta)
			mensajes_descifrados.append({'content': mensaje_descifrado, 'sender': mensaje.remitente.id})
		else:
			mensajes_descifrados.append({'content': "Error: El HMAC no coincide. El mensaje ha sido alterado.", 'sender': mensaje.remitente.id})

	print(mensajes_descifrados)
	return render(request, 'app/chat.html', {'form': form, 'mensajes_descifrados': mensajes_descifrados, 'receptor': receptor})
