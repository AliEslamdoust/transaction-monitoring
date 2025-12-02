"""
ASGI config for transaction_monitoring project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import transaction_monitoring.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transaction_monitoring.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(transaction_monitoring.routing.websocket_urlpatterns),
    }
)
