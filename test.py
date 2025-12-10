import requests
import random
import string
import json
import threading
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta


def random_id():
    return "".join(random.choices(string.digits, k=16))


def random_amount():
    return "".join(random.choices(string.digits, k=3))


url = "http://127.0.0.1:8000/api/"


def send_request():

    current_time = datetime.now(ZoneInfo("UTC"))
    payload = {
        "transaction_id": random_id(),
        "status": "PENDING",
        "user": 1,
        "amount": random_amount(),
        "created_at": str(current_time),
    }
    response = requests.post(f"{url}add-transaction/", json=payload)

    if response.status_code == 200:
        return {True}
    else:
        return False


send_request_flag = threading.Event()
send_request_flag.set()


def test_api_speed(dps=1):
    timer_thread = threading.Timer(1, send_request_flag.clear)
    timer_thread.start()

    i = 0
    while send_request_flag.is_set() and i < dps:
        if i == 0:
            start_time = datetime.now(ZoneInfo("UTC"))

        i += 1

        if i == dps:
            end_time = datetime.now(ZoneInfo("UTC"))

        req = threading.Thread(target=send_request)
        req.start()
        # if req:
        #     continue
        # else:
        #     print(f"failed on last request, requests sent: {i}")
        #     return

    diff = relativedelta(start_time, end_time)
    if diff.seconds < 1:
        timer_thread.cancel()
        print(dps, diff, end_time, start_time)
        thread = threading.Thread(target=test_api_speed, args=(dps + 10,))
        thread.start()
    elif not i == dps:
        thread = threading.Thread(target=test_api_speed, args=(dps - 1,))
        thread.start()
    else:
        print(f"this api can handle maximum of {dps} requests per second")

    print(f"{dps} data were sent successfully to requested api.")


test_api_speed()
