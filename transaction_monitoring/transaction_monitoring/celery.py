import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transaction_monitoring.settings")

app = Celery("transaction_monitoring")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
__all__ = ("flush_transactions",)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
