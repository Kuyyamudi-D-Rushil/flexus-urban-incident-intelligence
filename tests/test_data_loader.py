from src.data_loader import load_csv


def test_load_csv_smoke():
    assert callable(load_csv)
