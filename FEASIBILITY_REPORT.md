# FLEXUS Dataset Feasibility Report

Generated after Phase 1 dataset inspection.

## Dataset Reality

Raw dataset inspected:

- `data/raw/Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv`
- Shape: 8,173 rows x 46 columns
- Coverage window:
  - `start_datetime`: 2023-11-09 to 2024-04-08, 8,057 parseable rows
  - `created_date`: 2023-09-29 to 2024-04-08, 8,171 parseable rows
  - `modified_datetime`: 2023-11-09 to 2024-04-20, 8,173 parseable rows
- Dataset type: event incident log, not traffic sensor data

Available columns:

`id`, `event_type`, `latitude`, `longitude`, `endlatitude`, `endlongitude`, `address`, `end_address`, `event_cause`, `requires_road_closure`, `start_datetime`, `end_datetime`, `status`, `authenticated`, `modified_datetime`, `map_file`, `direction`, `description`, `veh_type`, `veh_no`, `corridor`, `priority`, `cargo_material`, `reason_breakdown`, `age_of_truck`, `created_date`, `route_path`, `client_id`, `created_by_id`, `last_modified_by_id`, `assigned_to_police_id`, `citizen_accident_id`, `comment`, `police_station`, `meta_data`, `kgid`, `resolved_at_address`, `resolved_at_latitude`, `resolved_at_longitude`, `closed_by_id`, `closed_datetime`, `resolved_by_id`, `resolved_datetime`, `gba_identifier`, `zone`, `junction`

## Dataset Strengths

- Strong incident-event coverage with 8,173 records.
- Complete core event fields: `id`, `event_type`, `event_cause`, `requires_road_closure`, `status`, `modified_datetime`, `police_station`.
- Complete start coordinates: `latitude` and `longitude` are present for every row.
- Useful categorical dimensions: `corridor`, `police_station`, `event_cause`, `event_type`, `priority`, `status`, `requires_road_closure`.
- Good enough for heatmaps, hotspot ranking, event-type breakdowns, corridor risk summaries, and simple historical frequency forecasting.
- `description` is present for 83.36% of records, enabling lightweight text-based similarity or clustering.

## Dataset Weaknesses

- No traffic speed, travel time, density, queue length, signal timing, road capacity, lane count, weather, or live sensor feed.
- No road-network topology, adjacency graph, or reliable route paths. `route_path` is 98.32% missing.
- `end_datetime` is 94.00% missing and contains unreliable values, including future dates and negative durations.
- `closed_datetime` is 61.57% missing; usable only for a subset.
- `zone` is 57.86% missing and `junction` is 69.29% missing.
- `endlatitude` and `endlongitude` include invalid `0.0` coordinates and out-of-city values, so they are not reliable as segment endpoints without cleaning.
- `map_file`, `comment`, and `meta_data` are 100% missing.
- This is not a congestion-labeled dataset. Congestion must be represented as incident risk or closure risk, not measured traffic congestion.

## Feasibility Summary

| Module | Classification | Score | Decision |
|---|---:|---:|---|
| Congestion Prediction Engine | Partially feasible | 55 | Simplify |
| Event DNA Engine | Fully feasible | 85 | Keep |
| Congestion Immunity Score | Partially feasible | 60 | Simplify |
| Congestion Propagation Analysis | Not feasible | 20 | Remove |
| Recommendation Engine | Partially feasible | 50 | Simplify |
| Geographic Visualization | Fully feasible | 90 | Keep |
| Traffic Hotspot Detection | Fully feasible | 85 | Keep |
| Event Similarity Analysis | Fully feasible | 80 | Keep |
| Resource Optimization | Partially feasible | 45 | Simplify |
| Risk Forecasting | Partially feasible | 65 | Simplify |

## Module-by-Module Validation

### 1. Congestion Prediction Engine

Classification: PARTIALLY FEASIBLE

Feasibility score: 55/100

Required columns:

- Timestamped traffic observations
- Location or road segment
- Congestion label, speed, volume, density, or travel time
- Weather, road capacity, event impact, closure status

Available columns:

- `start_datetime`, `created_date`, `modified_datetime`
- `latitude`, `longitude`
- `event_cause`, `event_type`, `priority`, `requires_road_closure`
- `corridor`, `police_station`, `zone`, `junction`

