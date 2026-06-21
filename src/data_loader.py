import pandas as pd

from src.data.loader import load_raw_events
from src.utils.paths import PROCESSED_DIR, RAW_DIR


DATA_RAW = RAW_DIR
DATA_PROCESSED = PROCESSED_DIR


def load_csv(path):
    return pd.read_csv(path)


def load_events():
    return load_raw_events()


def load_traffic():
    raise NotImplementedError("This project has an incident event log, not traffic sensor data.")


def load_roads():
    raise NotImplementedError("No road network dataset is available in the provided data.")


def save_processed_data(df, filename):
    path = DATA_PROCESSED / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
