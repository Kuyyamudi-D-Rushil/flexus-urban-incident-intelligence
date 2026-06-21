import numpy as np
import pandas as pd


DATETIME_COLUMNS = [
    "start_datetime",
    "end_datetime",
    "created_date",
    "modified_datetime",
    "closed_datetime",
    "resolved_datetime",
]


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = (
        cleaned.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return cleaned


def clean_events(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_column_names(df)

    for column in DATETIME_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce", utc=True)

    for column in ["latitude", "longitude", "endlatitude", "endlongitude"]:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if {"latitude", "longitude"}.issubset(cleaned.columns):
        cleaned = cleaned.dropna(subset=["latitude", "longitude"])
        in_bengaluru_bbox = (
            cleaned["latitude"].between(12.7, 13.4)
            & cleaned["longitude"].between(77.2, 77.9)
        )
        cleaned = cleaned.loc[in_bengaluru_bbox].copy()

    if {"endlatitude", "endlongitude"}.issubset(cleaned.columns):
        invalid_endpoint = (
            cleaned["endlatitude"].isna()
            | cleaned["endlongitude"].isna()
            | (cleaned["endlatitude"] == 0)
            | (cleaned["endlongitude"] == 0)
            | ~cleaned["endlatitude"].between(12.7, 13.4)
            | ~cleaned["endlongitude"].between(77.2, 77.9)
        )
        cleaned.loc[invalid_endpoint, ["endlatitude", "endlongitude"]] = np.nan

    text_columns = [
        "event_type",
        "event_cause",
        "status",
        "authenticated",
        "description",
        "veh_type",
        "corridor",
        "priority",
        "police_station",
        "zone",
        "junction",
    ]
    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column]
                .astype("string")
                .str.strip()
                .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
            )

    if "requires_road_closure" in cleaned.columns:
        cleaned["requires_road_closure"] = cleaned["requires_road_closure"].fillna(False).astype(bool)

    cleaned = cleaned.drop_duplicates()
    return cleaned.reset_index(drop=True)


def build_data_quality_report(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> str:
    missing = cleaned_df.isna().mean().sort_values(ascending=False).mul(100)
    lines = [
        "FLEXUS Data Quality Report",
        "=" * 28,
        "",
        f"Raw shape: {raw_df.shape[0]:,} rows x {raw_df.shape[1]:,} columns",
        f"Cleaned shape: {cleaned_df.shape[0]:,} rows x {cleaned_df.shape[1]:,} columns",
        f"Duplicate rows removed: {len(raw_df) - len(raw_df.drop_duplicates()):,}",
        "",
        "Dataset conclusion:",
        "This is an urban incident/event log. It supports incident intelligence, hotspot analysis, event similarity, and incident-risk proxies. It does not support traffic speed, traffic-volume, route, or congestion simulation features.",
        "",
        "Columns:",
        ", ".join(cleaned_df.columns),
        "",
        "Missing values by column (%):",
    ]
    for column, pct in missing.items():
        lines.append(f"- {column}: {pct:.2f}%")

    if "start_datetime" in cleaned_df.columns:
        start = cleaned_df["start_datetime"]
        lines.extend(
            [
                "",
                f"Start datetime coverage: {start.min()} to {start.max()}",
                f"Parseable start datetimes: {start.notna().sum():,}",
            ]
        )

    if {"latitude", "longitude"}.issubset(cleaned_df.columns):
        lines.extend(
            [
                "",
                "Coordinate coverage:",
                f"- Latitude range: {cleaned_df['latitude'].min():.6f} to {cleaned_df['latitude'].max():.6f}",
                f"- Longitude range: {cleaned_df['longitude'].min():.6f} to {cleaned_df['longitude'].max():.6f}",
            ]
        )

    if "event_cause" in cleaned_df.columns:
        lines.extend(["", "Top event causes:"])
        for cause, count in cleaned_df["event_cause"].value_counts(dropna=False).head(10).items():
            lines.append(f"- {cause}: {count:,}")

    return "\n".join(lines)
