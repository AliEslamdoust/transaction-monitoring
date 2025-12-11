from django.apps import AppConfig
from django.core.cache import cache
import sys


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transactions"

    def ready(self):
        if any(x in sys.argv for x in ["collectstatic", "makemigrations", "migrate"]):
            return

        if cache.get("watcher_is_running"):
            print("Watcher is already active. Skipping startup..")
            return

        lock_id = "startup_watcher"
        if cache.add(lock_id, "true", timeout=10):
            from .tasks import send_to_consumer

            send_to_consumer.delay()