Missing columns:

- Traffic volume
- Speed
- Density
- Travel time
- Congestion ground-truth label
- Road capacity
- Weather
- Sensor or live feed data

Completeness and reliability:

- Event time and coordinates are mostly complete.
- There is no measured congestion target.
- `event_cause = congestion` exists, but only 136 rows and should not be treated as comprehensive congestion truth.

Recommended implementation approach:

- Do not build a true congestion prediction model.
- Build an incident-risk predictor or event burden predictor instead.
- Predict probability of high-impact incidents using historical event frequency, event cause, corridor, time of day, day of week, priority, and road closure flag.
- Rename the module to `Incident Risk Prediction Engine` or `Congestion Risk Proxy`.

### 2. Event DNA Engine

Classification: FULLY FEASIBLE

Feasibility score: 85/100

Required columns:

- Event type
- Event cause
- Time
- Location
- Severity or priority
- Closure flag
- Description
- Corridor or jurisdiction

Available columns:

- `event_type`, `event_cause`, `start_datetime`
- `latitude`, `longitude`
- `priority`, `requires_road_closure`
- `description`, `corridor`, `police_station`, `zone`, `junction`
- `status`, `veh_type`

Missing columns:

- Valid duration for all events
- Quantified event impact
- Verified response time for all records

Completeness and reliability:

- Core DNA fields are strong.
- `description` is missing for 16.64% of rows but still useful.
- `zone` and `junction` are incomplete, so corridor and police station should be primary grouping fields.

Recommended implementation approach:

- Keep this module.
- Build a feature vector per event: cause, type, corridor, police station, hour, weekday, priority, closure flag, vehicle type, description keywords, and geospatial cluster.
- Show an event profile card and aggregate DNA distributions by corridor or hotspot.

### 3. Congestion Immunity Score

Classification: PARTIALLY FEASIBLE

Feasibility score: 60/100

Required columns:

- Historical congestion frequency
- Road capacity
- Recovery duration
- Closure frequency
- Repeated incident burden by area or corridor
- Traffic throughput

Available columns:

- `corridor`, `police_station`, `latitude`, `longitude`
- `event_cause`, `priority`, `requires_road_closure`
- `start_datetime`, `closed_datetime`, `resolved_datetime`
- `status`

Missing columns:

- Capacity
- Speed
- Traffic volume
- Lane count
- Reliable duration for most records
- True congestion clearance time

Completeness and reliability:

- Enough data exists to score incident resilience by corridor or police station.
- Not enough data exists to score true congestion immunity.

Recommended implementation approach:

- Simplify to `Incident Resilience Score`.
- Score each corridor or police station using normalized incident rate, high-priority share, road-closure share, repeat hotspot count, and available median closure time.
- Clearly label this as a proxy score based on historical events.

### 4. Congestion Propagation Analysis

Classification: NOT FEASIBLE

Feasibility score: 20/100

Required columns:

- Road graph topology
- Adjacent links or nodes
- Time-series congestion spread
- Speed or density by segment over time
- Route paths or segment-level observations

Available columns:

- `latitude`, `longitude`
- `endlatitude`, `endlongitude`
- `route_path`
- `start_datetime`
- `corridor`

Missing columns:

- Reliable road network graph
- Segment adjacency
- Time-series traffic states
- Propagation labels
- Route paths for most events

Completeness and reliability:

- `route_path` is 98.32% missing.
- Endpoint coordinates include invalid values and cannot define a reliable network.
- No time-series traffic states exist.

Recommended implementation approach:

- Remove this module.
- Closest feasible alternative: `Nearby Event Co-occurrence Analysis`, showing events that occurred within a selected radius and time window.
- Do not present it as propagation or causal spread.

### 5. Recommendation Engine

Classification: PARTIALLY FEASIBLE

Feasibility score: 50/100

Required columns:

- Incident type
- Location
- Severity
- Historical actions taken
- Outcomes after action
- Resource availability
- Response time

Available columns:

- `event_cause`, `event_type`, `priority`, `requires_road_closure`
- `corridor`, `police_station`, `latitude`, `longitude`
- `description`, `status`
- `assigned_to_police_id` for only 128 rows

