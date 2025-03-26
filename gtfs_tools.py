
import tempfile
import requests
import zipfile
import io
import csv
import os
import time
from datetime import datetime

CACHE_PATH = "/tmp/gtfs.zip"
CACHE_TTL = 60 * 60  # 1 hour

def download_gtfs():
    now = time.time()
    if os.path.exists(CACHE_PATH):
        if now - os.path.getmtime(CACHE_PATH) < CACHE_TTL:
            print("Using cached GTFS data")
            return CACHE_PATH

    print("Downloading fresh GTFS data")
    zip_url = 'https://transport.tallinn.ee/data/gtfs.zip'
    response = requests.get(zip_url)
    with open(CACHE_PATH, 'wb') as f:
        f.write(response.content)
    return CACHE_PATH

def find_oilme_stops_and_routes():
    zip_path = download_gtfs()
    oilme_stop_ids = []
    routes_data = {}
    trips_data = {}
    routes_with_oilme = set()

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open('stops.txt') as stops_file:
            reader = csv.DictReader(io.TextIOWrapper(stops_file, encoding='utf-8-sig'))
            for row in reader:
                if 'Õilme' in row['stop_name']:
                    oilme_stop_ids.append(row['stop_id'])

        with zip_ref.open('routes.txt') as routes_file:
            reader = csv.DictReader(io.TextIOWrapper(routes_file, encoding='utf-8-sig'))
            for row in reader:
                routes_data[row['route_id']] = row

        with zip_ref.open('trips.txt') as trips_file:
            reader = csv.DictReader(io.TextIOWrapper(trips_file, encoding='utf-8-sig'))
            for row in reader:
                trips_data[row['trip_id']] = row

        with zip_ref.open('stop_times.txt') as stop_times_file:
            reader = csv.DictReader(io.TextIOWrapper(stop_times_file, encoding='utf-8-sig'))
            for row in reader:
                if row['stop_id'] in oilme_stop_ids:
                    trip_id = row['trip_id']
                    if trip_id in trips_data:
                        route_id = trips_data[trip_id]['route_id']
                        if route_id in routes_data:
                            route_short_name = routes_data[route_id]['route_short_name']
                            routes_with_oilme.add(route_short_name)

    return {
        "oilme_stop_ids": oilme_stop_ids,
        "routes_with_oilme": sorted(list(routes_with_oilme))
    }

def get_schedule_for_route(route_short_name):
    zip_path = download_gtfs()
    oilme_stop_ids = []
    matched_route_ids = set()
    matched_trip_ids = set()
    schedule = []
    trip_headsigns = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open('stops.txt') as stops_file:
            reader = csv.DictReader(io.TextIOWrapper(stops_file, encoding='utf-8-sig'))
            for row in reader:
                if 'Õilme' in row['stop_name']:
                    oilme_stop_ids.append(row['stop_id'])

        with zip_ref.open('routes.txt') as routes_file:
            reader = csv.DictReader(io.TextIOWrapper(routes_file, encoding='utf-8-sig'))
            for row in reader:
                if row['route_short_name'] == route_short_name:
                    matched_route_ids.add(row['route_id'])

        with zip_ref.open('trips.txt') as trips_file:
            reader = csv.DictReader(io.TextIOWrapper(trips_file, encoding='utf-8-sig'))
            for row in reader:
                if row['route_id'] in matched_route_ids:
                    matched_trip_ids.add(row['trip_id'])
                    trip_headsigns[row['trip_id']] = row['trip_headsign']

        with zip_ref.open('stop_times.txt') as stop_times_file:
            reader = csv.DictReader(io.TextIOWrapper(stop_times_file, encoding='utf-8-sig'))
            for row in reader:
                if row['trip_id'] in matched_trip_ids and row['stop_id'] in oilme_stop_ids:
                    time_str = row['departure_time']
                    try:
                        dep_time = datetime.strptime(time_str, "%H:%M:%S").time()
                        now = datetime.now().time()
                        if dep_time > now:
                            schedule.append({
                                "time": dep_time.strftime('%H:%M'),
                                "headsign": trip_headsigns.get(row['trip_id'], '')
                            })
                    except:
                        continue

    return sorted(schedule, key=lambda x: x['time'])[:10]
