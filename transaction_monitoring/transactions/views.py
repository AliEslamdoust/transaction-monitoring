import json
from rest_framework import generics, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from .tasks import delete_transactions_for_test
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework.views import APIView
from .helper import get_time_frame, validate_datetime

REDIS_TRANSACTIONS_CHANNELS_KEY = settings.REDIS_TRANSACTIONS_CHANNELS_KEY
REDIS_TRANSACTIONS_DATABASE_KEY = settings.REDIS_TRANSACTIONS_DATABASE_KEY


class ObtainTransactionDetailsView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data["user"] = data["user"].id
        data["created_at"] = str(data["created_at"])

        redis = get_redis_connection("default")
        redis.lpush(REDIS_TRANSACTIONS_CHANNELS_KEY, json.dumps(data))
        redis.lpush(REDIS_TRANSACTIONS_DATABASE_KEY, json.dumps(data))

        return Response(
            {"message": "Transaction detail was obtained successfully."},
            status=status.HTTP_200_OK,
        )


class DeleteTransactionsView(APIView):
    def delete(Self, request, *args, **kwargs):
        delete_transactions_for_test()
        return Response(
            {"message": "Deleted all rows from transactions_transaction table"},
            status=status.HTTP_200_OK,
        )


class GetTransactionsAverageView(APIView):
    def get(self, request):
        from_date_str = request.GET.get("from")
        to_date_str = request.GET.get("to")

        from_datetime, to_datetime = validate_datetime(from_date_str, to_date_str)

        transactions = Transaction.objects.filter(
            created_at__gte=from_datetime, created_at__lte=to_datetime
        )

        transactions_list = list(transactions.values("created_at", "amount"))

        amounts = [i["amount"] for i in transactions_list]

        sales = sum(amounts)
        number_of_sales = len(amounts)

        if amounts:
            avg = sales / number_of_sales
        else:
            avg = 0

        time_frame = get_time_frame(to_datetime, from_datetime)

        return Response(
            {
                "data": {
                    "avgerage_of_transactions": avg,
                    "whole_profit": sales,
                    "numer_of_sales": number_of_sales,
                    "selected_time_frame": time_frame,
                }
            },
            status=status.HTTP_200_OK,
        )


class gettransaction(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
