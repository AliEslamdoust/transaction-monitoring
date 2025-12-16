#!/bin/bash
set -e

cd /app/transaction_monitoring

exec celery -A transaction_monitoring beat -l info
