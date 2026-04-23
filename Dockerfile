FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && echo 'Starting app...' && gunicorn -b 0.0.0.0:$PORT run:app"]