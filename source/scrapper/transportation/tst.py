from datetime import time

import requests
from bs4 import BeautifulSoup
from django.core.cache import cache

ROUTES_STOPS_URL = "http://myinfo.4cloud.pt/ip/WebIpService/Default.aspx" \
                   "?Request=%5Btype%3DGetNetwork%3BoperatorCastorId%3D104%5D"
BUSES_IN_STOP = "http://myinfo.4cloud.pt/ip/WebIpService/Default.aspx" \
                    "?Request=[type=GetNextStopTimes;stopId={STOP_ID};" \
                    "myInfoVersion=pt.card4b.tst_1.0.11_12;" \
                    "mac=12:12:12:12:12:12;so=android_27;device=NovaPhone]"


def get_departure_times():
    tst_bus_stops_lines, regen = _get_manifest()

    tst_relevant = None if regen else cache.get('tst_relevant')
    if tst_relevant is None:
        tst_relevant = _parse(tst_bus_stops_lines)
        cache.set('tst_relevant', tst_relevant, timeout=None)

    stops = tst_relevant['stops']
    relevant_stops = tst_relevant['stop_ids']
    lines = tst_relevant['line_names']
    departures = []

    for stop_id in relevant_stops:
        schedule = requests.post(url=BUSES_IN_STOP.format(STOP_ID=stop_id), headers={'User-Agent': "okhttp/3.14.0"})
        soup = BeautifulSoup(schedule.text, 'lxml')
        for stop_time in soup.find_all('stoptime'):
            line_id = int(stop_time.attrs['idline'])
            if line_id not in lines:
                continue
            destination_id = int(stop_time.attrs['stopdestination'])
            hour = time.fromisoformat(stop_time.attrs['hour'])
            planned_hour = time.fromisoformat(stop_time.attrs['plannedhour'])
            line_name = lines[line_id]
            destination = stops[destination_id]['name']
            if 'FCT' in destination:
                continue

            departures.append({
                'name': line_name,
                'time': hour,
                'time_prediction': planned_hour,
                'destination': __simplify_destination_name(destination)})
    return departures


def __simplify_destination_name(name):
    if name.startswith('Caci'):
        return 'Cacilhas'
    elif name.startswith('Cost'):
        return 'Costa Caparica (Argolas)'
    elif name.startswith('Mar'):
        return 'Marisol'
    elif name.startswith('Pai'):
        return 'Paio Pires (Centro)'
    elif name.startswith('Tra'):
        return 'Trafaria'
    elif name.startswith('Por'):
        return 'Porto Brandão'
    elif name.startswith('Monte'):
        return 'Monte Caparica, Fomega'
    elif name.startswith('Lis'):
        return 'Lisboa (Pça Espanha)'
    return name


def _get_manifest():
    tst_bus_stops_lines = cache.get('tst_lines_xml')  # TODO replace with TTL
    regen = False
    if tst_bus_stops_lines is None:
        reply = requests.post(url=ROUTES_STOPS_URL, headers={'User-Agent': "okhttp/3.14.0"})
        tst_bus_stops_lines = reply.text
        cache.set('tst_lines_xml', tst_bus_stops_lines, timeout=None)
        regen = True
    return tst_bus_stops_lines, regen


def _parse(tst_bus_stops_routes):
    relevant_zone_lines = {
        # Entrada Principal
        'Monte Caparica (FCT) Rotunda': ['124', '125', '126', '127', '145', '146', '158', '194', '198'],
        # Rotunda MTS
        'Monte Caparica (Avª Timor Lorosae) (X) Porto Brandão': ['146'],
        # Paragem MTS
        'EN 10-1 (Qta Torrinha) P Telecom': ['125', '158'],
    }
    relevant_line_names = set([y for x in relevant_zone_lines.values() for y in x])

    soup = BeautifulSoup(tst_bus_stops_routes, 'lxml')
    # zones_tag = soup.find('zones')
    # tst_zones = {int(zone.attrs['id']): zone.attrs['name']
    #              for zone in zones_tag.find_all('operatorzone')}

    stops_tag = soup.find('stops')
    tst_stops = {int(stop.attrs['id']): {
        'id': int(stop.attrs['id']),
        'name': stop.attrs['name'],
        # 'zone': tst_zones[int(stop.attrs['idzona'])],
        'lon': float(stop.attrs['coordxx']),
        'lat': float(stop.attrs['coordyy'])
    } for stop in stops_tag.find_all('stop')}

    relevant_stops = {
        stop_id: stop_properties
        for stop_id, stop_properties in tst_stops.items()
        if stop_properties['name'] in relevant_zone_lines}

    relevant_stop_ids = set()
    relevant_line_stops = set()
    line_names = dict()
    lines_tag = soup.find('lines')
    for line_tag in lines_tag.find_all('line'):
        line_name = line_tag.attrs['companyid']  # Bus identifier
        if line_name not in relevant_line_names:
            continue
        line_id = int(line_tag.attrs['id'])  # Usage unknown

        line_names[line_id] = line_name

        for line_stop_tag in line_tag.find_all('stopline'):
            stop_id = int(line_stop_tag.attrs['idstop'])  # The stop identifier
            if stop_id in relevant_stops and line_name in relevant_zone_lines[relevant_stops[stop_id]['name']]:
                line_stop_id = int(line_stop_tag.attrs['id'])  # The identifier of this stop in this line
                relevant_stop_ids.add(stop_id)
                relevant_line_stops.add(line_stop_id)

    relevant = {
        'stops': tst_stops,
        'line_names': line_names,
        'stop_ids': relevant_stop_ids,
    }
    return relevant