Missing columns:

- Recommended actions
- Actual interventions
- Resource inventory
- Crew availability
- Outcome measurements
- Reliable response and resolution times

Completeness and reliability:

- The dataset can support rule-based recommendations by event class.
- It cannot support learned recommendations or optimization from historical action outcomes.

Recommended implementation approach:

- Build a rule-based playbook, not an ML recommendation system.
- Example outputs: dispatch police for high-priority closure events, monitor frequent breakdown corridors, flag pothole clusters for maintenance review.
- Label recommendations as operational suggestions derived from event patterns.

### 6. Geographic Visualization

Classification: FULLY FEASIBLE

Feasibility score: 90/100

Required columns:

- Latitude
- Longitude
- Event attributes
- Optional grouping by corridor, police station, zone, or junction

Available columns:

- `latitude`, `longitude` with 100% coverage
- `event_cause`, `event_type`, `priority`, `requires_road_closure`
- `corridor`, `police_station`, `zone`, `junction`, `status`

Missing columns:

- Reliable route geometry
- Road-network shape files

Completeness and reliability:

- Point mapping is highly feasible.
- Line or route mapping is not reliable.

Recommended implementation approach:

- Keep this module.
- Build Folium or Plotly maps with event markers, heatmaps, corridor filters, cause filters, priority filters, and closure overlays.
- Avoid drawing road segments unless external road geometry is added later.

### 7. Traffic Hotspot Detection

Classification: FULLY FEASIBLE

Feasibility score: 85/100

Required columns:

- Event coordinates
- Event timestamp
- Severity or event type
- Area/corridor grouping

Available columns:

- `latitude`, `longitude`, `start_datetime`
- `event_cause`, `priority`, `requires_road_closure`
- `corridor`, `police_station`, `junction`

Missing columns:

- Traffic volume
- Speed
- True congestion measurements

Completeness and reliability:

- Strong for incident hotspots.
- Not a measured traffic-volume hotspot detector.

Recommended implementation approach:

- Keep as `Incident Hotspot Detection`.
- Use geospatial clustering such as DBSCAN or grid-based aggregation.
- Rank hotspots by event count, high-priority share, closure share, and recurring causes.

### 8. Event Similarity Analysis

Classification: FULLY FEASIBLE

Feasibility score: 80/100

Required columns:

- Event type
- Cause
- Location
- Time
- Severity
- Description text
- Optional vehicle type or corridor

Available columns:

- `event_type`, `event_cause`, `latitude`, `longitude`
- `start_datetime`, `priority`, `description`, `veh_type`, `corridor`, `police_station`

Missing columns:

- Standardized action outcome
- Complete descriptions

Completeness and reliability:

- Enough structured and semi-structured fields exist for meaningful similarity.
- Text data is imperfect but useful.

Recommended implementation approach:

- Keep this module.
- Use mixed similarity: categorical match, spatial distance, time-of-day similarity, and TF-IDF description similarity.
- Demonstrate by selecting an event and showing nearest historical analogs.

### 9. Resource Optimization

Classification: PARTIALLY FEASIBLE

Feasibility score: 45/100

Required columns:

- Resource inventory
- Staff or vehicle availability
- Demand by time and place
- Service time
- Response time
- Assignment history

Available columns:

- `start_datetime`, `latitude`, `longitude`
- `event_cause`, `priority`, `requires_road_closure`
- `police_station`, `corridor`
- `assigned_to_police_id` for 128 rows

Missing columns:

- Resource capacity
- Unit availability
- Dispatch logs
- Travel time
- Complete assignment records
- Complete resolution duration

Completeness and reliability:

- Demand pattern estimation is feasible.
- True resource optimization is not supported.

Recommended implementation approach:

- Simplify to `Demand-Aware Resource Planning`.
- Show expected incident load by police station, corridor, hour, and day.
- Produce staffing or patrol suggestions based on historical demand peaks, not optimized dispatch.

### 10. Risk Forecasting

Classification: PARTIALLY FEASIBLE

Feasibility score: 65/100

Required columns:

- Historical timestamped events
- Location or area grouping
- Event severity
- Cause
- Enough repeated observations over time

Available columns:

