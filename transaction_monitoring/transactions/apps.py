from django.apps import AppConfig
from django.core.cache import cache
import sys


class TransactionsConfig(AppConfig):
    """
    This configures the Transactions app, including its ready method for startup tasks.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "transactions"

    def ready(self):
        """
        This method is called when the app is ready, and it starts the watcher if it's not already running.
        """
        
        from . import signals

        if any(x in sys.argv for x in ["collectstatic", "makemigrations", "migrate"]):
            return

        if cache.get("watcher_is_running"):
            return

        lock_id = "startup_watcher"
        if cache.add(lock_id, "true", timeout=10):
            from .tasks import send_to_consumer

            send_to_consumer.delay()
