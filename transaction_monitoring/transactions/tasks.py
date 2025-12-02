import json
from celery import shared_task
from django_redis import get_redis_connection
from django.db import IntegrityError, DatabaseError
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Transaction

BATCH_SIZE = 100
REDIS_TRANSACTIONS_KEY = settings.REDIS_TRANSACTIONS_KEY


class TransactionManager:
    def save_data(self, objects):
        try:
            Transaction.objects.bulk_create(objects, ignore_conflicts=True)
            print(f"ADDED TRANSACTIONS AS BULK, AMOUNT: {len(objects)}")
        except IntegrityError as e:
            print(f"Integrity error while saving transactions: {e}")
        except DatabaseError as e:
            print(f"Database error while saving transactions: {e}")
        except Exception as e:
            print(f"Unexpected error while bulk saving: {e}")


@shared_task
def flush_transactions():
    redis = get_redis_connection("default")

    while True:
        pipe = redis.pipeline()
        pipe.lrange(REDIS_TRANSACTIONS_KEY, 0, BATCH_SIZE - 1)
        pipe.ltrim(REDIS_TRANSACTIONS_KEY, BATCH_SIZE, -1)
        items, _ = pipe.execute()

        if not items:
            break

        transactions_data = [json.loads(item) for item in items]

        objects = [
            Transaction(
                transaction_id=data["transaction_id"],
                user_id=data["user"],
                status=data.get("status", "PENDING"),
            )
            for data in transactions_data
        ]

        TransactionManager().save_data(objects)

    return "Flushed successfully"


@shared_task(bind=True, max_retries=3)
def process_transaction(self, transaction_data):
    try:
        redis = get_redis_connection("default")

        validated_data = {
            "transaction_id": transaction_data["transaction_id"],
            "user": transaction_data["user"].id,
            "status": transaction_data.get("status", "PENDING"),
        }

        redis.rpush(REDIS_TRANSACTIONS_KEY, json.dumps(validated_data))

        send_to_consumer(validated_data)

    except Exception as err:
        print(f"Error in process_transaction: {err}")


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
