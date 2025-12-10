from rest_framework import serializers
from .models import Transaction
from datetime import datetime


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
