FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema necesarias para psycopg2 y compilacion de paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway inyecta la variable PORT dinamicamente; el comando real
# se sobreescribe por servicio (web/worker/beat) en el panel de Railway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]