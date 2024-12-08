from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib import messages
from django.db import models
from .models import Image
from .forms import RegistroForm
from .covert import generar_claves, encriptar_mensaje, desencriptar_mensaje, ocultar_mensaje_imagen, extraer_mensaje_imagen
User = get_user_model()


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

			login(request, user)
			messages.success(request, "¡Registro exitoso! Has iniciado sesión.")
			return render(request, 'app/home.html', {'private_key': clave_privada})
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
	if request.method == 'GET':
		private_key = request.GET.get("private_key")
		print(private_key)
		images = Image.objects.all().order_by("-timestamp")
		decoded_images = []

		for image in images:
			if private_key:
				image_message = extraer_mensaje_imagen(image.image.path, image.length)
				if decoded_message := desencriptar_mensaje(private_key, image_message):
					image.decoded_message = decoded_message
			decoded_images.append(image)

		# images = Image.objects.all().order_by("-timestamp")
		return render(request, "app/home.html", {"images": decoded_images})

	if request.method == "POST":
		receiver_name = request.POST.get("username")
		message = f"De {request.user.username}:\n{request.POST.get('message')}"
		image_file = request.FILES.get("image")

		recipient = User.objects.get(username=receiver_name)
		encrypted_message = encriptar_mensaje(recipient.public_key, message)

		if image_file:
			ocultar_mensaje_imagen(image_file, encrypted_message)

		return redirect("home")
