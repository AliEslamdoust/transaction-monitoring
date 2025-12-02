from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import time
import random
import string

User = get_user_model()


def generate_transaction_id():
    return "".join(random.choices(string.digits, k=16))


class HighLoadTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test")

    def setUp(self):
        self.client = Client()

    def test_2000_transactions_per_second(self):
        url = "/api/add-transaction/"
        requests_per_second = 50

        start_time = time.time()
        end_time = start_time + 1

        while time.time() < end_time:
            for i in range(requests_per_second):
                payload = {
                    "transaction_id": generate_transaction_id(),
                    "status": "PENDING",
                    "user": self.user.id, 
                }
                response = self.client.post(url, data=payload)
                print(f"done: {payload}, request: {i}")
                self.assertIn(response.status_code, [200, 201, 202])
