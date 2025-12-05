from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import random
import string
import threading

User = get_user_model()


def generate_transaction_id():
    return "".join(random.choices(string.digits, k=16))


def generate_transaction_amount():
    return "".join(random.choices(string.digits, k=3))


class HighLoadTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = []
        for i in range(50):
            user = User.objects.create(username=f"test_user_{i}")
            cls.users.append(user)

    def setUp(self):
        self.client = Client()

    def send_request(self, user, url, request_num):
        """Send a single request for a specific user"""
        payload = {
            "transaction_id": generate_transaction_id(),
            "status": "PENDING",
            "user": user.id,
            "amount": generate_transaction_amount(),
        }
        client = Client()
        response = client.post(url, data=payload)
        print(f"User {user.username} - Request {request_num}: {response.status_code}")
        self.assertIn(response.status_code, [200, 201, 202])

    def test_transactions(self):
        url = "/api/add-transaction/"
        requests_per_user = 50
        threads = []

        for user in self.users:
            for request_num in range(requests_per_user):
                thread = threading.Thread(
                    target=self.send_request, args=(user, url, request_num)
                )
                threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print(f"Completed {len(threads)} requests from {len(self.users)} users")
