from datetime import datetime, timedelta
from itertools import chain

from django.core.cache import cache
from scrapper.transportation import mts, tst


def get_transportation_departures():
    departures = cache.get('departures')
    if departures is None:
        try:
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            departures = list(chain(mts.get_departure_times(), tst.get_departure_times()))
            curr_time = now.time()
            for departure in departures:
                departure_time = departure['time']
                if curr_time < departure_time:
                    departure['datetime'] = midnight + timedelta(
                        hours=departure_time.hour, minutes=departure_time.minute)
                else:
                    departure['datetime'] = midnight + timedelta(
                        days=1, hours=departure_time.hour, minutes=departure_time.minute)
            departures.sort(key=lambda departure: departure['datetime'])
            departures = departures
            cache.set('departures', departures, timeout=60 * 10)
        except Exception:
            departures = []
    return departures
