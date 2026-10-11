// Constants
const TARGET_LAT = 47.3948;
const TARGET_LON = 8.5315;
const RADIUS_KM = 1.0;
const API_URL = "https://www.zueriwieneu.ch/open311/v2/requests.json?jurisdiction_id=zurich";

const NUISANCE_CATEGORIES = [
    'Graffiti',
    'Abfall/Sammelstelle',
    'Signalisation/Lichtsignal',
    'Strasse/Trottoir/Platz',
    'Beleuchtung/Uhren'
];

// Initialize Map
const map = L.map('map').setView([TARGET_LAT, TARGET_LON], 15);

// Add OpenStreetMap base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Data tracking
let heatmapLayer = null;
const allPoints = []; // Stores {lat, lon} for heatmap
const existingIds = new Set();

// Utility: Haversine distance
function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
    var R = 6371; // Radius of the earth in km
    var dLat = deg2rad(lat2 - lat1);
    var dLon = deg2rad(lon2 - lon1);
    var a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c; // Distance in km
    return d;
}

function deg2rad(deg) {
    return deg * (Math.PI / 180)
}

// Add a marker to the map and record for heatmap
function addIncidentToMap(incident, isNew = false) {
    if (existingIds.has(incident.id)) return false;

    existingIds.add(incident.id);

    // Add to heatmap data
    allPoints.push([incident.lat, incident.lon, 1.0]); // Lat, Lon, Intensity

    // Create Popup HTML
    const popupContent = `
        <div class="popup-title">${incident.title || 'Incident'} ${isNew ? '<span style="color:red">(NEW)</span>' : ''}</div>
        <div class="popup-meta"><b>Type:</b> ${incident.service} | <b>Date:</b> ${new Date(incident.date).toLocaleString()}</div>
        <div class="popup-desc">${incident.desc || 'No description provided.'}</div>
        <div class="popup-meta"><b>Status:</b> ${incident.status}</div>
    `;

    // Create Circle Marker
    L.circleMarker([incident.lat, incident.lon], {
        radius: isNew ? 6 : 4,
        fillColor: isNew ? "#f1c40f" : "#e74c3c", // Yellow for new, Red for history
        color: isNew ? "#f39c12" : "#c0392b",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).bindPopup(popupContent).addTo(map);

    return true;
}

// Update the heatmap layer
function renderHeatmap() {
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
    }

    heatmapLayer = L.heatLayer(allPoints, {
        radius: 20,
        blur: 15,
        maxZoom: 17,
        gradient: {0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
    }).addTo(map);
}

// Load historical data
async function loadHistoricalData() {
    try {
        const response = await fetch('historical_data.json');
        if (!response.ok) throw new Error("Could not load historical JSON");

        const data = await response.json();
        console.log(`Loaded ${data.length} historical records.`);

        data.forEach(item => {
            addIncidentToMap(item, false);
        });

        renderHeatmap();
    } catch (error) {
        console.error("Error loading historical data. If opening from file:// protocol, Chrome blocks JSON loading. You may need a local server or Unity WebView to run this correctly.", error);
    }
}

// Rate Limiting Constants
const FETCH_COOLDOWN_MS = 60000; // 60 seconds
let lastFetchTime = 0;

// Fetch live reports
async function fetchLiveReports() {
    const now = Date.now();
    const btn = document.getElementById('live-btn');

    // Polite scraping: prevent spamming the API
    if (now - lastFetchTime < FETCH_COOLDOWN_MS) {
        const remainingSecs = Math.ceil((FETCH_COOLDOWN_MS - (now - lastFetchTime)) / 1000);
        alert(`Please wait ${remainingSecs} seconds before fetching again to respect server limits.`);
        return;
    }

    btn.disabled = true;
    btn.innerText = "Fetching...";

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("API Network response was not ok");

        const data = await response.json();
        let requestsList = Array.isArray(data) ? data : (data.service_requests || []);

        let newCount = 0;

        requestsList.forEach(req => {
            const lat = parseFloat(req.lat);
            const lon = parseFloat(req.long || req.lon);
            const service = req.service_name || '';
            const reqId = String(req.service_request_id);

            if (!lat || !lon) return;

            const dist = getDistanceFromLatLonInKm(TARGET_LAT, TARGET_LON, lat, lon);

            if (dist <= RADIUS_KM && NUISANCE_CATEGORIES.includes(service)) {

                const incident = {
                    id: reqId,
                    lat: lat,
                    lon: lon,
                    title: req.title,
                    service: service,
                    desc: req.detail || req.description,
                    date: req.requested_datetime,
                    status: req.status
                };

                if (addIncidentToMap(incident, true)) {
                    newCount++;
                }
            }
        });

        if (newCount > 0) {
            renderHeatmap();
            alert(`Found ${newCount} new incident(s) in the Wipkingen area!`);
        } else {
            alert("No new relevant incidents found.");
            console.log("No new relevant incidents found.");
        }

        lastFetchTime = Date.now(); // Update the successful fetch time

    } catch (error) {
        console.error("Failed to fetch live reports:", error);
        alert("Failed to fetch live data. Please check your internet connection.");
    } finally {
        btn.disabled = false;
        btn.innerText = "Refresh Live Data";
    }
}

// Init
window.onload = () => {
    loadHistoricalData();
};
