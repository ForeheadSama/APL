# Use the official Python image from the Docker hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for the app
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    # Clean up cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install any needed Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run the app when the container starts
CMD ["python", "app.py"]
