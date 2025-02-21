# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy only requirements first for efficient caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port 8080 for Flask (Google Cloud Run requirement)
EXPOSE 8080

# Define environment variables
ENV PORT=8080

# Start both Flask and Discord bot using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
