# FLEXUS Final Audit Report

Audit roles: Senior QA Engineer, Product Reviewer, Hackathon Judge, UI/UX Reviewer, Reliability Engineer.

Audit date: 2026-06-17

## Executive Verdict

FLEXUS is demo-ready as a local hackathon prototype.

The project correctly stays within the dataset reality: it presents urban incident intelligence, not traffic simulation or congestion forecasting. The pipeline generates usable processed datasets, model artifacts, maps, reports, rankings, resilience scores, and recommendations. The Streamlit dashboard loads and all primary pages render without runtime exceptions.

## Verified Functional Checklist

### Data Layer

- PASS: Raw dataset loads from `data/raw/*.csv`.
- PASS: Dataset is cleaned into `data/processed/cleaned_dataset.csv`.
- PASS: Engineered dataset is generated at `data/processed/engineered_dataset.csv`.
- PASS: Missing values are handled for key modeling/dashboard fields.
- PASS: Invalid endpoint coordinates are removed from endpoint fields.
- PASS: Core start coordinates are preserved for mapping.
- PASS: Data quality report exists at `reports/data_quality_report.txt`.

### Feature Engineering

- PASS: Time features exist: hour, day, weekday, month, weekend, peak-hour indicator.
- PASS: Event features exist: closure flag, high-priority flag, cleaned description text.
- PASS: Location/category fields are normalized for corridor, police station, event type, event cause, vehicle type, status.
- PASS: Text keyword summary generated at `outputs/description_keywords.csv`.

### Event DNA Engine

- PASS: Event DNA clustering runs.
- PASS: DNA cluster IDs are written to `data/processed/dna_dataset.csv`.
- PASS: Cluster summaries exist at `outputs/dna_cluster_summary.csv`.
- PASS: DNA model artifact exists at `models/event_dna_clusterer.pkl`.

### Hotspot Intelligence

- PASS: Hotspot clustering runs using incident coordinates.
- PASS: Hotspot dataset exists at `data/processed/hotspot_dataset.csv`.
- PASS: Ranked hotspots exist at `outputs/hotspot_rankings.csv`.
- PASS: Incident map exists at `outputs/maps/phase1_map.html`.

### Incident Risk Forecasting

- PASS: Risk model trains and is persisted at `models/trained_model.pkl`.
- PASS: Model report exists at `reports/risk_prediction_report.json`.
- PASS: Dashboard predictor loads the model artifact.
- PASS: Target is an incident-risk proxy, not traffic congestion.

### Resilience Score

- PASS: Corridor resilience scores exist at `outputs/corridor_resilience_scores.csv`.
- PASS: Police-station resilience scores exist at `outputs/station_resilience_scores.csv`.
- PASS: Scoring is formula-based and explainable.

### Recommendations

- PASS: Rule-based recommendations exist at `outputs/recommendations.csv`.
- PASS: Recommendations are grounded in hotspot, closure, recurring cause, and resilience outputs.
- PASS: No fake optimization or route/resource simulation is introduced.

### Dashboard

- PASS: Streamlit app responds at `http://localhost:8501`.
- PASS: Browser reload shows no Streamlit exception blocks.
- PASS: Browser console has no captured errors or warnings.
- PASS: Main pages render:
  - Executive Overview
  - Dataset Explorer
  - Event DNA Explorer
  - Hotspot Intelligence
  - Incident Risk Predictor
  - Resilience Score Dashboard
  - Recommendations Center
- PASS: Download buttons exist for filtered data and recommendations.
- PASS: Scope disclaimer is visible on the Executive Overview page.

### Reports And Packaging

- PASS: README exists with setup, run commands, architecture, data flow, validation steps, and assumptions.
- PASS: Demo script exists at `reports/demo_script.md`.
- PASS: Judge walkthrough exists at `reports/judge_walkthrough.md`.
- PASS: PDF/text reports exist for executive summary, hotspot, DNA, and recommendations.

## Issues Found And Fixed During Audit

### Fixed: Empty Filter Demo Crash Risk

Severity: High

Problem:
If a judge selected sidebar filters that produced zero matching incidents, metrics could show bad values and the predictor page could fail because select boxes had no options.

