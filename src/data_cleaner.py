"""
Data cleaning and preprocessing utilities
"""
import pandas as pd
import numpy as np
from datetime import datetime

def clean_traffic(df):
    """
    Clean traffic data:
    - Handle missing values
    - Convert timestamps
    - Remove outliers
    """
    df = df.copy()

    # Convert timestamps if exists
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Handle missing volumes (assume 0)
    if 'volume' in df.columns:
        df['volume'] = df['volume'].fillna(0)

    # Remove outliers (e.g., volume > 99th percentile)
    if 'volume' in df.columns:
        cap = df['volume'].quantile(0.99)
        df.loc[df['volume'] > cap, 'volume'] = cap

    print(f"🧹 Cleaned traffic: {df.shape[0]} records")
    print(f"   Missing values: {df.isnull().sum().sum()}")
    return df

def clean_events(df):
    """Clean event data"""
    df = df.copy()

    # Ensure coordinates exist
    if 'lat' not in df.columns or 'lon' not in df.columns:
        print("⚠️  Warning: Missing lat/lon columns for events")

    # Convert event time if exists
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'])

    # Drop events with missing coordinates
    if 'lat' in df.columns and 'lon' in df.columns:
        df = df.dropna(subset=['lat', 'lon'])

    print(f"🧹 Cleaned events: {df.shape[0]} records")
    return df

def clean_roads(df):
    """Clean road network data"""
    df = df.copy()

    # Ensure node coordinates exist
    if 'node_lat' not in df.columns or 'node_lon' not in df.columns:
        print("⚠️  Warning: Missing node coordinates")

    # Drop rows with missing coordinates
    if 'node_lat' in df.columns and 'node_lon' in df.columns:
        df = df.dropna(subset=['node_lat', 'node_lon'])

    print(f"🧹 Cleaned roads: {df.shape[0]} records")
    return df