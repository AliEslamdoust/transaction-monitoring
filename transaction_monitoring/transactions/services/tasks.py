from celery import shared_task
from transactions.models import Transaction
import logging

logger = logging.getLogger(__name__)


@shared_task
def save_transaction(data):
    try:
        transaction = Transaction.objects.create(**data)
    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
