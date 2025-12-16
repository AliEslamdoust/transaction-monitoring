#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."

until python - <<EOF
import socket, os
s = socket.socket()
try:
    s.connect((os.environ["DB_HOST"], int(os.environ["DB_PORT"])))
    s.close()
except Exception:
    exit(1)
EOF
do
  sleep 1
done

echo "PostgreSQL is up"

cd /app/transaction_monitoring

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec daphne -b 0.0.0.0 -p 8000 transaction_monitoring.asgi:application
