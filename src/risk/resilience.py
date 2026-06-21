import pandas as pd


def calculate_resilience_scores(df: pd.DataFrame, group_col: str = "corridor") -> pd.DataFrame:
    grouped = (
        df.groupby(group_col)
        .agg(
            incidents=("id", "count"),
            high_priority_rate=("high_priority_flag", "mean"),
            closure_rate=("closure_flag", "mean"),
            active_rate=("status", lambda s: s.astype("string").str.lower().eq("active").mean()),
            recurring_causes=("event_cause", "nunique"),
            median_resolution_hours=("closure_duration_hours", "median"),
        )
        .reset_index()
    )
    grouped["median_resolution_hours"] = grouped["median_resolution_hours"].fillna(grouped["median_resolution_hours"].median()).fillna(0)
    max_incidents = max(grouped["incidents"].max(), 1)
    max_recurring = max(grouped["recurring_causes"].max(), 1)
    max_duration = max(grouped["median_resolution_hours"].max(), 1)

    risk_pressure = (
        0.35 * (grouped["incidents"] / max_incidents)
        + 0.25 * grouped["high_priority_rate"]
        + 0.20 * grouped["closure_rate"]
        + 0.10 * grouped["active_rate"]
        + 0.05 * (grouped["recurring_causes"] / max_recurring)
        + 0.05 * (grouped["median_resolution_hours"] / max_duration)
    )
    grouped["resilience_score"] = ((1 - risk_pressure).clip(0, 1) * 100).round(2)
    grouped["risk_pressure"] = (risk_pressure * 100).round(2)
    return grouped.sort_values("resilience_score", ascending=True)
