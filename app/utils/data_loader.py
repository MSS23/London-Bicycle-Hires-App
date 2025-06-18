from pathlib import Path
import pandas as pd
import os
from google.cloud import bigquery

store = Path(r"C:\Users\msidh\Documents\Coding\London Bicycle Hires App\storage\Bronze")

if not store.exists():
    raise FileNotFoundError(f"Expected folder not found: {store.resolve()}")


def load_trips_data():
    path = store / "cycle_hire_2022.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.resolve()}")
    return pd.read_parquet(path)


def load_stations_data():
    path = store / "cycle_stations.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.resolve()}")
    return pd.read_parquet(path)


# GCP setup
project = "london-bike-hire-dataset-test"
location = "EU"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    r"C:\Users\msidh\Documents\Coding\London Bicycle Hires App\credentials\bq_viewer_key.json"
)
client = bigquery.Client(project=project, location=location)
