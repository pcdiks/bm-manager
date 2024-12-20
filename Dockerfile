# Use the official Python image
FROM python:3.14.0a2-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Install Packages
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y gettext-base
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy the Django project into the container
COPY . /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Remove the default Nginx site
RUN rm -f /etc/nginx/sites-enabled/default

# Copy the Nginx configuration
COPY nginx/default.conf.template /etc/nginx/conf.d/default.conf.template

# Expose the port for Nginx
EXPOSE 80

# Start both Nginx and Gunicorn
# CMD ["/bin/bash", "-c", "gunicorn bookmark_manager.wsgi:application --bind 0.0.0.0:8000 & nginx -g 'daemon off;'"]
# CMD ["/bin/bash", "-c", "python manage.py migrate && gunicorn bookmark_manager.wsgi:application --bind 0.0.0.0:8000 & nginx -g 'daemon off;'"]
CMD envsubst '${APP_HOST}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && \
    python manage.py migrate && \
    gunicorn bookmark_manager.wsgi:application --bind 0.0.0.0:8000 & \
    nginx -g "daemon off;"