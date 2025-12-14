from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Min, Max
from datetime import datetime
from django.utils.dateparse import parse_datetime
from .models import Transaction

def validate_datetime(datetime_str, is_min):
    """Validates and parses date strings.

    Args:
        datetime_str (str): The datetime string.
        is_min (bool): Whether the datetime is the minimum value.

    Returns:
        datetime: The validated datetime object.
    """
    parsed_datetime = parse_datetime(datetime_str)

    if not parsed_datetime:
        return (
            timezone.make_aware(datetime.min)
            if is_min
            else timezone.make_aware(datetime.max)
        )

    if is_min:
        if timezone.is_naive(parsed_datetime) or parsed_datetime < timezone.make_aware(datetime.min):
            parsed_datetime = timezone.make_aware(parsed_datetime)

    else:
        if timezone.is_naive(parsed_datetime) or parsed_datetime > timezone.make_aware(datetime.max):
            parsed_datetime = timezone.make_aware(parsed_datetime)

    return parsed_datetime


def get_time_frame(to_datetime, from_datetime):
    """calculates time difference between dates

    Args:
        to_datetime (datetime): The end datetime.
        from_datetime (datetime): The start datetime.

    Returns:
        str: A string representing the time difference.
    """
    earliest, latest = get_date()

    if from_datetime < earliest:
        from_datetime = earliest
    if to_datetime > latest:
        to_datetime = latest

    diff = relativedelta(to_datetime, from_datetime)

    parts = []

    if diff.years:
        parts.append(f"{diff.years} years")
    if diff.months:
        parts.append(f"{diff.months} months")
    if diff.days:
        parts.append(f"{diff.days} days")
    if diff.hours:
        parts.append(f"{diff.hours} hours")
    if diff.minutes:
        parts.append(f"{diff.minutes} minutes")
    if diff.seconds:
        parts.append(f"{diff.seconds} seconds")

    return ", ".join(parts) if parts else "0 seconds"


def get_date():
    """gets earliest and latest transaction dates

    Returns:
        tuple: A tuple containing the earliest and latest datetime objects.
    """
    dates = Transaction.objects.aggregate(
        earliest=Min("created_at"), latest=Max("created_at")
    )

    return dates["earliest"], dates["latest"]
