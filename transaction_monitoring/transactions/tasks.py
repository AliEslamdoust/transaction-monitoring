import json
from celery import shared_task
from django_redis import get_redis_connection
from django.db import IntegrityError, DatabaseError, connection
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Transaction

REDIS_TRANSACTIONS_DATABASE_KEY = settings.REDIS_TRANSACTIONS_DATABASE_KEY
REDIS_TRANSACTIONS_CHANNELS_KEY = settings.REDIS_TRANSACTIONS_CHANNELS_KEY


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

    items = redis.lrange(REDIS_TRANSACTIONS_DATABASE_KEY, 0, -1)

    if not items:
        return

    transactions = [json.loads(item) for item in items]

    objects = [
        Transaction(
            transaction_id=data["transaction_id"],
            user_id=data["user"],
            status=data.get("status", "PENDING"),
            amount=data["amount"],
            created_at=data["created_at"]
        )
        for data in transactions
    ]

    save_data = manager.save_data(objects)
    if save_data["success"]:
        redis.ltrim(REDIS_TRANSACTIONS_DATABASE_KEY, len(objects), -1)


@shared_task(time_limit=None, soft_time_limit=None)
def send_to_consumer():
    print("fuck true 1")
    redis = get_redis_connection("default")
    channel_layer = get_channel_layer()
    

    while True:
        _, data = redis.brpop(REDIS_TRANSACTIONS_CHANNELS_KEY)
        
        print("fuck true 2")

        receivers = ["admin_global"]

        for receiver in receivers:
            async_to_sync(channel_layer.group_send)(
                receiver,
                {
                    "type": "send_transaction_update",
                    "details": data,
                },
            )


def delete_transactions_for_test():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM transactions_transaction;")
        cursor.execute(
            "TRUNCATE TABLE transactions_transaction RESTART IDENTITY CASCADE;"
        )
