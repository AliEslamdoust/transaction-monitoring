from rest_framework import serializers
from .models import Transaction
from datetime import datetime


class TransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"

        def create(self, validated_data):
            validated_data["created_at"] = datetime.now()
            return super().crrate(validated_data)
