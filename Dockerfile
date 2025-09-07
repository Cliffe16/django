# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 7860

# Run the web server
CMD ["gunicorn", "sugarqube.wsgi:application", "--bind", "0.0.0.0:7860"]