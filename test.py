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


send_request_flag = threading.Event()
send_request_flag.set()


def test_api_speed(dps=10):
    timer_thread = threading.Timer(1, send_request_flag.clear)
    timer_thread.start()

    # req = ""
    results = []
    future_to_req = []
    post_url = f"{url}add-transaction/"

    start_time = time.time()
    # i = 0
    # while send_request_flag.is_set() and i < dps:
    #     i += 1
    print(f"Started sending {dps} requests ...")

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

    for future in concurrent.futures.as_completed(future_to_req):
        result = future.result()
        results.append(result)
        
        if result["status"] == "failed":
            result_id = result["id"]
            result_err = result["error"]
            print(f"Request {result_id} failed: {result_err}")
            
    duration = time.time() - start_time
    print(f"Finished in {duration:.2f} seconds")
    
    success_counts = sum (1 for r in results if r["status"] == "success")
    fail_counts = dps - success_counts
    
    print(f"Success: {success_counts}")
    print(f"Failed: {fail_counts}")

    # num_of_tries = dps / 10
    # avg_of_all_tries = (dps + 10) / 2
    # total_requests = num_of_tries * avg_of_all_tries
    # print(total_requests)

    # req.join()
    # end_time = datetime.now(ZoneInfo("UTC"))
    # diff = relativedelta(start_time, end_time)

    # if diff.seconds < 1:
    #     timer_thread.cancel()
    #     print(dps, diff, end_time, start_time)
    #     thread = threading.Thread(target=test_api_speed, args=(dps + 10,))
    #     thread.start()
    # elif not i == dps:
    #     thread = threading.Thread(target=test_api_speed, args=(dps - 1,))
    #     thread.start()
    # else:
    #     print(f"this api can handle maximum of {dps} requests per second")

    # print(f"{dps} data were sent successfully to requested api.")


test_api_speed(1000)
