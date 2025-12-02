from django.urls import path
from .consumers import AdminTransactionConsumer

websocket_urlpatterns = [
    path("ws/admin/transactions/", AdminTransactionConsumer.as_asgi()),
]
