from django.core.files.base import ContentFile
from .models import Image as image
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from io import BytesIO
from PIL import Image
import base64, uuid

def generar_claves():
	clave = RSA.generate(2048)
	clave_privada = clave.export_key().decode('utf-8')
	clave_publica = clave.publickey().export_key().decode('utf-8')
	return clave_privada, clave_publica

def encriptar_mensaje(clave_publica_pem, mensaje):
	clave_publica = RSA.import_key(clave_publica_pem)
	cipher = PKCS1_OAEP.new(clave_publica)
	encrypted_message = cipher.encrypt(mensaje.encode('utf-8'))
	return base64.b64encode(encrypted_message).decode('utf-8')

def desencriptar_mensaje(clave_privada_str, mensaje):
	try:
		clave_privada = RSA.import_key(clave_privada_str)
		cifrado = PKCS1_OAEP.new(clave_privada)
		mensaje_encriptado = base64.b64decode(mensaje)
		mensaje_desencriptado = cifrado.decrypt(mensaje_encriptado)
		return mensaje_desencriptado.decode('utf-8')
	except (ValueError, TypeError) as e:
		return None

def ocultar_mensaje_imagen(imagen, mensaje):
	mensaje_bin = ''.join(format(ord(i), '08b') for i in mensaje)
	img = Image.open(imagen)
	pixeles = img.load()

	longitud_mensaje = len(mensaje_bin)
	ancho, altura = img.size
	indice_pixel = 0

	for i in range(ancho):
		for j in range(altura):
			pixel = list(pixeles[i, j])

			for indice_color in range(3): # R, G, B
				if indice_pixel < longitud_mensaje:
					# Modificar el bit menos significativo (LSB) del canal de color
					pixel[indice_color] = (pixel[indice_color] & 0xFE) | int(mensaje_bin[indice_pixel])
					indice_pixel += 1
			pixeles[i, j] = tuple(pixel)

			if indice_pixel >= longitud_mensaje:
				break
		if indice_pixel >= longitud_mensaje:
			break

	salida = BytesIO()
	img.save(salida, format='PNG')
	salida.seek(0)

	imagen_oculta = image()
	imagen_oculta.length = longitud_mensaje
	imagen_oculta.image.save(f'{uuid.uuid4().hex.upper()}.png', ContentFile(salida.read()), save=True)
	salida.close()

def extraer_mensaje_imagen(ruta_imagen, longitud_bits):
	img = Image.open(ruta_imagen)
	pixeles = img.load()

	ancho, altura = img.size
	mensaje_bin = ''
	indice_pixel = 0

	for i in range(ancho):
		for j in range(altura):
			pixel = list(pixeles[i, j])

			for indice_color in range(3):  # R, G, B
				if indice_pixel < longitud_bits:
					mensaje_bin += str(pixel[indice_color] & 1)
					indice_pixel += 1

			if indice_pixel >= longitud_bits:
				break
		if indice_pixel >= longitud_bits:
			break

	return ''.join(chr(int(mensaje_bin[i:i+8], 2)) for i in range(0, len(mensaje_bin), 8))


if __name__ == "__main__":
	pass
