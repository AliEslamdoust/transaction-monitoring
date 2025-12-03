import json
from rest_framework import generics, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from .tasks import send_to_consumer, delete_transactions_for_test
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework.views import APIView
from django.db.models import Min, Max, Avg
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

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


class DeleteTransactionsView(APIView):
    def delete(Self, request, *args, **kwargs):
        delete_transactions_for_test()
        return Response(
            {"message": "Deleted all rows from transactions_transaction table"},
            status=status.HTTP_200_OK,
        )


class GetTransactionsAverageView(APIView):
    def get(self, request):
        from_date_str = validate_date(request.GET.get("from"))
        to_date_str = validate_date(request.GET.get("to"))

        earliest_date, latest_date = get_date()

        earliest_date = datetime.fromisoformat(
            str(earliest_date).replace("Z", "+00:00")
        )
        latest_date = datetime.fromisoformat(str(latest_date).replace("Z", "+00:00"))

        if not from_date_str or from_date_str < earliest_date:
            from_date_str = earliest_date
        else:
            from_date_str = from_date_str.split("T") + "T00:00:00.000000+00:00"

        if not to_date_str or to_date_str > latest_date:
            to_date_str = latest_date
        else:
            to_date_str = to_date_str.split("T") + "T23:59:59.999999+00:00"

        diff = (to_date_str - from_date_str).days

        qs = (
            Transaction.objects.filter(
                created_at__date__gte=from_date_str, created_at__date__lte=to_date_str
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(avg_amount=Avg("amount"))
            .order_by("day")
        )

        # data_by_day = {f"{item["day"]}": item["avg_amount"] for item in qs}
        return Response(
            {
                "data": {
                    "e": earliest_date,
                    "l": latest_date,
                    "f": from_date_str,
                    "t": to_date_str,
                    "data": qs,
                }
            },
            status=status.HTTP_200_OK,
        )


def get_date():
    dates = Transaction.objects.aggregate(
        earliest=Min("created_at"), latest=Max("created_at")
    )
    # print(dates["earliest"])

    return dates["earliest"], dates["latest"]


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


class gettransaction(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
