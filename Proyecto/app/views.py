from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.core.files.base import ContentFile
from django.contrib import messages
from .forms import RegistroForm
from .models import Image as ImageModel
from .covert import *
from PIL import Image as PilImage
from random import randint
from io import BytesIO
User = get_user_model()


def convert_to_png(image_file):
	with PilImage.open(image_file) as img:
		img = img.convert("RGBA")
		buffer = BytesIO()
		img.save(buffer, format="PNG")
		buffer.seek(0)

		new_file = ContentFile(buffer.read())
		new_file.name = f"{image_file.name.split('.')[0]}.png"
		return new_file

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
			clave_privada, clave_publica = generar_claves()
			user.public_key = clave_publica
			user.save()
			clave_privada = clave_privada.replace('N RSA PRIVATE KEY-----', 'N RSA PRIVATE KEY-----<br>')
			clave_privada = clave_privada.replace('-----E', '<br>-----E')

			login(request, user)
			messages.success(request, "¡Registro exitoso! Has iniciado sesión.")
			request.session['private_key'] = clave_privada
			return redirect('home')
		else:
			messages.error(request, "Hubo un error en el formulario.")
			return render(request, 'app/register.html', {'form': form})

def login2(request):
	if request.method == 'GET':
		if request.user.is_authenticated:
			return redirect('home')
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
	if request.method == 'GET':
		private_key = request.session.pop('private_key', None)
		private_key_decode = request.GET.get('private_key_decode')
		images = ImageModel.objects.all().order_by('-timestamp')
		decoded_images = []

		for image in images:
			if private_key_decode:
				image_message = extraer_mensaje_imagen(image.image.path, image.length)
				if decoded_message := desencriptar_mensaje(private_key_decode, image_message):
					image.decoded_message = decoded_message.replace('\n', '<br>')
			decoded_images.append(image)

		context = {
			'images': decoded_images,
			'private_key': private_key,
			'private_key_decode': private_key_decode
		}
		return render(request, "app/home.html", context)

	if request.method == "POST":
		if request.POST.get('action') == 'clear_private_key':
			request.session.pop('private_key', None)
			return redirect('home')

		receiver_name = request.POST.get('username')
		message = f"De {request.user.username}:<br>{request.POST.get('message')}"
		image_file = request.FILES.get('image')

		if receiver_name:
			recipient = get_object_or_404(User, username=receiver_name)
			encrypted_message = encriptar_mensaje(recipient.public_key, message)
			if image_file:
				ocultar_mensaje_imagen(image_file, encrypted_message)
		else:
			if image_file:
				image_file = convert_to_png(image_file)
				image = ImageModel.objects.create(image=image_file, length=randint(0, 1024) * 8)
				image.save()

		return redirect("home")
