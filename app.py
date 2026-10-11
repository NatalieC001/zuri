import os
import csv
from flask import Flask, render_template_string, jsonify
import folium
from folium.plugins import HeatMap
from scrape_live_nuisances import scrape_live_data

app = Flask(__name__)

LEDGER_FILE = "wipkingen_nuisance_ledger.csv"
TARGET_LAT = 47.3948
TARGET_LON = 8.5315

def generate_map_html():
    # Base map centered around Lagernstrasse
    m = folium.Map(location=[TARGET_LAT, TARGET_LON], zoom_start=15)

    # Read the ledger data
    heat_data = []

    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = float(row['lat'])
                lon = float(row['lon'])
                heat_data.append([lat, lon])

                # Add markers for each point (perhaps limiting markers to avoid browser crash,
                # but let's try adding them all since the user wants to see real locations)
                # To prevent too much clutter, we can add them to a FastMarkerCluster if needed,
                # but standard markers or circles work nicely.
                popup_html = f"""
                <b>{row['title']}</b><br>
                <i>{row['service_name']}</i><br>
                {row['requested_datetime']}<br>
                <hr>
                <p>{row['description']}</p>
                <b>Status:</b> {row['status']}
                """
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=4,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)

    # Add heatmap layer
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10).add_to(m)

    return m.get_root().render()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wipkingen 8037 Nuisance Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        header { background: #333; color: #fff; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        h1 { margin: 0; font-size: 1.5em; }
        button { padding: 10px 15px; font-size: 1em; cursor: pointer; background: #e74c3c; color: white; border: none; border-radius: 4px; }
        button:hover { background: #c0392b; }
        #map-container { width: 100%; height: calc(100vh - 60px); border: none; }
    </style>
</head>
<body>

<header>
    <h1>Wipkingen 8037 Nuisance Tracker</h1>
    <div>
        <button id="scrapeBtn" onclick="triggerScrape()">Fetch Live Updates from Open311</button>
    </div>
</header>

<iframe id="map-container" src="/map"></iframe>

<script>
function triggerScrape() {
    const btn = document.getElementById('scrapeBtn');
    btn.disabled = true;
    btn.innerText = "Fetching...";

    fetch('/scrape')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            // Refresh the map iframe
            document.getElementById('map-container').src = document.getElementById('map-container').src;
        })
        .catch(err => {
            alert("Error fetching data: " + err);
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerText = "Fetch Live Updates from Open311";
        });
}
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/map")
def map_view():
    return generate_map_html()

@app.route("/scrape")
def trigger_scrape():
    try:
        scrape_live_data()
        return jsonify({"status": "success", "message": "Successfully scraped the latest data. Ledger updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
