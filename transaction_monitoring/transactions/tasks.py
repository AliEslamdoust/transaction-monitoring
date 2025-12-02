import json
from celery import shared_task
from django.conf import settings
from .models import Transaction
from django.db import IntegrityError, DatabaseError


class TransactionManager:
    def save_data(self, data):
        try:
            Transaction.objects.create(**data)
        except IntegrityError as e:
            print(f"Integrity error while saving transaction details: {e}")
        except DatabaseError as e:
            print(f"Database error while saving transaction details: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

@shared_task(bind=True, max_retries=3)
def process_transaction(self,transaction_data):
    try:
        data = json.load(transaction_data)
        
        try:
            TransactionManager().save_data(data=data)
        except IntegrityError as err:
            print(f"Error while saving {data.get('transaction_id')} to database: {err}")
            
        # call redis
    except json.JSONDecodeError:
        print(f"JSON Is not formatted correctly: {transaction_data}")
    except Exception as err:
        print(f"An unexpected error has occured: {err}")