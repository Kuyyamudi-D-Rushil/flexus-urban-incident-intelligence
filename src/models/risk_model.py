import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


RISK_CATEGORICAL = ["event_type", "event_cause", "corridor", "police_station", "veh_type", "weekday"]
RISK_NUMERIC = ["latitude", "longitude", "hour", "month", "is_peak_hour", "is_weekend"]


def choose_target(df: pd.DataFrame) -> str:
    closure_rate = df["closure_flag"].mean()
    high_priority_rate = df["high_priority_flag"].mean()
    if 0.1 <= closure_rate <= 0.9:
        return "closure_flag"
    if 0.1 <= high_priority_rate <= 0.9:
        return "high_priority_flag"
    return "high_priority_flag"


def train_risk_model(df: pd.DataFrame, model_path):
    target = choose_target(df)
    data = df.copy()
    features = RISK_CATEGORICAL + RISK_NUMERIC + ["description_clean"]
    for column in RISK_CATEGORICAL:
        data[column] = data[column].astype("string").fillna("Unknown")
    for column in RISK_NUMERIC:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    data["description_clean"] = data["description_clean"].fillna("")

    X = data[features]
    y = data[target].astype(int)
    stratify = y if y.nunique() > 1 and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=stratify
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), RISK_CATEGORICAL),
            ("text", TfidfVectorizer(max_features=100, min_df=3), "description_clean"),
            ("num", "passthrough", RISK_NUMERIC),
        ]
    )
    clf = RandomForestClassifier(
        n_estimators=160,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=1,
    )
    pipeline = Pipeline([("features", preprocessor), ("model", clf)])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    proba = pipeline.predict_proba(X_test)[:, 1] if len(pipeline.classes_) == 2 else preds

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="f1")

    report = {
        "target": target,
        "accuracy": accuracy_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, proba) if y_test.nunique() == 2 else None,
        "cv_f1_mean": float(cv_scores.mean()),
        "cv_f1_std": float(cv_scores.std()),
        "classification_report": classification_report(y_test, preds),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        "features": features,
    }

    joblib.dump({"pipeline": pipeline, "target": target, "features": features, "report": report}, model_path)
    return report
