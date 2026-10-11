import json
import math

# Target coordinates: Lagernstrasse 8037 Zurich (Approx: 47.3948 N, 8.5315 E)
TARGET_LAT = 47.3948
TARGET_LON = 8.5315
RADIUS_KM = 1.0

# Relevant categories for "nuisance" / mischief
# The dataset has unicode issues with some names, we can check prefix or pure strings
NUISANCE_CATEGORIES = [
    'Graffiti',
    'Abfall/Sammelstelle',
    'Signalisation/Lichtsignal',
    'Strasse/Trottoir/Platz',
    'Beleuchtung/Uhren' # often vandalism against lights
]

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def process_data(input_file, output_file):
    print("Loading raw data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    filtered_features = []

    print(f"Total features in dataset: {len(features)}")

    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        if not geom or geom.get('type') != 'Point':
            continue

        coords = geom.get('coordinates', [])
        if len(coords) < 2:
            continue

        service_name = props.get('service_name', '')
        if service_name not in NUISANCE_CATEGORIES:
            continue

        # The WFS output in EPSG:4326 comes out as [lon, lat] directly
        lon, lat = coords[0], coords[1]

        # Calculate distance to Lagernstrasse
        dist_km = haversine(TARGET_LON, TARGET_LAT, lon, lat)

        if dist_km <= RADIUS_KM:
            props['wgs84_lon'] = lon
            props['wgs84_lat'] = lat
            filtered_features.append(feature)

    print(f"Features found within {RADIUS_KM}km matching nuisance categories: {len(filtered_features)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_features, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_data('zueri_wie_neu.json', 'filtered_nuisances.json')
