from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"


def ensure_project_dirs() -> None:
    for path in [
        RAW_DIR,
        PROCESSED_DIR,
        OUTPUTS_DIR,
        OUTPUTS_DIR / "maps",
        OUTPUTS_DIR / "figures",
        REPORTS_DIR,
        MODELS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def find_raw_dataset() -> Path:
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV dataset found in {RAW_DIR}")
    return csv_files[0]
