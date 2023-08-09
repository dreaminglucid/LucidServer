FROM python:3.11.4-slim-buster

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=3 --log-level=info"

CMD ["gunicorn", "server:app"]
