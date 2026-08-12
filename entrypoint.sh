#!/bin/sh
# Arranque del contenedor: deja el esquema al día, siembra si hay con qué, y
# levanta el servidor.
#
# Vive en un script y no en el CMD del Dockerfile ni en el docker-compose para
# que el entorno local y la plataforma arranquen exactamente igual. Cuando el
# comando de arranque está escrito en dos sitios, tarde o temprano dejan de
# coincidir y el fallo aparece solo en el que no se prueba.
set -e

# Antes de aceptar tráfico: si el código espera una columna que la base no
# tiene, es preferible fallar aquí que a mitad de una petición.
alembic upgrade head

# La siembra solo corre si hay contraseña de administrador. `app.seed` termina
# con error cuando falta, y encadenado aquí eso impediría arrancar el servicio
# entero — en un despliegue ya sembrado esa variable no tiene por qué seguir
# presente. Es idempotente, así que repetirla en cada arranque no duplica nada.
if [ -n "$ADMIN_CONTRASENA" ]; then
	python -m app.seed
fi

# PORT lo inyecta la plataforma de despliegue; 8000 es el valor de desarrollo.
#
# --proxy-headers hace que la aplicación tome el esquema y la IP de origen de
# las cabeceras que pone el proxy en vez de la conexión directa. Sin
# --forwarded-allow-ips no sirve de nada: por defecto uvicorn solo confía en
# 127.0.0.1, y el proxy de la plataforma no conecta por loopback, así que
# descarta las cabeceras en silencio y todas las peticiones quedan registradas
# con la IP del proxy.
#
# Confiar en cualquier origen ("*") es correcto solo mientras nadie pueda
# hablarle al contenedor sin pasar por el proxy. Por eso el docker-compose
# publica el puerto únicamente en 127.0.0.1: si se expusiera a la red,
# cualquiera podría falsificar X-Forwarded-For y envenenar la bitácora.
exec uvicorn app.main:app \
	--host 0.0.0.0 \
	--port "${PORT:-8000}" \
	--proxy-headers \
	--forwarded-allow-ips="*"
