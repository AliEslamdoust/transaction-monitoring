from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
import random
import string
import json

User = get_user_model()

def random_id():
    return "".join(random.choices(string.digits, k=16))

def random_amount():
    return "".join(random.choices(string.digits, k=3))


class HighLoadTransactionTest(TransactionTestCase):
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test_user")
        cls.client = Client()

    def send_request(self, url, i):
        data = {
            "transaction_id": random_id(),
            "status": "PENDING",
            "user": self.user.id,
            "amount": random_amount(),
        }
        resp = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        print(f"Request {i}: {resp.status_code}")
        self.assertEqual(resp.status_code, 200)

    def test_50_requests(self):
        url = "/api/add-transaction/"
        for i in range(50):
            self.send_request(url, i)
