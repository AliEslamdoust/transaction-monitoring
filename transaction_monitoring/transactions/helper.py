from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Min, Max
from datetime import datetime
from django.utils.dateparse import parse_datetime
from .models import Transaction


def validate_datetime(from_date_str, to_date_str):
    from_datetime = parse_datetime(from_date_str)
    to_datetime = parse_datetime(to_date_str)

    if not to_datetime:
        to_datetime = timezone.make_aware(datetime.max)

    if not from_datetime:
        from_datetime = timezone.make_aware(datetime.min)

    if timezone.is_naive(to_datetime):
        timezone.make_aware(to_datetime)

    if timezone.is_naive(from_datetime):
        timezone.make_aware(from_datetime)

    if to_datetime < from_datetime:
        to_datetime, from_datetime = from_datetime, to_datetime

    return from_datetime, to_datetime


def get_time_frame(to_datetime, from_datetime):
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
    dates = Transaction.objects.aggregate(
        earliest=Min("created_at"), latest=Max("created_at")
    )

    return dates["earliest"], dates["latest"]
