import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster
from sklearn.cluster import DBSCAN


def detect_hotspots(df: pd.DataFrame, eps_degrees: float = 0.006, min_samples: int = 8) -> pd.DataFrame:
    data = df.dropna(subset=["latitude", "longitude"]).copy()
    coords = data[["latitude", "longitude"]].to_numpy()
    labels = DBSCAN(eps=eps_degrees, min_samples=min_samples).fit_predict(coords)
    data["hotspot_cluster"] = labels
    return data


def summarize_hotspots(df: pd.DataFrame) -> pd.DataFrame:
    clustered = df[df["hotspot_cluster"] >= 0].copy()
    if clustered.empty:
        return pd.DataFrame()
    summary = (
        clustered.groupby("hotspot_cluster")
        .agg(
            events=("id", "count"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            high_priority_rate=("high_priority_flag", "mean"),
            closure_rate=("closure_flag", "mean"),
            top_corridor=("corridor", lambda s: s.mode().iat[0] if not s.mode().empty else "Unknown"),
            top_cause=("event_cause", lambda s: s.mode().iat[0] if not s.mode().empty else "Unknown"),
            top_station=("police_station", lambda s: s.mode().iat[0] if not s.mode().empty else "Unknown"),
        )
        .reset_index()
        .sort_values(["events", "high_priority_rate", "closure_rate"], ascending=False)
    )
    summary["risk_score"] = (
        0.55 * (summary["events"] / summary["events"].max())
        + 0.25 * summary["high_priority_rate"]
        + 0.20 * summary["closure_rate"]
    ) * 100
    return summary.sort_values("risk_score", ascending=False)


def create_incident_map(df: pd.DataFrame, output_path) -> None:
    center = [df["latitude"].mean(), df["longitude"].mean()]
    fmap = folium.Map(location=center, zoom_start=11, tiles="OpenStreetMap")
    heat_data = df[["latitude", "longitude"]].dropna().values.tolist()
    if heat_data:
        HeatMap(heat_data, radius=11, blur=16, min_opacity=0.25).add_to(fmap)

    marker_cluster = MarkerCluster(name="Incidents").add_to(fmap)
    sample = df.sample(min(len(df), 700), random_state=42) if len(df) > 700 else df
    for _, row in sample.iterrows():
        popup = (
            f"<b>{row.get('event_cause', 'Unknown')}</b><br>"
            f"Priority: {row.get('priority', 'Unknown')}<br>"
            f"Corridor: {row.get('corridor', 'Unknown')}<br>"
            f"Station: {row.get('police_station', 'Unknown')}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color="#d73027" if row.get("closure_flag", 0) else "#4575b4",
            fill=True,
            fill_opacity=0.7,
            popup=popup,
        ).add_to(marker_cluster)
    folium.LayerControl().add_to(fmap)
    fmap.save(str(output_path))
