from rest_framework import generics
from .models import Transaction
from .serializers import TransactionSerializer


class ObtainTransactionDetailsView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)