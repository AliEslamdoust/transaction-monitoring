import json
from rest_framework import generics, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from .tasks import send_to_consumer, delete_transactions_for_test
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework.views import APIView
from django.db.models import Min, Max
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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

        if not from_date_str:
            from_datetime = timezone.make_aware(datetime.min)
        else:
            from_datetime = parse_datetime(from_date_str)

        if not to_date_str:
            to_datetime = timezone.make_aware(datetime.max)
        else:
            to_datetime = parse_datetime(to_date_str)

        if to_datetime < from_datetime:
            to_datetime, from_datetime = from_datetime, to_datetime

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


def get_time_frame(to_datetime, from_datetime):
    earliest, latest = get_date()
    
    if from_datetime < earliest:
        from_datetime = earliest
    if to_datetime > latest:
        to_datetime = latest

    diff = relativedelta(to_datetime, from_datetime)

    parts = []

    if diff.years:
        parts.append(f"{diff.years} years")
    if diff.months:
        parts.append(f"{diff.months} months")
    if diff.days:
        parts.append(f"{diff.days} days")
    if diff.hours:
        parts.append(f"{diff.hours} hours")
    if diff.minutes:
        parts.append(f"{diff.minutes} minutes")
    if diff.seconds:
        parts.append(f"{diff.seconds} seconds")

    return ", ".join(parts) if parts else "0 seconds"


def get_date():
    dates = Transaction.objects.aggregate(
        earliest=Min("created_at"), latest=Max("created_at")
    )

    return dates["earliest"], dates["latest"]


class gettransaction(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
