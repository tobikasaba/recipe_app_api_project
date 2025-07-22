#!/bin/zsh
# Tells the system to run this script with zsh.

# Exit immediately if any command returns a non-zero status/command fails. The script stops
set -e

# Wait for the database service to become available
python3 manage.py wait_for_db

# Collect all static files into STATIC_ROOT without prompting
python3 manage.py collectstatic --noinput

# Apply any new database migrations
python3 manage.py migrate

# Launch uWSGI to serve the Django app
# Listen on port 9000 for HTTP/TCP.
# Use 4 worker processes to handle requests.
# Enable a master process to manage workers
# Allow each worker to use threads
# Point to the Django  WSGI application in app/wsgi.py
uwsgi --socket :9000 --workers 4 --master -- enable-threads --module app.wsgi
