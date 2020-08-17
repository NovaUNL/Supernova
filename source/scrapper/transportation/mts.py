from datetime import time

import requests
from django.core.cache import cache


def get_departure_times():
    departure_times = cache.get('mts_departures')
    if departure_times is not None:
        return departure_times

    response = requests.post(
        "https://intranet.mts.pt/api/search",
        data={'line': 6, 'day_type': 1, 'season': 2, 'stations': 19})
    times = response.json()['data']['times']

    departure_times = [{'name': '3', 'time': _timestamp_to_time(time), 'destination': 'Cacilhas'} for time in times]
    cache.set('mts_departures', departure_times, timeout=None)
    return departure_times


def _timestamp_to_time(timestamp):
    minutes = int(timestamp['start_time']) // 60
    return time(hour=minutes // 60, minute=minutes % 60)
