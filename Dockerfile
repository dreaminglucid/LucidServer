# Use the specific Python runtime as a parent image
FROM python:3.11.4-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install system dependencies for some Python packages like psycopg2, C++ compiler, and sqlite3
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Build SQLite3 from source
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3360000.tar.gz \
    && tar xvfz sqlite-autoconf-3360000.tar.gz \
    && cd sqlite-autoconf-3360000 \
    && ./configure \
    && make \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf sqlite-autoconf-3360000 \
    && rm sqlite-autoconf-3360000.tar.gz

# Check SQLite version
RUN sqlite3 --version

# Install Python dependencies from the requirements file
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make ports available to the world outside this container
EXPOSE 8000

# Define environment variable for Gunicorn
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=3 --log-level=info"

# Run app.py when the container launches
CMD ["gunicorn", "server:app"]