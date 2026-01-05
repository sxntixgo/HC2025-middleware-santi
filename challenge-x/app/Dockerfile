FROM python:3.10-slim
WORKDIR /app
COPY ../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/app.py ./.env ./
CMD ["gunicorn", "--bind", "0.0.0.0:443", "--workers", "4", "--certfile", "/app/cert.pem", "--keyfile", "/app/key.pem", "app:app"]
