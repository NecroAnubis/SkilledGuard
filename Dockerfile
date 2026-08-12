FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Se copian los requirements primero para que Docker reutilice la capa de
# dependencias cuando solo cambia el código.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuario sin privilegios: si alguien compromete la app, no es root del contenedor.
# El bit de ejecución del entrypoint se fija aquí y no se confía al checkout: en
# Windows el permiso no sobrevive al clon y el contenedor no arrancaría.
RUN chmod +x entrypoint.sh && useradd --create-home appuser && chown -R appuser /app
USER appuser

# Documenta el puerto de desarrollo. La plataforma de despliegue inyecta PORT y
# el entrypoint la respeta, así que este valor es informativo, no vinculante.
EXPOSE 8000
CMD ["./entrypoint.sh"]
