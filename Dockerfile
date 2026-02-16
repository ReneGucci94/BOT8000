# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make startup script executable
RUN chmod +x run_system.sh

# Define environment variable
ENV NAME Bot8000
ENV PYTHONPATH /app
ENV TRADING_MODE simulation
ENV API_KEY ""
ENV SECRET_KEY ""

# Run run_system.sh when the container launches
CMD ["./run_system.sh"]
