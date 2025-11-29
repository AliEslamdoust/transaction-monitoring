from django.db import models
from django.contrib.auth import get_user_model


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    PAYMENT_STATUS = [
        ["PENDING", "Pending"],
        ["SUCCESS", "Success"],
        ["FAILED", "Failed"],
    ]
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id
