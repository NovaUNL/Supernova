from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError


def get_weekday_occurrences(from_date, to_date):
    try:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(detail="Bad date range")
    if to_date < from_date:
        raise ValidationError(detail="Range goes back in time")

    delta: timedelta = to_date - from_date
    if delta.days > 31:
        raise ValidationError(detail="Range exceeds limit")

    weekday_occurrences = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    day = from_date
    for _ in range(delta.days):
        weekday_occurrences[day.weekday()].append(day)
        day = day + timedelta(days=1)
    return weekday_occurrences
