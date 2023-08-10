# Use the specific Python runtime as a parent image
FROM python:3.11.4-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install system dependencies for some Python packages like psycopg2, C++ compiler, wget, git, and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Download, compile, and install SQLite from the provided snapshot
RUN wget -v https://sqlite.org/snapshot/sqlite-snapshot-202308011103.tar.gz && \
    tar xvfz sqlite-snapshot-202308011103.tar.gz && \
    cd sqlite-snapshot-202308011103 && \
    ./configure && \
    make && make install && \
    ldconfig && \
    cd .. && \
    rm -rf sqlite-snapshot-202308011103 && \
    rm sqlite-snapshot-202308011103.tar.gz

# Check SQLite version
RUN sqlite3 --version

# Install Python dependencies from the requirements file
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make ports available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches, using the Heroku-provided PORT environment variable
CMD gunicorn --bind 0.0.0.0:$PORT server:app