Fix:
Added `require_data()` and empty-state handling in `app.py`.

Result:
The dashboard now shows a clear warning when filters produce no data.

### Fixed: Test Collection Reliability

Severity: Medium

Problem:
Pytest began collecting temporary cache folders created by a previous sandboxed run, causing a permission error before reaching the actual test.

Fix:
Added `pytest.ini` with `testpaths = tests`.

Result:
The project test now runs and passes.

## Remaining Risks

### Risk: Browser Performance On Map/Charts

Severity: Medium

The dashboard loads several large HTML/Plotly/Folium assets. It works locally, but on a low-spec laptop the Executive Overview map and large dataframes may feel slow.

Recommended demo handling:
Open the app before judging starts and avoid rapid page switching during the first load.

### Risk: Streamlit Dependency Conflict In Existing Python Environments

Severity: Medium

This machine had an older `starlette` package that initially prevented Streamlit from starting. Upgrading `starlette` fixed it locally, but a fresh environment should install from `requirements.txt` before running.

Recommended demo handling:
Run setup and app launch before the demo. If Streamlit fails, run:

```powershell
python -m pip install --upgrade streamlit starlette
```

### Risk: Model Interpretability Is Limited

Severity: Low

The risk model is useful for the demo, but the dashboard currently shows core metrics, not feature importance. The report JSON contains evaluation metrics, but feature importance is not surfaced visually.

Recommendation:
For judging, explain the model as a practical incident-risk proxy, not as a deep predictive system.

### Risk: Hotspot And Recommendation Pages Use Full-Dataset Artifacts

Severity: Low

Sidebar filters affect most visible event data, but hotspot, resilience, and recommendation rankings are generated from full-dataset artifacts for stability. This is now disclosed with page captions.

Recommendation:
Frame these as official overall rankings, not per-filter recalculations.

### Risk: Dataset Limitation Must Be Repeated Verbally

Severity: Low

Judges may ask why there is no route optimization or traffic prediction. The product correctly avoids those claims, but the presenter must emphasize the dataset-first choice.

Recommendation:
Use the phrase: "FLEXUS predicts incident risk proxies, not traffic speed or congestion flow."

## UI/UX Review

Strengths:

- Clear page structure.
- Sidebar navigation is simple.
- Executive Overview gives immediate project framing.
- Data explorer is useful for transparency.
- The app includes a visible scope disclaimer.
- Recommendation Center is judge-friendly because it translates analytics into actions.

Weaknesses:

- Some visualizations use long category labels, especially corridors and event causes.
- Dataframe-heavy pages can feel dense.
- Executive Overview has two visible `FLEXUS` headings because the sidebar title and page title appear together.
- No custom styling; acceptable for hackathon speed, but not highly branded.

Recommended demo behavior:

- Start with Executive Overview.
- Move quickly to Hotspot Intelligence and Recommendations Center.
- Use Dataset Explorer only to prove data transparency.
- Avoid spending too long on raw tables.

## Reliability Review

Verified commands:

```powershell
python run_pipeline.py
python -m compileall app.py src
python -m pytest
```

Results:

- Pipeline completed successfully before audit.
- Compile check passed after audit fixes.
- Tests passed: 1 passed.
- App returned HTTP 200 at `http://localhost:8501`.
- Browser reload found no Streamlit exception blocks.
- Browser console logs had no captured errors.

Known non-blocking warning:

- Pytest may emit a cache warning on this Windows sandboxed filesystem, but the test still passes.

## Judge Experience Assessment

Best judging path:

1. Executive Overview
2. Hotspot Intelligence
3. Event DNA Explorer
4. Incident Risk Predictor
5. Resilience Score Dashboard
6. Recommendations Center
7. Reports/demo script if asked

Strongest story:

FLEXUS is valuable because it refuses to fake unavailable traffic data. It turns the actual incident dataset into a working decision-support tool for hotspot detection, incident pattern discovery, operational prioritization, and risk-aware monitoring.

## Final Status

Status: PASS WITH MINOR RISKS

FLEXUS is ready for a hackathon demo as a local incident-intelligence prototype. Do not add major features before presentation. Focus on rehearsing the demo path and clearly explaining the dataset-first scope.
