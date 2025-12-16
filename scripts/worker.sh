#!/bin/bash
set -e

cd /app/transaction_monitoring

exec celery -A transaction_monitoring worker -l info
