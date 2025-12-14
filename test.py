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


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text):
    """prints centered header with colors""" 
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """prints green success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """prints red error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text):
    """prints blue info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """prints yellow warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_menu_option(number, text):
    """prints menu option with number"""
    print(f"{Colors.BOLD}{Colors.YELLOW}[{number}]{Colors.ENDC} {text}")


def random_id():
    """generates random transaction id"""
    return "".join(random.choices(string.digits, k=16))


def random_amount():
    """generates random amount"""
    return "".join(random.choices(string.digits, k=3))


url = "http://127.0.0.1:8000/api/"


def send_request(post_url, payload, request_id):
    """sends single transaction request

    Args:
        post_url (str): The URL to send the request to.
        payload (dict): The payload to send with the request.
        request_id (int): The ID of the request.

    Returns:
        dict: A dictionary containing the result of the request."
    """
    try:
        response = requests.post(post_url, json=payload)
        response.raise_for_status()
        return {"id": request_id, "status": "success", "code": response.status_code}
    except Exception as e:
        return {"id": request_id, "status": "failed", "error": str(e)}


def test_api_speed(dps):
    """tests api speed with concurrent requests

    Args:
        dps (int): The number of requests per second.

    Returns:
        None
    """
    print_header("API SPEED TEST")
    future_to_req = []
    post_url = f"{url}add-transaction/"

    start_time = time.time()
    is_one_second = True

    print_info(
        f"Sending {Colors.BOLD}{dps}{Colors.ENDC}{Colors.BLUE} requests...{Colors.ENDC}"
    )

    while is_one_second:
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
    failed_requests = []

    for future in concurrent.futures.as_completed(future_to_req):
        result = future.result()
        results.append(result)

        if result["status"] == "failed":
            failed_requests.append(result)

    duration = time.time() - start_time
    success_counts = sum(1 for r in results if r["status"] == "success")
    fail_counts = len(results) - success_counts

    print(f"\n{Colors.BOLD}{'─'*60}{Colors.ENDC}")
    print_success(f"Duration: {Colors.BOLD}{duration:.2f}s{Colors.ENDC}{Colors.GREEN}")
    print_success(
        f"Success: {Colors.BOLD}{success_counts}{Colors.ENDC}{Colors.GREEN} / {len(results)}"
    )

    if fail_counts > 0:
        print_error(
            f"Failed: {Colors.BOLD}{fail_counts}{Colors.ENDC}{Colors.RED} / {len(results)}"
        )
        print(f"\n{Colors.RED}Failed Requests:{Colors.ENDC}")
        for req in failed_requests[:5]:
            print_error(f"  Request {req['id']}: {req['error']}")
        if len(failed_requests) > 5:
            print_error(f"  ... and {len(failed_requests) - 5} more")
    else:
        print_success(
            f"Failed: {Colors.BOLD}0{Colors.ENDC}{Colors.GREEN} / {len(results)}"
        )

    print(f"{Colors.BOLD}{'─'*60}{Colors.ENDC}\n")

    print_menu_option("1", "Test again")
    print_menu_option("0", "Return to main menu")
    option = input(f"\n{Colors.BOLD}Your choice: {Colors.ENDC}").strip()

    if option == "1":
        try:
            new_dps = int(input(f"{Colors.CYAN}Enter data per second: {Colors.ENDC}"))
            test_api_speed(new_dps)
        except ValueError:
            print_error("Invalid input. Returning to main menu.")
            main()
    elif option == "0":
        main()
    else:
        print_error("Invalid option. Returning to main menu.")
        main()


def main():
    """main menu for test cli"""
    print_header("TRANSACTION MONITORING - TEST CLI")
    print_menu_option("1", "Test API Speed")
    print_menu_option("2", "Get Transaction Statistics")
    print_menu_option("0", "Exit")

    option = input(f"\n{Colors.BOLD}Your choice: {Colors.ENDC}").strip()

    if option == "1":
        try:
            dps = int(input(f"{Colors.CYAN}Enter data per second, 0 to return to main menu: {Colors.ENDC}"))
            if dps == 0:
                main()
            test_api_speed(dps)
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            main()
    elif option == "2":
        try:
            test_get_transaction_statistics()
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            main()
    elif option == "0":
        print_success("Goodbye!")
        exit()
    else:
        print_error("Invalid option. Please try again.")
        main()


def test_get_transaction_statistics():
    """gets and displays transaction statistics"""
    print_header("TRANSACTION STATISTICS")

    print_info("Date format: YYYY-MM-DD HH:MM:SS")
    print_info("Press Enter for no limit, or type '0' to return\n")

    from_datetime = input(f"{Colors.CYAN}From date: {Colors.ENDC}").strip()
    to_datetime = input(f"{Colors.CYAN}To date: {Colors.ENDC}").strip()

    if from_datetime == "0" or to_datetime == "0":
        main()
        return

    from_datetime, to_datetime = validate_datetime(from_datetime, to_datetime)
    get_url = f"{url}transactions"

    print_info("Fetching statistics...")

    try:
        response = requests.get(
            get_url, params={"from": from_datetime, "to": to_datetime}
        )
        response.raise_for_status()
        data = response.json()

        print(f"\n{Colors.BOLD}{'─'*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}TRANSACTION STATISTICS{Colors.ENDC}\n")

        if "data" in data:
            stats = data["data"]
            print(
                f"{Colors.CYAN}Time Frame:{Colors.ENDC} {Colors.BOLD}{stats.get('selected_time_frame', 'N/A')}{Colors.ENDC}"
            )
            print(
                f"{Colors.CYAN}Number of Sales:{Colors.ENDC} {Colors.BOLD}{stats.get('numer_of_sales', 0)}{Colors.ENDC}"
            )
            print(
                f"{Colors.CYAN}Total Profit:{Colors.ENDC} {Colors.BOLD}${stats.get('whole_profit', 0):,.2f}{Colors.ENDC}"
            )
            print(
                f"{Colors.CYAN}Average Transaction:{Colors.ENDC} {Colors.BOLD}${stats.get('avgerage_of_transactions', 0):,.2f}{Colors.ENDC}"
            )
        else:
            print(json.dumps(data, indent=2))

        print(f"{Colors.BOLD}{'─'*60}{Colors.ENDC}\n")

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")

    print_menu_option("1", "Test again")
    print_menu_option("0", "Return to main menu")
    option = input(f"\n{Colors.BOLD}Your choice: {Colors.ENDC}").strip()

    if option == "1":
        test_get_transaction_statistics()
    elif option == "0":
        main()
    else:
        print_error("Invalid option. Returning to main menu.")
        main()


def validate_datetime(from_date_str, to_date_str):
    """converts date strings to iso format

    Args:
        from_date_str (str): The start date string in format YYYY-MM-DD HH:MM:SS.
        to_date_str (str): The end date string in format YYYY-MM-DD HH:MM:SS.

    Returns:
        tuple: A tuple containing the start and end datetime objects.
    """
    try:
        if from_date_str:
            from_datetime = datetime.strptime(from_date_str, "%Y-%m-%d %H:%M:%S")
        else:
            from_datetime = ""

        if to_date_str:
            to_datetime = datetime.strptime(to_date_str, "%Y-%m-%d %H:%M:%S")
        else:
            to_datetime = ""

        return from_datetime, to_datetime
    except ValueError:
        print_error("Invalid date format. Please use: YYYY-MM-DD HH:MM:SS")
        return test_get_transaction_statistics()


if __name__ == "__main__":
    main()
