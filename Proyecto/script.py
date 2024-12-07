from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import hmac
import base64
import os

# Funciones de Cifrado AES
def cifrar_mensaje(mensaje, clave_secreta):
    # Cifrado AES con padding
    cipher = AES.new(clave_secreta, AES.MODE_CBC)
    mensaje_cifrado = cipher.encrypt(pad(mensaje.encode(), AES.block_size))
    return cipher.iv + mensaje_cifrado

def descifrar_mensaje(mensaje_cifrado, clave_secreta):
    # Descifrado AES con padding
    iv = mensaje_cifrado[:16]  # Los primeros 16 bytes son el IV
    mensaje_cifrado = mensaje_cifrado[16:]
    cipher = AES.new(clave_secreta, AES.MODE_CBC, iv)
    mensaje_descifrado = unpad(cipher.decrypt(mensaje_cifrado), AES.block_size)
    return mensaje_descifrado.decode()

# Funciones de HMAC para autenticación
def generar_hmac(mensaje, clave_secreta):
    return hmac.new(clave_secreta, mensaje.encode(), hashlib.sha256).hexdigest()

def verificar_hmac(mensaje, hmac_original, clave_secreta):
    hmac_comprobado = generar_hmac(mensaje, clave_secreta)
    return hmac_comprobado == hmac_original

# Funciones de Esteganografía en Imagen
def ocultar_mensaje_imagen(imagen_path, mensaje):
    # Convertir mensaje a bytes
    mensaje_bin = ''.join(format(ord(i), '08b') for i in mensaje)
    img = Image.open(imagen_path)
    pixeles = img.load()

    mensaje_longitud = len(mensaje_bin)
    ancho, alto = img.size
    pixel_index = 0
    
    for i in range(ancho):
        for j in range(alto):
            pixel = list(pixeles[i, j])
            
            for color_index in range(3):  # R, G, B
                if pixel_index < mensaje_longitud:
                    pixel[color_index] = (pixel[color_index] & 0xFE) | int(mensaje_bin[pixel_index])
                    pixel_index += 1
            
            pixeles[i, j] = tuple(pixel)

            if pixel_index >= mensaje_longitud:
                break
        if pixel_index >= mensaje_longitud:
            break
    
    # Guardar imagen modificada
    img.save("imagen_oculta.png")
    print("Mensaje oculto en imagen: imagen_oculta.png")

def extraer_mensaje_imagen(imagen_path, longitud_bits):
    img = Image.open(imagen_path)
    pixeles = img.load()

    mensaje_bin = ''
    ancho, alto = img.size
    pixel_index = 0

    for i in range(ancho):
        for j in range(alto):
            pixel = list(pixeles[i, j])

            for color_index in range(3):  # R, G, B
                if pixel_index < longitud_bits:
                    mensaje_bin += str(pixel[color_index] & 1)
                    pixel_index += 1

            if pixel_index >= longitud_bits:
                break
        if pixel_index >= longitud_bits:
            break
    
    # Convertir los bits a texto
    mensaje = ''.join(chr(int(mensaje_bin[i:i+8], 2)) for i in range(0, len(mensaje_bin), 8))
    return mensaje

# Generar una clave secreta aleatoria de 16 bytes
def generar_clave():
    return get_random_bytes(16)

# Función principal
def comunicacion_encubierta():
    # Paso 1: Preparación
    mensaje_secreto = "Cómo suena la espalda de caldecrack? CRACK."
    clave_secreta = generar_clave()

    # Paso 2: Cifrado del mensaje
    mensaje_cifrado = cifrar_mensaje(mensaje_secreto, clave_secreta)
    mensaje_base64 = base64.b64encode(mensaje_cifrado).decode()

    # Paso 3: Crear HMAC del mensaje cifrado
    hmac_secreto = generar_hmac(mensaje_base64, clave_secreta)

    # Paso 4: Ocultar el mensaje cifrado y el HMAC en una imagen
    mensaje_completo = mensaje_base64 + hmac_secreto
    ocultar_mensaje_imagen("imagen_original.png", mensaje_completo)

    # Paso 5: Enviar la imagen (en este caso, la imagen modificada es la que se "envía").

    # Paso 6: En el lado del receptor, extraer y verificar el mensaje
    imagen_recibida = "imagen_oculta.png"
    # Calcular la longitud en bits
    longitud_bits = len(mensaje_completo) * 8
    mensaje_extraido = extraer_mensaje_imagen(imagen_recibida, longitud_bits)

    # Extraer mensaje cifrado y HMAC
    mensaje_cifrado_extraido = mensaje_extraido[:-64]  # Los últimos 64 caracteres son el HMAC
    hmac_extraido = mensaje_extraido[-64:]

    # Verificar la autenticidad del mensaje
    if verificar_hmac(mensaje_cifrado_extraido, hmac_extraido, clave_secreta):
        print("HMAC verificado, el mensaje es auténtico.")
        # Descifrar el mensaje
        mensaje_descifrado = descifrar_mensaje(base64.b64decode(mensaje_cifrado_extraido), clave_secreta)
        print(f"Mensaje recibido: {mensaje_descifrado}")
    else:
        print("Error: El HMAC no coincide. El mensaje ha sido alterado.")

# Ejecutar el programa
if __name__ == "__main__":
    comunicacion_encubierta()