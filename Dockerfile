# Use a newer Python base image
FROM python:3.10-slim

# Install system dependencies for ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]