import json

import joblib
import plotly.express as px

from src.data.cleaner import build_data_quality_report, clean_events
from src.data.loader import load_raw_events
from src.dna.engine import build_dna_clusters, summarize_clusters
from src.features.engineering import engineer_features, keyword_summary
from src.hotspots.engine import create_incident_map, detect_hotspots, summarize_hotspots
from src.models.risk_model import train_risk_model
from src.recommendations.engine import generate_recommendations
from src.reports.generator import dataframe_snapshot, write_pdf_report, write_text_report
from src.risk.resilience import calculate_resilience_scores
from src.utils.paths import MODELS_DIR, OUTPUTS_DIR, PROCESSED_DIR, REPORTS_DIR, ensure_project_dirs, find_raw_dataset


def save_plot(fig, filename: str) -> None:
    fig.write_html(str(OUTPUTS_DIR / "figures" / filename))


def main() -> None:
    ensure_project_dirs()

    raw_path = find_raw_dataset()
    raw_df = load_raw_events(raw_path)
    cleaned_df = clean_events(raw_df)
    engineered_df = engineer_features(cleaned_df)

    cleaned_path = PROCESSED_DIR / "cleaned_dataset.csv"
    engineered_path = PROCESSED_DIR / "engineered_dataset.csv"
    cleaned_df.to_csv(cleaned_path, index=False)
    engineered_df.to_csv(engineered_path, index=False)

    quality_report = build_data_quality_report(raw_df, cleaned_df)
    (REPORTS_DIR / "data_quality_report.txt").write_text(quality_report, encoding="utf-8")
    create_incident_map(engineered_df, OUTPUTS_DIR / "maps" / "phase1_map.html")

    dna_df, dna_model = build_dna_clusters(engineered_df)
    dna_summary = summarize_clusters(dna_df)
    dna_df.to_csv(PROCESSED_DIR / "dna_dataset.csv", index=False)
    dna_summary.to_csv(OUTPUTS_DIR / "dna_cluster_summary.csv", index=False)
    joblib.dump(dna_model, MODELS_DIR / "event_dna_clusterer.pkl")

    hotspot_df = detect_hotspots(dna_df)
    hotspot_summary = summarize_hotspots(hotspot_df)
    hotspot_df.to_csv(PROCESSED_DIR / "hotspot_dataset.csv", index=False)
    hotspot_summary.to_csv(OUTPUTS_DIR / "hotspot_rankings.csv", index=False)

    model_report = train_risk_model(dna_df, MODELS_DIR / "trained_model.pkl")
    (REPORTS_DIR / "risk_prediction_report.json").write_text(json.dumps(model_report, indent=2), encoding="utf-8")

    corridor_resilience = calculate_resilience_scores(dna_df, "corridor")
    station_resilience = calculate_resilience_scores(dna_df, "police_station")
    corridor_resilience.to_csv(OUTPUTS_DIR / "corridor_resilience_scores.csv", index=False)
    station_resilience.to_csv(OUTPUTS_DIR / "station_resilience_scores.csv", index=False)

    recommendations = generate_recommendations(dna_df, hotspot_summary, corridor_resilience)
    recommendations.to_csv(OUTPUTS_DIR / "recommendations.csv", index=False)
    keyword_summary(dna_df).to_csv(OUTPUTS_DIR / "description_keywords.csv", index=False)

    save_plot(px.histogram(dna_df, x="event_cause", title="Incident Cause Distribution"), "event_cause_distribution.html")
    save_plot(px.bar(hotspot_summary.head(15), x="top_corridor", y="risk_score", color="top_cause", title="Top Hotspots by Risk Score"), "hotspot_risk.html")
    save_plot(px.bar(corridor_resilience.head(15), x="corridor", y="resilience_score", title="Lowest Corridor Resilience Scores"), "resilience_scores.html")
    save_plot(px.bar(dna_summary, x="dna_cluster", y="events", color="top_cause", title="Event DNA Cluster Sizes"), "dna_clusters.html")

    reports = {
        "executive_summary": {
            "Dataset": f"{len(dna_df):,} usable incident records from {raw_path.name}.",
            "What FLEXUS Does": "FLEXUS analyzes urban incident patterns, identifies hotspots, clusters similar event DNA, estimates incident risk, scores corridor resilience, and generates rule-based operational recommendations.",
            "What FLEXUS Does Not Do": "It does not predict traffic speed, volume, density, routes, or congestion propagation because those columns are not present in the dataset.",
            "Top Causes": dna_df["event_cause"].value_counts().head(10).to_string(),
        },
        "hotspot_report": {
            "Summary": "Hotspots are detected from repeated incident coordinates using DBSCAN clustering.",
            "Top Hotspots": dataframe_snapshot(hotspot_summary),
        },
        "dna_analysis_report": {
            "Summary": "Event DNA combines event cause, type, location, time, priority, road closure flag, vehicle type, and description text.",
            "Cluster Summary": dataframe_snapshot(dna_summary),
        },
        "recommendation_report": {
            "Summary": "Recommendations are rule-based and derived from observed hotspots, recurring causes, closure rates, and resilience scores.",
            "Recommendations": dataframe_snapshot(recommendations, 20),
        },
    }

    for name, sections in reports.items():
        title = name.replace("_", " ").title()
        write_text_report(REPORTS_DIR / f"{name}.txt", title, sections)
        write_pdf_report(REPORTS_DIR / f"{name}.pdf", title, sections)

    print("FLEXUS pipeline complete.")
    print(f"Cleaned dataset: {cleaned_path}")
    print(f"Engineered dataset: {engineered_path}")
    print(f"Risk model: {MODELS_DIR / 'trained_model.pkl'}")
    print("Dashboard: streamlit run app.py")


if __name__ == "__main__":
    main()
