from django.apps import AppConfig
from django.core.cache import cache
import sys


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transactions"

    def ready(self):
        if any(x in sys.argv for x in ["collectstatic", "makemigrations", "migrate"]):
            return

        lock_id = "startup_task"
        if cache.add(lock_id, "true", timeout=60):
            from .tasks import send_to_consumer

            send_to_consumer.delay()
