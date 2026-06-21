from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.utils.paths import RAW_DIR


ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
MODELS = ROOT / "models"

PRIMARY = "#00b8d9"
DANGER = "#ff4d4f"
WARNING = "#f5a623"
SUCCESS = "#34c759"
INK = "#102033"


st.set_page_config(page_title="FLEXUS Command Center", page_icon="F", layout="wide")


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4f7fb;
            --panel: #ffffff;
            --ink: #102033;
            --muted: #637083;
            --line: #dbe4ef;
            --primary: #00b8d9;
            --danger: #ff4d4f;
            --warning: #f5a623;
            --success: #34c759;
        }
        .stApp {
            background:
                radial-gradient(circle at 18% 0%, rgba(0, 184, 217, 0.16), transparent 28%),
                linear-gradient(180deg, #f7fbff 0%, #eef4f8 100%);
            color: var(--ink);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1b2a 0%, #102033 100%);
            color: white;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        [data-testid="stSidebar"] * { color: inherit; }
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stTextInput label,
        [data-testid="stSidebar"] .stRadio label {
            color: rgba(255,255,255,0.88) !important;
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 16px 14px;
            box-shadow: 0 10px 24px rgba(16, 32, 51, 0.07);
        }
        div[data-testid="stMetric"] label {
            color: var(--muted) !important;
            font-size: 0.82rem !important;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--ink);
            font-weight: 750;
        }
        .hero {
            background: linear-gradient(135deg, #102033 0%, #17324a 58%, #085c70 100%);
            color: #fff;
            padding: 28px 30px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 18px 44px rgba(16, 32, 51, 0.20);
            margin-bottom: 18px;
        }
        .hero-kicker {
            color: #8de8f7;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
            font-size: 0.78rem;
            margin-bottom: 8px;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 8px;
        }
        .hero-copy {
            color: rgba(255,255,255,0.82);
            max-width: 850px;
            font-size: 1rem;
        }
        .section-title {
            font-size: 1.08rem;
            font-weight: 760;
            color: var(--ink);
            margin: 18px 0 8px;
        }
        .insight-card, .rec-card, .cluster-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--primary);
            border-radius: 8px;
            padding: 15px 16px;
            box-shadow: 0 10px 22px rgba(16, 32, 51, 0.06);
            min-height: 118px;
        }
        .rec-card.high { border-left-color: var(--danger); }
        .rec-card.medium { border-left-color: var(--warning); }
        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 0.72rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 8px;
        }
        .badge.high { background: rgba(255,77,79,0.14); color: #a82020; }
        .badge.medium { background: rgba(245,166,35,0.16); color: #8a5a00; }
        .badge.good { background: rgba(52,199,89,0.15); color: #126b2d; }
        .muted { color: var(--muted); }
        .small { font-size: 0.84rem; }
        .divider { height: 1px; background: var(--line); margin: 16px 0; }
        h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 8px 14px;
        }
        .stTabs [aria-selected="true"] {
            border-color: var(--primary);
            color: var(--ink);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    path = PROCESSED / "dna_dataset.csv"
    if not path.exists():
        path = PROCESSED / "engineered_dataset.csv"
    if not path.exists():
        raw_files = sorted(RAW_DIR.glob("*.csv"))
        if raw_files:
            with st.spinner("Preparing FLEXUS data artifacts for this deployment..."):
                from run_pipeline import main as run_pipeline_main

                run_pipeline_main()
            path = PROCESSED / "dna_dataset.csv"
        else:
            st.error("Dataset artifacts are missing from this deployment.")
            st.info(
                "Streamlit Cloud does not have `data/processed/dna_dataset.csv` or a raw CSV in `data/raw/`. "
                "Push either the processed artifacts, or the raw dataset CSV so the app can generate artifacts on startup."
            )
            st.stop()
    if not path.exists():
        st.error("FLEXUS data preparation did not create the expected processed dataset.")
        st.stop()
    df = pd.read_csv(path)
    if "start_datetime" in df.columns:
        df["start_datetime"] = pd.to_datetime(df["start_datetime"], errors="coerce")
    for column in ["hour", "month", "closure_flag", "high_priority_flag", "is_peak_hour", "is_weekend"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    for column in ["event_cause", "corridor", "priority", "police_station", "event_type", "veh_type", "weekday"]:
        if column in df.columns:
            df[column] = df[column].fillna("Unknown").astype(str)
    return df


@st.cache_data
def load_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


@st.cache_resource
def load_model():
    model_path = MODELS / "trained_model.pkl"
    return joblib.load(model_path) if model_path.exists() else None


def top_value(series, fallback="Unknown"):
    mode = series.dropna().mode()
    return mode.iat[0] if not mode.empty else fallback


def pct(value):
    return f"{value:.1%}" if pd.notna(value) else "N/A"


def filter_options(df, column, limit=40):
    values = df[column].dropna().astype(str).value_counts().head(limit).index.tolist()
    return sorted(values)


def sidebar_filters(df):
    st.sidebar.markdown("### FLEXUS")
    st.sidebar.caption("Smart City Incident Command")

    search = st.sidebar.text_input("Search incidents", placeholder="Cause, corridor, station, description")
    causes = st.sidebar.multiselect("Event cause", filter_options(df, "event_cause"))
    corridors = st.sidebar.multiselect("Corridor", filter_options(df, "corridor"))
    priorities = st.sidebar.multiselect("Priority", filter_options(df, "priority"))
    event_types = st.sidebar.multiselect("Event type", filter_options(df, "event_type"))

    filtered = df.copy()
    if search:
        haystack = (
            filtered["event_cause"].astype(str)
            + " "
            + filtered["corridor"].astype(str)
            + " "
            + filtered["police_station"].astype(str)
            + " "
            + filtered.get("description_clean", pd.Series("", index=filtered.index)).astype(str)
        ).str.lower()
        filtered = filtered[haystack.str.contains(search.lower(), na=False)]
    if causes:
        filtered = filtered[filtered["event_cause"].isin(causes)]
    if corridors:
        filtered = filtered[filtered["corridor"].isin(corridors)]
    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]
    if event_types:
        filtered = filtered[filtered["event_type"].isin(event_types)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} incidents")
    return filtered


def page_nav():
    return st.sidebar.radio(
        "Command views",
        [
            "Command Center",
            "Dataset Explorer",
            "Event DNA",
            "Hotspot Intelligence",
            "Risk Predictor",
            "Resilience Scores",
            "Recommendations",
        ],
    )


def require_data(df):
    if df.empty:
        st.warning("No incidents match the current filters. Clear one or more sidebar filters to continue.")
        return False
    return True


def hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-kicker">Urban Incident Intelligence Platform</div>
          <div class="hero-title">FLEXUS Command Center</div>
          <div class="hero-copy">
            A local decision-support dashboard for detecting incident hotspots, understanding recurring event DNA,
            forecasting incident-risk proxies, ranking resilience, and converting raw event logs into operational action.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(df, hotspot_count=None):
    if df.empty:
        st.info("No records available for the current filter selection.")
        return
    risk_pressure = (0.45 * df["high_priority_flag"].mean()) + (0.35 * df["closure_flag"].mean()) + (0.20 * df["is_peak_hour"].mean())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Incidents", f"{len(df):,}")
    c2.metric("High Priority", f"{int(df['high_priority_flag'].sum()):,}", pct(df["high_priority_flag"].mean()))
    c3.metric("Road Closures", f"{int(df['closure_flag'].sum()):,}", pct(df["closure_flag"].mean()))
    c4.metric("Hotspots", f"{hotspot_count if hotspot_count is not None else 'N/A'}")
    c5.metric("Risk Level", "High" if risk_pressure >= 0.45 else "Moderate" if risk_pressure >= 0.25 else "Low", f"{risk_pressure * 100:.1f}/100")


def section(title, caption=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def insight_cards(df, hotspots):
    if df.empty:
        return
    top_cause = top_value(df["event_cause"])
    top_corridor = top_value(df["corridor"])
    peak_hour = int(df["hour"].mode().iat[0]) if not df["hour"].dropna().mode().empty else 0
    high_closure = hotspots.sort_values("closure_rate", ascending=False).head(1) if not hotspots.empty else pd.DataFrame()
    cols = st.columns(4)
    cards = [
        ("Dominant Cause", top_cause, f"{df['event_cause'].value_counts().iloc[0]:,} incidents appear in the leading category."),
        ("Most Active Corridor", top_corridor, "Highest observed incident burden in the current filter selection."),
        ("Peak Signal", f"{peak_hour:02d}:00", "Most common incident start hour in the filtered data."),
        ("Closure Watch", high_closure["top_corridor"].iat[0] if not high_closure.empty else "N/A", f"{pct(high_closure['closure_rate'].iat[0]) if not high_closure.empty else 'N/A'} closure rate in the top closure hotspot."),
    ]
    for col, (label, value, copy) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="badge good">{label}</div>
                    <h3 style="margin:0 0 6px 0;">{value}</h3>
                    <div class="muted small">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def command_center(df):
    hotspots = load_csv(OUTPUTS / "hotspot_rankings.csv")
    hero()
    metric_row(df, len(hotspots) if not hotspots.empty else None)
    if not require_data(df):
        return

    section("Top 5 Findings", "Auto-generated operational observations from the current filtered incident view.")
    insight_cards(df, hotspots)

    section("Operations Snapshot")
    left, right = st.columns([1.2, 1])
    with left:
        cause_counts = df["event_cause"].value_counts().head(12).reset_index()
        cause_counts.columns = ["event_cause", "incidents"]
        fig = px.bar(
            cause_counts,
            x="incidents",
            y="event_cause",
            orientation="h",
            color="incidents",
            color_continuous_scale="teal",
            title="Leading Incident Causes",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        risk_mix = pd.DataFrame(
            {
                "signal": ["High priority", "Road closure", "Peak hour", "Weekend"],
                "rate": [
                    df["high_priority_flag"].mean(),
                    df["closure_flag"].mean(),
                    df["is_peak_hour"].mean(),
                    df["is_weekend"].mean(),
                ],
            }
        )
        fig = go.Figure(
            data=[
                go.Scatterpolar(
                    r=risk_mix["rate"],
                    theta=risk_mix["signal"],
                    fill="toself",
                    line_color=PRIMARY,
                    name="Risk mix",
                )
            ]
        )
        fig.update_layout(title="Incident Risk Signal Radar", polar=dict(radialaxis=dict(range=[0, 1])), height=430, margin=dict(l=20, r=20, t=55, b=20))
        st.plotly_chart(fig, use_container_width=True)

    section("Geographic Command Map", "Heatmap plus clustered event markers generated from incident coordinates.")
    map_path = OUTPUTS / "maps" / "phase1_map.html"
    if map_path.exists():
        components.html(map_path.read_text(encoding="utf-8"), height=610)
    else:
        st.warning("Map artifact not found. Run `python run_pipeline.py`.")

    section("Quick Navigation")
    c1, c2, c3 = st.columns(3)
    c1.info("Use Hotspot Intelligence to brief judges on recurring incident zones.")
    c2.info("Use Event DNA to show the unique innovation layer.")
    c3.info("Use Recommendations to close with operational impact.")


def dataset_explorer(df):
    st.title("Dataset Explorer")
    st.caption("Transparency layer for validating the incident-log foundation behind FLEXUS.")
    metric_row(df)
    if not require_data(df):
        return

    tab1, tab2, tab3 = st.tabs(["Records", "Quality", "Timeline"])
    with tab1:
        st.dataframe(df, use_container_width=True, height=430)
        st.download_button("Download filtered dataset", df.to_csv(index=False), "flexus_filtered_dataset.csv", use_container_width=True)
    with tab2:
        missing = df.isna().mean().mul(100).reset_index()
        missing.columns = ["column", "missing_pct"]
        fig = px.bar(
            missing.sort_values("missing_pct", ascending=False).head(25),
            x="missing_pct",
            y="column",
            orientation="h",
            title="Top Missing-Value Fields",
            color="missing_pct",
            color_continuous_scale="orrd",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=520)
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        timeline = df.dropna(subset=["start_datetime"]).copy()
        timeline["date"] = timeline["start_datetime"].dt.date
        daily = timeline.groupby("date").size().reset_index(name="incidents")
        fig = px.area(daily, x="date", y="incidents", title="Incident Timeline", markers=True)
        fig.update_traces(line_color=PRIMARY)
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)


def event_dna(df):
    st.title("Event DNA")
    st.caption("Incident fingerprints built from cause, type, location, time, priority, closure signal, vehicle type, and text.")
    if not require_data(df):
        return
    summary = load_csv(OUTPUTS / "dna_cluster_summary.csv")
    if summary.empty:
        st.warning("DNA cluster summary not found. Run the pipeline first.")
        return

    top_clusters = summary.sort_values("events", ascending=False).head(4)
    cols = st.columns(4)
    for col, row in zip(cols, top_clusters.to_dict("records")):
        with col:
            st.markdown(
                f"""
                <div class="cluster-card">
                    <div class="badge good">Cluster {int(row['dna_cluster'])}</div>
                    <h3 style="margin:0;">{int(row['events']):,} events</h3>
                    <div class="muted small">Cause: {row['top_cause']}</div>
                    <div class="muted small">Corridor: {row['top_corridor']}</div>
                    <div class="muted small">Closure rate: {pct(row['closure_rate'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.1, 1])
    with left:
        fig = px.treemap(summary, path=["top_cause", "top_corridor", "dna_cluster"], values="events", color="closure_rate", color_continuous_scale="teal", title="DNA Cluster Composition")
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.scatter(
            summary,
            x="high_priority_rate",
            y="closure_rate",
            size="events",
            color="top_cause",
            hover_data=["dna_cluster", "top_corridor", "top_station"],
            title="Cluster Risk Profile",
        )
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)

    cluster_ids = sorted(df["dna_cluster"].dropna().unique()) if "dna_cluster" in df else []
    cluster = st.selectbox("Inspect DNA cluster", cluster_ids)
    selected = df[df["dna_cluster"] == cluster] if cluster_ids else df.head(0)
    st.dataframe(selected.head(120), use_container_width=True, height=360)


def hotspot_page(df):
    st.title("Hotspot Intelligence")
    st.caption("Risk-ranked recurring incident zones. Rankings use full-dataset artifacts for stable command-center reporting.")
    hotspots = load_csv(OUTPUTS / "hotspot_rankings.csv")
    if hotspots.empty:
        st.warning("Hotspot rankings are not available. Run the pipeline first.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Detected Hotspots", f"{len(hotspots):,}")
    c2.metric("Highest Hotspot Risk", f"{hotspots['risk_score'].max():.1f}")
    c3.metric("Max Closure Rate", pct(hotspots["closure_rate"].max()))

    left, right = st.columns([1.15, 1])
    with left:
        fig = px.scatter_mapbox(
            hotspots,
            lat="latitude",
            lon="longitude",
            size="events",
            color="risk_score",
            hover_name="top_corridor",
            hover_data=["top_cause", "top_station", "closure_rate", "events"],
            zoom=10,
            height=640,
            mapbox_style="open-street-map",
            title="Interactive Hotspot Command Map",
            color_continuous_scale="Turbo",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(
            hotspots.head(12),
            x="risk_score",
            y="top_corridor",
            color="top_cause",
            orientation="h",
            title="Top Hotspot Rankings",
            hover_data=["top_station", "events", "closure_rate"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(hotspots.head(15), use_container_width=True, height=250)


def gauge(title, value, suffix="%", color=PRIMARY):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": suffix},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 35], "color": "#e8f5ee"},
                    {"range": [35, 70], "color": "#fff3d8"},
                    {"range": [70, 100], "color": "#ffe3e3"},
                ],
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=15, r=15, t=40, b=10))
    return fig


def predictor_page(df):
    st.title("Incident Risk Predictor")
    st.caption("Predicts incident-risk proxy outcomes from event-log features. It does not predict traffic speed, flow, or congestion propagation.")
    if not require_data(df):
        return
    bundle = load_model()
    if bundle is None:
        st.warning("Risk model not found. Run `python run_pipeline.py` first.")
        return

    report = bundle["report"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Model Target", bundle["target"].replace("_", " ").title())
    c2.metric("Accuracy", f"{report['accuracy']:.2f}")
    c3.metric("CV F1", f"{report['cv_f1_mean']:.2f}")

    left, right = st.columns([1, 1])
    with left:
        with st.form("risk_form"):
            event_type = st.selectbox("Event type", sorted(df["event_type"].dropna().unique()))
            event_cause = st.selectbox("Event cause", sorted(df["event_cause"].dropna().unique()))
            corridor = st.selectbox("Corridor", sorted(df["corridor"].dropna().unique()))
            police_station = st.selectbox("Police station", sorted(df["police_station"].dropna().unique()))
            veh_type = st.selectbox("Vehicle type", sorted(df["veh_type"].dropna().unique()))
            weekday = st.selectbox("Weekday", sorted(df["weekday"].dropna().unique()))
            hour = st.slider("Hour", 0, 23, 9)
            latitude = st.number_input("Latitude", value=float(df["latitude"].median()))
            longitude = st.number_input("Longitude", value=float(df["longitude"].median()))
            description = st.text_input("Description", "vehicle breakdown near junction")
            submitted = st.form_submit_button("Predict incident risk", use_container_width=True)

    with right:
        if submitted:
            row = pd.DataFrame(
                [
                    {
                        "event_type": event_type,
                        "event_cause": event_cause,
                        "corridor": corridor,
                        "police_station": police_station,
                        "veh_type": veh_type,
                        "weekday": weekday,
                        "latitude": latitude,
                        "longitude": longitude,
                        "hour": hour,
                        "month": int(df["month"].dropna().mode().iat[0]) if "month" in df and not df["month"].dropna().empty else 1,
                        "is_peak_hour": int(hour in {8, 9, 10, 17, 18, 19, 20}),
                        "is_weekend": int(weekday in {"Saturday", "Sunday"}),
                        "description_clean": description.lower(),
                    }
                ]
            )
            prob = float(bundle["pipeline"].predict_proba(row)[0, 1])
            level = "High" if prob >= 0.7 else "Moderate" if prob >= 0.35 else "Low"
            color = DANGER if level == "High" else WARNING if level == "Moderate" else SUCCESS
            st.plotly_chart(gauge("Predicted Risk", prob * 100, color=color), use_container_width=True)
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="badge {'high' if level == 'High' else 'medium' if level == 'Moderate' else 'good'}">{level} risk</div>
                    <h3 style="margin:0 0 8px 0;">{prob:.1%} probability</h3>
                    <div class="muted small">Contributing context: {event_cause}, {corridor}, {weekday} at {hour:02d}:00, vehicle type {veh_type}.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            baseline = df["high_priority_flag"].mean() * 100 if bundle["target"] == "high_priority_flag" else df["closure_flag"].mean() * 100
            st.plotly_chart(gauge("Historical Baseline", baseline, color=PRIMARY), use_container_width=True)
            st.info("Fill the incident context form and submit to generate a risk probability with a visual gauge.")


def resilience_page(df):
    st.title("Resilience Scores")
    st.caption("Executive corridor and police-station resilience rankings calculated from full-dataset incident pressure.")
    corridor = load_csv(OUTPUTS / "corridor_resilience_scores.csv")
    station = load_csv(OUTPUTS / "station_resilience_scores.csv")
    if corridor.empty or station.empty:
        st.warning("Resilience score artifacts are missing. Run the pipeline first.")
        return

    weakest = corridor.head(1).iloc[0]
    strongest = corridor.sort_values("resilience_score", ascending=False).head(1).iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Weakest Corridor", weakest["corridor"], f"{weakest['resilience_score']:.1f}/100")
    c2.metric("Strongest Corridor", strongest["corridor"], f"{strongest['resilience_score']:.1f}/100")
    c3.metric("Median Resilience", f"{corridor['resilience_score'].median():.1f}/100")

    tab1, tab2 = st.tabs(["Corridor Command", "Police Station Command"])
    with tab1:
        left, right = st.columns([1.1, 1])
        with left:
            fig = px.bar(corridor.head(18), x="resilience_score", y="corridor", color="risk_pressure", orientation="h", title="Lowest Corridor Resilience Scores", color_continuous_scale="Reds")
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=560)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.dataframe(corridor, use_container_width=True, height=560)
    with tab2:
        fig = px.bar(station.head(22), x="resilience_score", y="police_station", color="risk_pressure", orientation="h", title="Police Station Resilience Rankings", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(station, use_container_width=True, height=300)


def recommendations_page():
    st.title("Recommendations")
    st.caption("Actionable, rule-based operating suggestions derived from observed incident patterns. No fake optimization.")
    recs = load_csv(OUTPUTS / "recommendations.csv")
    if recs.empty:
        st.warning("Recommendations are not available. Run the pipeline first.")
        return

    high = int(recs["priority"].astype(str).str.lower().eq("high").sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Recommendations", f"{len(recs):,}")
    c2.metric("High Priority Actions", f"{high:,}")
    c3.metric("Coverage Areas", f"{recs['area'].nunique():,}")

    section("Action Panels")
    for row in recs.head(12).to_dict("records"):
        priority = str(row["priority"]).lower()
        impact = "Reduce repeated operational blind spots and improve targeted monitoring readiness."
        st.markdown(
            f"""
            <div class="rec-card {'high' if priority == 'high' else 'medium'}">
                <div class="badge {'high' if priority == 'high' else 'medium'}">{row['priority']} priority</div>
                <h3 style="margin:0 0 6px 0;">{row['area']}</h3>
                <div class="small"><b>Reason:</b> {row['trigger']}</div>
                <div class="small"><b>Suggested action:</b> {row['recommendation']}</div>
                <div class="small muted"><b>Expected impact:</b> {impact}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

    with st.expander("Full recommendation table"):
        st.dataframe(recs, use_container_width=True, height=420)
    st.download_button("Download recommendations", recs.to_csv(index=False), "flexus_recommendations.csv", use_container_width=True)


inject_css()
df = load_data()
filtered_df = sidebar_filters(df)
page = page_nav()

if page == "Command Center":
    command_center(filtered_df)
elif page == "Dataset Explorer":
    dataset_explorer(filtered_df)
elif page == "Event DNA":
    event_dna(filtered_df)
elif page == "Hotspot Intelligence":
    hotspot_page(filtered_df)
elif page == "Risk Predictor":
    predictor_page(filtered_df)
elif page == "Resilience Scores":
    resilience_page(filtered_df)
else:
    recommendations_page()
