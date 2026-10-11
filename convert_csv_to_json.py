import csv
import json

def convert():
    records = []
    with open('wipkingen_nuisance_ledger.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                'id': row['service_request_id'],
                'date': row['requested_datetime'],
                'service': row['service_name'],
                'title': row['title'],
                'desc': row['description'],
                'status': row['status'],
                'lat': float(row['lat']),
                'lon': float(row['lon'])
            })

    with open('unity_assets/historical_data.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False)

    print(f"Successfully converted {len(records)} records to unity_assets/historical_data.json")

if __name__ == "__main__":
    convert()
