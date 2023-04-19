# Start with a base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code into the container
COPY app/ app/
COPY logging/ logging/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LOGURU_AUTO_ROTATION=True \
    LOGURU_RETENTION="10 days" \
    LOGURU_ROTATION="1 week" \
    LOGURU_FORMAT="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
