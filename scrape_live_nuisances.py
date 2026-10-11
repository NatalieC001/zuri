import urllib.request
import json
import csv
import math
import os
from datetime import datetime

# Target coordinates: Lagernstrasse 8037 Zurich
TARGET_LAT = 47.3948
TARGET_LON = 8.5315
RADIUS_KM = 1.0

# API Endpoint for Live Züri wie neu Open311 Requests
API_URL = "https://www.zueriwieneu.ch/open311/v2/requests.json?jurisdiction_id=zurich"

# File to store the ledger
LEDGER_FILE = "wipkingen_nuisance_ledger.csv"

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def scrape_live_data():
    print(f"[{datetime.now().isoformat()}] Fetching live Open311 data from Züri wie neu...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0 NuisanceScraper/1.0'})
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise e

    # Load existing IDs to avoid duplicates
    existing_ids = set()
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(str(row['service_request_id']))

    new_records = []

    requests_list = data.get('service_requests', [])
    if isinstance(data, list):
        requests_list = data

    for req_data in requests_list:
        req_id = str(req_data.get('service_request_id'))

        if req_id in existing_ids:
            continue

        lat = req_data.get('lat')
        lon = req_data.get('long') # Open311 uses 'long'

        if not lat or not lon:
            continue

        dist_km = haversine(TARGET_LON, TARGET_LAT, lon, lat)

        # Relevant categories for "nuisance" / mischief
        NUISANCE_CATEGORIES = [
            'Graffiti',
            'Abfall/Sammelstelle',
            'Signalisation/Lichtsignal',
            'Strasse/Trottoir/Platz',
            'Beleuchtung/Uhren'
        ]

        service_name = req_data.get('service_name', '')

        # Check if within Wipkingen/Lagernstrasse area and matches a nuisance category
        if dist_km <= RADIUS_KM and service_name in NUISANCE_CATEGORIES:
            new_records.append({
                'service_request_id': req_id,
                'requested_datetime': req_data.get('requested_datetime', ''),
                'service_name': req_data.get('service_name', ''),
                'title': req_data.get('title', ''),
                'description': req_data.get('detail', req_data.get('description', '')),
                'status': req_data.get('status', ''),
                'lat': lat,
                'lon': lon
            })

    if new_records:
        print(f"Found {len(new_records)} NEW relevant incidents! Appending to ledger.")
        file_exists = os.path.exists(LEDGER_FILE)
        with open(LEDGER_FILE, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['service_request_id', 'requested_datetime', 'service_name', 'title', 'description', 'status', 'lat', 'lon']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for r in new_records:
                writer.writerow(r)
    else:
        print("No new relevant incidents found.")

if __name__ == "__main__":
    scrape_live_data()
