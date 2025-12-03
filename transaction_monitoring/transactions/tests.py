from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()


def generate_transaction_id():
    return "".join(random.choices(string.digits, k=16))


def generate_transaction_amount():
    return "".join(random.choices(string.digits, k=3))


class HighLoadTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test")

    def setUp(self):
        self.client = Client()

    def test_transactions(self):
        url = "/api/add-transaction/"
        requests_amount = 500

        for i in range(requests_amount):
            payload = {
                "transaction_id": generate_transaction_id(),
                "status": "PENDING",
                "user": self.user.id,
                "amount": generate_transaction_amount(),
            }
            response = self.client.post(url, data=payload)
            print(f"done: {payload}, request: {i}")
            self.assertIn(response.status_code, [200, 201, 202])
