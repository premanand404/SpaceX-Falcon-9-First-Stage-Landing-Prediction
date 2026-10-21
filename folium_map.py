"""Create a real interactive Folium map for launch records."""
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from src.common import ROOT, OUTPUT_DIR, load_course_csv, ensure_class

FALLBACK_COORDS = {
    "CCAFS SLC 40": (28.561857, -80.577366),
    "CCAFS LC-40": (28.561857, -80.577366),
    "KSC LC 39A": (28.608059, -80.603956),
    "KSC LC-39A": (28.608059, -80.603956),
    "VAFB SLC 4E": (34.632093, -120.610829),
}


def main():
    df = ensure_class(load_course_csv("dataset_part_2.csv"))
    site_col = "LaunchSite" if "LaunchSite" in df else "launch_site"
    lat_col = "Latitude" if "Latitude" in df else "latitude"
    lon_col = "Longitude" if "Longitude" in df else "longitude"
    if lat_col not in df or lon_col not in df:
        coords = df[site_col].astype(str).map(FALLBACK_COORDS)
        df["_lat"] = coords.map(lambda x: x[0] if isinstance(x, tuple) else None)
        df["_lon"] = coords.map(lambda x: x[1] if isinstance(x, tuple) else None)
        lat_col, lon_col = "_lat", "_lon"
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    center = [float(df[lat_col].mean()), float(df[lon_col].mean())]
    m = folium.Map(location=center, zoom_start=4, tiles="OpenStreetMap")
    cluster = MarkerCluster(name="Launch records").add_to(m)
    for _, row in df.iterrows():
        success = int(row.get("Class", 0) or 0) == 1
        site = str(row.get(site_col, "Unknown site"))
        flight = row.get("FlightNumber", row.get("flight_number", "n/a"))
        payload = row.get("PayloadMass", row.get("payload_mass__kg_", "n/a"))
        orbit = row.get("Orbit", row.get("orbit", "n/a"))
        popup = folium.Popup(f"<b>{site}</b><br>Flight: {flight}<br>Payload: {payload}<br>Orbit: {orbit}<br>Landing class: {int(success)}", max_width=300)
        folium.CircleMarker(location=[row[lat_col], row[lon_col]], radius=5, color="#109e8f" if success else "#eb7056", fill=True, fill_opacity=.8, popup=popup, tooltip=f"{site} | Class {int(success)}").add_to(cluster)
    folium.LayerControl().add_to(m)
    out = OUTPUT_DIR / "launch_map.html"
    m.save(str(out))
    print(f"Created interactive map: {out}")

if __name__ == "__main__":
    main()
