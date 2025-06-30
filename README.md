# Prueba-GPT

Este proyecto contiene un pequeño ejemplo de aplicación Flask.

## Instalación

1. Clona el repositorio y entra en la carpeta:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Prueba-GPT
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. De forma opcional puedes ejecutar el script `setup.sh` que automatiza la
   creación del entorno virtual e instala las dependencias:
   ```bash
   bash setup.sh
   ```


## Ejecutar la aplicación

Para arrancar el servidor de desarrollo de Flask ejecuta:
```bash
python app.py
```

Si quieres ejecutar la aplicación en un entorno de producción de forma
simple, puedes usar Gunicorn mediante el script incluido:
```bash
./run_gunicorn.sh
```

## Ejecutar pruebas

Instala las dependencias de desarrollo y ejecuta `pytest`:

```bash
pip install -r requirements-dev.txt
pytest
```

## Integración con Apache y mod_wsgi

1. Asegúrate de tener instalado `mod_wsgi`.
2. Copia el archivo `gamehub.wsgi` en el directorio del proyecto.
3. Configura Apache añadiendo algo similar a lo siguiente en tu VirtualHost:
    ```apache
    WSGIDaemonProcess gamehub python-path=/ruta/al/proyecto/.venv/lib/python3.x/site-packages
    WSGIProcessGroup gamehub
    WSGIScriptAlias / /ruta/al/proyecto/gamehub.wsgi
    
    <Directory /ruta/al/proyecto>
    Require all granted
    </Directory>
    ```

Al reiniciar Apache, la aplicación estará disponible usando `mod_wsgi`.

## API con JWT

La aplicación incluye un pequeño API bajo el prefijo `/api` que permite listar,
crear, actualizar y eliminar juegos. Todas las rutas están protegidas con
JSON Web Tokens.

Para obtener un token envía una petición `POST` a `/login` con las claves
`username` y `password` (por defecto `admin`/`password`). El token devuelto se
usa en la cabecera `Authorization` con el formato `Bearer <token>` para acceder
a las rutas protegidas.
