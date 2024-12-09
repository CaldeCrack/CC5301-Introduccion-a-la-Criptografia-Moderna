# Comunicación encubierta

## Instalación y ejecución

Para ejecutar este proyecto se necesita tener instalado Python, a continucación se entregarán las instrucciones a ejecutar por consola para probar la aplicación web. Es posible que se necesite crear y activar un ambiente virtual con las siguientes instrucciones:

```bash
python -m venv env
env\Scripts\activate # Windows
source env/bin/activate # MacOs y Linux
```

Luego, deberán instalarse las librerías del proyecto en el ambiente virtual:

```bash
pip install -r requirements.txt
```

Finalmente, para ejecutar el proyecto con seguridad se deben ejecutar las siguientes instrucciones:

```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py runserver
```

En este momento la aplicación estará corriendo en el host local. Para acceder a ella deberá ingresarse a la siguiente dirección en el navegador web de confianza: http://127.0.0.1:8000/

Cabe destacar que es necesario crear una cuenta para poder utilizar la aplicación. Una vez se cree esta, deberá guardarse la clave RSA privada entregada por completo, incluyendo las líneas de inicio y fin de la clave.

```text
-----BEGIN RSA PRIVATE KEY-----
<key-content>
-----END RSA PRIVATE KEY-----
```

Para realizar pruebas en la aplicación se recomienda guiarse por el ejemplo de uso del informe.
