from datetime import datetime, timedelta
from itertools import chain

from django.core.cache import cache
from scrapper.transportation import mts, tst

import logging

logger = logging.getLogger(__name__)


def get_transportation_departures(use_cache_alone=False):
    departures = cache.get('departures')
    if departures is None:
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        mts_departures, mts_cacheable = mts.get_departure_times()
        tst_departures, tst_cacheable = tst.get_departure_times(use_cache_alone=use_cache_alone)

        departures = list(chain(
            mts_departures,
            tst_departures
        ))
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
        if mts_cacheable and tst_cacheable:
            cache.set('departures', departures, timeout=60 * 10)
    return departures


def get_file_name_parts(name):
    name_parts = name.split('.')
    if len(name_parts) > 1:
        extension = name_parts[-1]
        if extension == '':
            return name, None
        else:
            return name[:len(extension)], extension
    return name, None


def prettify_file_name(name):
    name = name.replace('_', ' ').capitalize()
    return name
