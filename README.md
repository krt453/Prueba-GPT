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

El modo de depuración se controla mediante la variable de entorno
`DEBUG`. Si se establece a `1`, `true` o `yes` la aplicación se ejecutará
en modo debug. De lo contrario, la depuración estará desactivada.

Si quieres ejecutar la aplicación en un entorno de producción de forma
simple, puedes usar Gunicorn mediante el script incluido:
```bash
./run_gunicorn.sh
```

En un entorno de producción es recomendable definir las variables de entorno
`SECRET_KEY` y `JWT_SECRET_KEY` con valores propios para asegurar las claves
de la aplicación y de los tokens JWT.
El archivo `gamehub/config.py` también toma `SECRET_KEY` del entorno en caso
de que se use su clase `Config` en otras configuraciones.

## Base de datos

La aplicación persiste los juegos en una base de datos MySQL. Puedes
configurar la conexión mediante las variables de entorno `MYSQL_HOST`,
`MYSQL_USER`, `MYSQL_PASSWORD` y `MYSQL_DATABASE`. El archivo
`docker-compose.yml` define un servicio MySQL listo para usar con estos
valores.

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
crear, actualizar y eliminar juegos. Cada juego almacena un nombre,
descripción, género y la fecha de lanzamiento (todos menos el nombre son
opcionales). Todas las rutas están protegidas con JSON Web Tokens.

Para obtener un token envía una petición `POST` a `/login` con las claves
`username` y `password` (por defecto `admin`/`password`). El token devuelto se
usa en la cabecera `Authorization` con el formato `Bearer <token>` para acceder
a las rutas protegidas.

Las rutas web de gestión de juegos (`/games` y sus variantes) también requieren
el mismo token y siguen el mismo formato de autenticación.

### Usuarios y roles

Puedes registrar nuevos usuarios enviando una petición `POST` a `/register` con
`username` y `password`. Opcionalmente puedes indicar el campo `role` que por
defecto es `user`. Los usuarios con rol `admin` son los únicos autorizados para
crear o eliminar juegos tanto en el API como en las vistas web.

## Formularios Web

Se incluye una interfaz basada en Flask-WTF para crear y editar juegos desde la web. Las plantillas utilizan Bootstrap para el estilo y requieren un token JWT en la cabecera `Authorization` como el resto de las rutas.
