import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DNA_CATEGORICAL = [
    "event_type",
    "event_cause",
    "corridor",
    "police_station",
    "priority",
    "veh_type",
]
DNA_NUMERIC = ["latitude", "longitude", "hour", "weekday_num", "closure_flag", "high_priority_flag"]


def build_dna_clusters(df: pd.DataFrame, n_clusters: int = 8):
    data = df.copy()
    for column in DNA_CATEGORICAL:
        if column not in data.columns:
            data[column] = "Unknown"
        data[column] = data[column].astype("string").fillna("Unknown")
    for column in DNA_NUMERIC:
        if column not in data.columns:
            data[column] = 0
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    if "description_clean" not in data.columns:
        data["description_clean"] = ""

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), DNA_CATEGORICAL),
            ("num", StandardScaler(), DNA_NUMERIC),
            ("text", TfidfVectorizer(max_features=80, min_df=3), "description_clean"),
        ]
    )
    model = Pipeline(
        steps=[
            ("features", preprocessor),
            ("cluster", KMeans(n_clusters=n_clusters, random_state=42, n_init=10)),
        ]
    )
    labels = model.fit_predict(data)
    out = data.copy()
    out["dna_cluster"] = labels
    return out, model


def summarize_clusters(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cluster_id, group in df.groupby("dna_cluster"):
        rows.append(
            {
                "dna_cluster": cluster_id,
                "events": len(group),
                "top_cause": group["event_cause"].mode().iat[0] if not group["event_cause"].mode().empty else "Unknown",
                "top_corridor": group["corridor"].mode().iat[0] if not group["corridor"].mode().empty else "Unknown",
                "top_station": group["police_station"].mode().iat[0] if not group["police_station"].mode().empty else "Unknown",
                "high_priority_rate": group["high_priority_flag"].mean(),
                "closure_rate": group["closure_flag"].mean(),
                "peak_hour_rate": group["is_peak_hour"].mean(),
                "common_hour": int(group["hour"].mode().iat[0]) if not group["hour"].dropna().mode().empty else -1,
            }
        )
    return pd.DataFrame(rows).sort_values("events", ascending=False)
