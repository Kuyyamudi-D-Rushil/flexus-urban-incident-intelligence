import pandas as pd

from src.utils.paths import find_raw_dataset


def load_raw_events(path=None) -> pd.DataFrame:
    dataset_path = path or find_raw_dataset()
    return pd.read_csv(dataset_path)


def load_processed_events(path) -> pd.DataFrame:
    return pd.read_csv(path)
