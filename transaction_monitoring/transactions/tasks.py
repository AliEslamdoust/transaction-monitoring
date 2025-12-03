import json
from celery import shared_task
from django_redis import get_redis_connection
from django.db import IntegrityError, DatabaseError, connection
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Transaction

REDIS_TRANSACTIONS_KEY = settings.REDIS_TRANSACTIONS_KEY


class TransactionManager:
    def save_data(self, objects):
        try:
            Transaction.objects.bulk_create(objects, ignore_conflicts=True)
            return {"success": True}
        except IntegrityError as e:

            print(f"Integrity error while saving transactions: {e}")
        except DatabaseError as e:
            print(f"Database error while saving transactions: {e}")
        except Exception as e:
            print(f"Unexpected error while bulk saving: {e}")
        return {"success": False}


@shared_task
def flush_transactions():
    redis = get_redis_connection("default")
    manager = TransactionManager()

    items = redis.lrange(REDIS_TRANSACTIONS_KEY, 0, - 1)

    if not items:
        return

    transactions = [json.loads(item) for item in items]

    objects = [
        Transaction(
            transaction_id=data["transaction_id"],
            user_id=data["user"],
            status=data.get("status", "PENDING"),
            amount=data["amount"],
        )
        for data in transactions
    ]

    save_data = manager.save_data(objects)
    if save_data["success"]:
        redis.ltrim(REDIS_TRANSACTIONS_KEY, len(objects), -1)


def send_to_consumer(data):
    channel_layer = get_channel_layer()

    details = data.copy()
    details["user"] = data["user"]

    async_to_sync(channel_layer.group_send)(
        "admin_global",
        {
            "type": "send_transaction_update",
            "details": details,
        },
    )


def delete_transactions_for_test():
    # Delete all rows from database
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM transactions_transaction;")
        cursor.execute(
            "TRUNCATE TABLE transactions_transaction RESTART IDENTITY CASCADE;"
        )
