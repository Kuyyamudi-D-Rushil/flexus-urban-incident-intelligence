import pandas as pd


def generate_recommendations(df: pd.DataFrame, hotspot_summary: pd.DataFrame, resilience_df: pd.DataFrame) -> pd.DataFrame:
    recommendations = []

    for _, row in hotspot_summary.head(8).iterrows():
        recommendations.append(
            {
                "priority": "High" if row["risk_score"] >= 60 else "Medium",
                "area": row["top_corridor"],
                "trigger": f"Hotspot {int(row['hotspot_cluster'])} has {int(row['events'])} incidents and {row['closure_rate']:.1%} closure rate.",
                "recommendation": f"Increase monitoring near {row['top_corridor']} / {row['top_station']} for recurring {row['top_cause']} incidents.",
            }
        )

    potholes = df[df["event_cause"].astype("string").str.lower().str.contains("pot", na=False)]
    if not potholes.empty:
        for corridor, count in potholes["corridor"].value_counts().head(5).items():
            recommendations.append(
                {
                    "priority": "Medium",
                    "area": corridor,
                    "trigger": f"{count} pothole-related incidents recorded.",
                    "recommendation": "Schedule road-condition inspection and maintenance review for this corridor.",
                }
            )

    for _, row in resilience_df.head(5).iterrows():
        recommendations.append(
            {
                "priority": "High" if row["resilience_score"] < 45 else "Medium",
                "area": row.iloc[0],
                "trigger": f"Low resilience score: {row['resilience_score']:.1f}/100.",
                "recommendation": "Prioritize this area for patrol planning, recurring cause review, and incident response readiness.",
            }
        )

    closure_by_corridor = df.groupby("corridor")["closure_flag"].mean().sort_values(ascending=False).head(5)
    for corridor, rate in closure_by_corridor.items():
        if rate > df["closure_flag"].mean():
            recommendations.append(
                {
                    "priority": "Medium",
                    "area": corridor,
                    "trigger": f"Road closure rate is {rate:.1%}.",
                    "recommendation": "Monitor closure-prone incidents and prepare diversion communication playbooks.",
                }
            )

    return pd.DataFrame(recommendations).drop_duplicates().reset_index(drop=True)
