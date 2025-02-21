# Use Python 3.11 Slim as the base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory
WORKDIR /app

# Copy required files
COPY requirements.txt .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files
COPY . .

# Expose Flask port
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]
