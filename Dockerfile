# Use an official Python runtime as a parent image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container to /app
WORKDIR /app

# Copy the main.py contents into the container at /app
COPY requirements.txt . 

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy main.py into the container at /app
COPY main.py .

# Copy the templates directory into the container at /app/templates
COPY templates templates

# Copy the static directory into the container at /app/static
COPY static static

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run your application
CMD ["python", "main.py"]
