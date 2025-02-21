# Use Python 3.11 Slim as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy required files
COPY requirements.txt .
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Flask
EXPOSE 8080

# Command to run the bot
CMD ["python", "main.py"]
