import requests
import random
import string
import json
import threading
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
import concurrent.futures
import time


def random_id():
    return "".join(random.choices(string.digits, k=16))


def random_amount():
    # random_number = random.choices(string.digits, k=3)
    return "".join(random.choices(string.digits, k=3))


url = "http://127.0.0.1:8000/api/"


def send_request(post_url, payload, request_id):
    try:
        response = requests.post(post_url, json=payload)

        response.raise_for_status()

        return {"id": request_id, "status": "success", "code": response.status_code}

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"id": request_id, "status": "failed", "error": str(e)}


def test_api_speed(dps=40):
    future_to_req = []
    post_url = f"{url}add-transaction/"

    start_time = time.time()
    is_one_second = True
    while is_one_second:
        print(f"Sending {dps} requests ...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executer:
            for i in range(dps):
                current_time = datetime.now(ZoneInfo("UTC"))
                payload = {
                    "transaction_id": random_id(),
                    "status": "PENDING",
                    "user": 1,
                    "amount": random_amount(),
                    "created_at": str(current_time),
                }
                future = executer.submit(send_request, post_url, payload, i)
                future_to_req.append(future)

        is_one_second = time.time() - start_time < 1

    results = []
    for future in concurrent.futures.as_completed(future_to_req):
        result = future.result()
        results.append(result)

        if result["status"] == "failed":
            result_id = result["id"]
            result_err = result["error"]
            print(f"Request {result_id} failed: {result_err}")

    duration = time.time() - start_time
    print(f"Finished in {duration:.2f} seconds")

    success_counts = sum(1 for r in results if r["status"] == "success")
    fail_counts = len(results) - success_counts

    print(f"Success: {success_counts} / {len(results)}")
    print(f"Failed: {fail_counts} / {len(results)}")


test_api_speed()
