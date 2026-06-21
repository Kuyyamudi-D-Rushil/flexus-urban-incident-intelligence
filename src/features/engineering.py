import re

import numpy as np
import pandas as pd


PEAK_HOURS = {8, 9, 10, 17, 18, 19, 20}


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    start = pd.to_datetime(out["start_datetime"], errors="coerce", utc=True)
    out["hour"] = start.dt.hour
    out["day"] = start.dt.day
    out["weekday"] = start.dt.day_name()
    out["weekday_num"] = start.dt.weekday
    out["month"] = start.dt.month
    out["is_weekend"] = out["weekday_num"].isin([5, 6]).astype(int)
    out["is_peak_hour"] = out["hour"].isin(PEAK_HOURS).astype(int)
    return out


def add_event_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["closure_flag"] = out.get("requires_road_closure", False).astype(bool).astype(int)
    priority = out.get("priority", pd.Series("", index=out.index)).astype("string").str.lower()
    out["high_priority_flag"] = priority.eq("high").fillna(False).astype(int)
    out["description_clean"] = out.get("description", "").map(clean_text)

    if "closed_datetime" in out.columns:
        start = pd.to_datetime(out["start_datetime"], errors="coerce", utc=True)
        closed = pd.to_datetime(out["closed_datetime"], errors="coerce", utc=True)
        duration_hours = (closed - start).dt.total_seconds() / 3600
        out["closure_duration_hours"] = duration_hours.where(duration_hours.between(0, 24 * 30), np.nan)
    else:
        out["closure_duration_hours"] = np.nan

    for column in ["corridor", "police_station", "event_type", "event_cause", "priority", "veh_type", "status"]:
        if column in out.columns:
            out[column] = out[column].astype("string").fillna("Unknown")

    return out


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    return add_event_features(add_time_features(df))


def keyword_summary(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    words = {}
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "near",
        "road",
        "from",
        "this",
        "that",
        "are",
        "was",
        "sir",
        "please",
    }
    for text in df.get("description_clean", pd.Series(dtype=str)).dropna():
        for word in str(text).split():
            if len(word) >= 4 and word not in stopwords:
                words[word] = words.get(word, 0) + 1
    return pd.DataFrame(sorted(words.items(), key=lambda x: x[1], reverse=True)[:top_n], columns=["keyword", "count"])
