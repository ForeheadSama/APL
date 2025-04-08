# Use the official Python image from the Docker hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run the app when the container starts
CMD ["flask", "run", "--host=0.0.0.0"]
