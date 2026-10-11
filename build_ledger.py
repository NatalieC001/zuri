import json
import csv

def build_initial_ledger(input_json, output_csv):
    print(f"Loading filtered historical data from {input_json}...")
    with open(input_json, 'r', encoding='utf-8') as f:
        features = json.load(f)

    print(f"Loaded {len(features)} records.")

    # Define columns for our permanent ledger
    fieldnames = [
        'service_request_id', # Unique ID
        'requested_datetime', # Date of report
        'service_name',       # Category
        'title',              # Title of report
        'description',        # Details
        'status',             # Current status
        'lat',                # WGS84 Latitude
        'lon'                 # WGS84 Longitude
    ]

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for feature in features:
            props = feature.get('properties', {})

            row = {
                'service_request_id': props.get('service_request_id', ''),
                'requested_datetime': props.get('requested_datetime', ''),
                'service_name': props.get('service_name', ''),
                'title': props.get('title', ''),
                'description': props.get('detail', ''), # OpenData uses 'detail' for description
                'status': props.get('status', ''),
                'lat': props.get('wgs84_lat', ''),
                'lon': props.get('wgs84_lon', '')
            }
            writer.writerow(row)

    print(f"Successfully wrote {len(features)} records to {output_csv}.")

if __name__ == "__main__":
    build_initial_ledger('filtered_nuisances.json', 'wipkingen_nuisance_ledger.csv')
