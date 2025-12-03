import json
from rest_framework import generics, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from .tasks import send_to_consumer
from django.conf import settings
from django_redis import get_redis_connection

REDIS_TRANSACTIONS_KEY = settings.REDIS_TRANSACTIONS_KEY


class ObtainTransactionDetailsView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data["user"] = data["user"].id

        redis = get_redis_connection("default")
        redis.rpush(REDIS_TRANSACTIONS_KEY, json.dumps(data))
        send_to_consumer(data=data)

        return Response(
            {"message": "Transaction detail was obtained successfully."},
            status=status.HTTP_200_OK,
        )
