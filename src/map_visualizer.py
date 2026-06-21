"""
Map visualization utilities using Folium
"""
import folium
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / 'outputs' / 'maps'

def create_base_map(roads_df, center=None):
    """
    Create a base map with road network
    """
    # Determine center
    if center is None:
        if 'node_lat' in roads_df.columns and 'node_lon' in roads_df.columns:
            center_lat = roads_df['node_lat'].mean()
            center_lon = roads_df['node_lon'].mean()
        else:
            center_lat, center_lon = 0, 0

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )

    # Add roads
    if 'node_lat' in roads_df.columns and 'node_lon' in roads_df.columns:
        for _, row in roads_df.iterrows():
            if 'to_lat' in roads_df.columns and 'to_lon' in roads_df.columns:
                folium.PolyLine(
                    locations=[
                        [row['node_lat'], row['node_lon']],
                        [row['to_lat'], row['to_lon']]
                    ],
                    color='gray',
                    weight=2,
                    opacity=0.6
                ).add_to(m)

    print(f"🗺️  Base map created with {len(roads_df)} road segments")
    return m

def add_events_to_map(m, events_df):
    """Add event markers to map"""
    if 'lat' not in events_df.columns or 'lon' not in events_df.columns:
        print("⚠️  No lat/lon in events data")
        return m

    for _, event in events_df.iterrows():
        popup_text = event.get('name', 'Event')
        if 'start_time' in event:
            popup_text += f"\nStart: {event['start_time']}"

        folium.Marker(
            [event['lat'], event['lon']],
            popup=popup_text,
            icon=folium.Icon(color='red', icon='calendar', prefix='fa')
        ).add_to(m)

    print(f"📍 Added {len(events_df)} event markers")
    return m

def add_hotspots_to_map(m, traffic_df, roads_df, top_n=10):
    """
    Add top congested nodes as hotspots
    """
    if 'volume' not in traffic_df.columns or 'nearest_node' not in traffic_df.columns:
        print("⚠️  Cannot add hotspots: missing volume or nearest_node")
        return m

    # Calculate average volume per node
    node_volumes = traffic_df.groupby('nearest_node')['volume'].mean()
    top_nodes = node_volumes.nlargest(top_n)

    # Get coordinates for these nodes
    for node_id, volume in top_nodes.items():
        node_row = roads_df[roads_df['node_id'] == node_id]
        if node_row.empty:
            continue

        lat = node_row['node_lat'].values[0]
        lon = node_row['node_lon'].values[0]

        folium.CircleMarker(
            [lat, lon],
            radius=10,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.6,
            popup=f"Node {node_id}\nVolume: {volume:.0f}"
        ).add_to(m)

    print(f"🔥 Added {len(top_nodes)} hotspots")
    return m

def save_map(m, filename='phase1_map.html'):
    """Save map to outputs folder"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    m.save(str(path))
    print(f"💾 Map saved to: {path}")
    return path