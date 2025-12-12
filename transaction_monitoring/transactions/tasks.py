import json
from celery import shared_task
from django_redis import get_redis_connection
import time
from django.db import IntegrityError, DatabaseError, connection
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache

from .models import Transaction

REDIS_TRANSACTIONS_DATABASE_KEY = settings.REDIS_TRANSACTIONS_DATABASE_KEY
REDIS_TRANSACTIONS_CHANNELS_KEY = settings.REDIS_TRANSACTIONS_CHANNELS_KEY


class TransactionManager:
    """handles bulk transaction saving"""

    def save_data(self, objects):
        """saves transactions to database"""
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
    """moves transactions from redis to database"""
    r = get_redis_connection("default")
    manager = TransactionManager()

    items = r.lrange(REDIS_TRANSACTIONS_DATABASE_KEY, 0, -1)

    if not items:
        return

    transactions = [json.loads(item) for item in items]

    objects = [
        Transaction(
            transaction_id=data["transaction_id"],
            user_id=data["user"],
            status=data.get("status", "PENDING"),
            amount=data["amount"],
            created_at=data["created_at"],
        )
        for data in transactions
    ]

    save_data = manager.save_data(objects)
    if save_data["success"]:
        r.ltrim(REDIS_TRANSACTIONS_DATABASE_KEY, len(objects), -1)


@shared_task(bind=True, time_limit=None, soft_time_limit=None)
def send_to_consumer(self):
    """sends transactions to websocket consumers"""
    r = get_redis_connection("default")
    channel_layer = get_channel_layer()

    while True:

        cache.set("watcher_is_running", "true", timeout=5)

        try:
            res = r.brpop(REDIS_TRANSACTIONS_CHANNELS_KEY, timeout=5)

            if res:
                _, raw_data = res

                json_data = raw_data.decode("utf-8")
                receivers = ["admin_global"]

                for receiver in receivers:
                    async_to_sync(channel_layer.group_send)(
                        receiver,
                        {
                            "type": "send_transaction_update",
                            "details": json_data,
                        },
                    )
            else:
                pass

            r = get_redis_connection("default")

        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)


def delete_transactions_for_test():
    """deletes all transactions for testing"""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM transactions_transaction;")
        cursor.execute(
            "TRUNCATE TABLE transactions_transaction RESTART IDENTITY CASCADE;"
        )
