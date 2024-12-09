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

# Convierte una imagen cargada por el usuario a formato PNG, haciendo uso de la librería
# PIL para convertir la imagen a formato RGBA y luego guardarla en dicho formato
def convert_to_png(image_file):
	with PilImage.open(image_file) as img:
		img = img.convert("RGBA")
		buffer = BytesIO()
		img.save(buffer, format="PNG")
		buffer.seek(0)

		new_file = ContentFile(buffer.read())
		new_file.name = f"{image_file.name.split('.')[0]}.png"
		return new_file

# Página por defecto de la aplicación, siendo esta el chat global,
# se necesita haber iniciado sesión
@login_required(login_url='/login/')
def index(request):
	if request.method == 'GET':
		return render(request, 'app/home.html')

# Permite a un nuevo usuario registrarse en la aplicación
def register(request):
	# Se muestra el formulario de registro
	if request.method == 'GET':
		form = RegistroForm()
		return render(request, 'app/register.html', {'form': form})

	# Una vez envía este formulario (POST), se genera su par de claves públicas y privadas RSA,
	# guardándose la clave pública automáticamente y redirigiendo al usuario a la página principal
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

# Permite a los usuarios iniciar sesión. Si el usuario proporciona credenciales
# válidas, se autentica y redirige a la página principal
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

# Permite a los usuarios cerrar sesión. Al ser llamada, el usuario es 
# desconectado y se redirige a la página de inicio de sesión
def logout2(request):
	logout(request)
	return redirect('login2')

# Muestra la página principal, donde los usuarios pueden ver las imágenes
# con mensajes ocultos y subir nuevas imágenes, siguiendo la lógica de
# "tablero de imágenes global" descrita anteriormente
@login_required(login_url='/login/')
def home(request):
	# Si el usuario realiza una solicitud GET, se muestran las imágenes en el tablero, y los mensajes
	# ocultos que se le han enviado si ingresa su clave privada en el formulario respectivo
	if request.method == 'GET':
		private_key = request.session.pop('private_key', None)
		private_key_decode = request.GET.get('private_key_decode')
		images = ImageModel.objects.all().order_by('-timestamp')
		decoded_images = []

		for image in images:
			if private_key_decode:
				image_message = extraer_mensaje_imagen(image.image.path, image.length)
				hmac = image_message[-64:]
				message = image_message[:-64]
				if decoded_message := desencriptar_mensaje(private_key_decode, message):
					decoded_message = decoded_message.replace('\n', '<br>')
					sender_name = decoded_message[3:decoded_message.find(':')]
					sender = get_object_or_404(User, username=sender_name)
					if verificar_hmac(message, hmac, sender.public_key):
						image.decoded_message = decoded_message
			decoded_images.append(image)

		context = {
			'images': decoded_images,
			'private_key': private_key,
			'private_key_decode': private_key_decode
		}
		return render(request, "app/home.html", context)

	# Si el usuario realiza una solicitud POST, puede subir una imagen con un mensaje cifrado oculto en
	# ella, el mensaje entonces se cifra con la clave pública del destinatario
	if request.method == "POST":
		# Si se presiona el botón 'refrescar' se recarga la página eliminando los mensajes
		# desencriptados o la clave privada que se muestra al registrarse
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
				ocultar_mensaje_imagen(image_file, encrypted_message, request.user.public_key)
		# En caso de no especificarse un destinatario, simplemente se sube la imagen
		# al tablero sin mensaje oculto alguno
		else:
			if image_file:
				image_file = convert_to_png(image_file)
				image = ImageModel.objects.create(image=image_file, length=randint(0, 1024) * 8)
				image.save()

		return redirect("home")
