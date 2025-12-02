import json
from rest_framework import generics, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from .tasks import process_transaction


class ObtainTransactionDetailsView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        # data = self.request.data
        validated_data = serializer.validated_data

        if not serializer.is_valid():
            return Response(
                {"message": "Data is invalid."}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        process_transaction(transaction_data=validated_data)
        return Response(
            {"message": "Transaction detail was obtained successfully."},
            status=status.HTTP_200_OK,
        )