- `start_datetime`, `created_date`
- `event_cause`, `priority`, `requires_road_closure`
- `corridor`, `police_station`, `latitude`, `longitude`

Missing columns:

- Weather
- Traffic volume
- Road works schedules outside event records
- Calendar of external events
- Longer multi-year history

Completeness and reliability:

- The dataset covers roughly five months of events.
- Short-term historical risk scoring is feasible; robust long-range forecasting is not.

Recommended implementation approach:

- Simplify to historical risk forecasting by hour/day/corridor.
- Use rolling averages, seasonal hour-of-week patterns, or a conservative baseline classifier.
- Output risk buckets instead of precise predictions.

## Features That Can Be Implemented Fully

- Event DNA Engine
- Geographic Visualization
- Incident Hotspot Detection
- Event Similarity Analysis

These features align directly with the available event, location, time, cause, priority, corridor, and description fields.

## Features That Should Be Simplified

- Congestion Prediction Engine -> Incident Risk Prediction Engine
- Congestion Immunity Score -> Incident Resilience Score
- Recommendation Engine -> Rule-Based Operational Playbook
- Resource Optimization -> Demand-Aware Resource Planning
- Risk Forecasting -> Historical Incident Risk Forecasting

These features can be demonstrated convincingly only if framed as event-risk and operational analytics, not as true traffic simulation or congestion modeling.

## Features That Should Be Removed Entirely

- Congestion Propagation Analysis

Reason:

- The dataset does not contain a road graph, reliable route paths, segment adjacency, or measured time-series congestion states.
- Implementing propagation would require hallucinating traffic dynamics.

Closest feasible alternative:

- Nearby event co-occurrence within a spatial radius and time window.

## Revised Architecture

The architecture should be event-analytics first:

1. Data Loader
   - Load the single Astram event CSV.
   - Normalize column names and parse timestamps.

2. Data Quality Layer
   - Validate coordinates.
   - Remove or flag invalid endpoint coordinates.
   - Parse datetime fields.
   - Add safe derived fields: hour, weekday, month, duration where available, closure flag, high-priority flag.

3. Event Analytics Layer
   - Event DNA profiles.
   - Incident hotspots.
   - Similar event search.
   - Corridor and police-station summaries.

4. Risk Proxy Layer
   - Historical incident risk by corridor, police station, cause, hour, and weekday.
   - Incident resilience score.
   - Demand-aware resource planning.

5. Recommendation Layer
   - Rule-based operational suggestions tied to observed patterns.

6. Visualization Layer
   - Map view.
   - Hotspot view.
   - Corridor dashboard.
   - Event similarity explorer.

## Revised Roadmap

### Phase 1: Dataset Analysis

Status: complete.

Outputs:

- Dataset column inventory
- Missingness analysis
- Feasibility report

### Phase 2: Project Reality Check

Status: complete in this report.

Decision:

- Build an event intelligence prototype, not a full congestion simulation platform.

### Phase 3: Data Foundation

- Implement robust event CSV loader.
- Implement cleaning and validation.
- Generate processed event dataset.

### Phase 4: Geographic Visualization

- Build event map, filters, heatmap, and hotspot overlays.

### Phase 5: Event DNA

- Build event profile generation and aggregate DNA cards.

### Phase 6: Hotspot Detection

- Build geospatial clustering and ranked hotspot tables.

### Phase 7: Event Similarity

- Build similar-event search using structured and text features.

### Phase 8: Risk Proxy

- Build historical incident risk scoring by corridor, police station, hour, and weekday.

### Phase 9: Recommendations

- Build rule-based operational playbook tied to hotspot and risk outputs.

### Phase 10: Demo Polish

- Create a coherent dashboard narrative.
- Remove or rename unsupported congestion claims.
- Add transparent dataset limitations.

## Final Feasibility Decision

Proceed with a working prototype focused on:

- Where incidents happen
- What kind of incidents dominate
- Which corridors and police stations carry the highest incident burden
- Which historical events are similar
- Which locations and time windows have higher future incident risk
- What rule-based operational actions are suggested

Do not build:

- True congestion propagation
- True traffic-flow prediction
- True resource optimization
- Route-level simulation
- Any feature requiring fabricated traffic volume, speed, road graph, or capacity data
