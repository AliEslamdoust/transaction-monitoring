#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."

until python -c "
import socket
import sys

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('$DB_HOST', int('$DB_PORT')))
    s.close()
except socket.error as e:
    sys.exit(1)
"
do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL started"

cd /app/transaction_monitoring

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Daphne server..."

exec daphne -b 0.0.0.0 -p 8000 transaction_monitoring.asgi:application