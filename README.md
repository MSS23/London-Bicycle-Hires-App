## London Bicycle Hires Dashboard

A Streamlit dashboard for exploring London cycle hire data, featuring three main sections:

1. **KPI Summary**: Displays total rides, average ride duration, busiest stations, and other key metrics.
2. **Bike Maintenance**: Identifies bikes with errors or unusual usage. For flagged bikes, you can filter by error type, view metadata, inspect the latest faulty trip, and locate its endpoint on a map.
3. **Station Capacity**: Monitors station fill levels, highlights stations over 75% or under 25% capacity, and suggests up to five nearby stations under 50% capacity for rebalancing.

---

## Prerequisites

* **Python 3.x**
* **pip** for installing packages
* **Google Cloud**: service account with BigQuery dataset access
* **Service account key** (JSON)

---

## Installation & Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/MSS23/London-Bicycle-Hires-App.git
   cd London-Bicycle-Hires-App
   ```
2. **Install dependencies and launch**

   ```bash
   uv run streamlit run app/main.py
   ```

Open your browser at [http://localhost:8501](http://localhost:8501).

---

## Notebooks

The `eda/` directory contains Jupyter notebooks for data exploration:

* **`data_analysis.ipynb`**: Exploratory analysis of rides and stations with charts and tables.
* **`data_quality.ipynb`**: Data consistency checks, outlier detection, and cleaning documentation.
* **`store_dataset.ipynb`**: Loading raw data into Parquet and storing in `storage/Bronze`.

---

## Project Structure

```
London-Bicycle-Hires-App/
├── app/
│   ├── main.py
│   ├── kpi_summary.py
│   ├── bike_maintenance.py
│   ├── station_capacity.py
│   └── utils/
│       ├── data_loader.py
│       └── helper.py
├── credentials/           # service keys (ignored by Git)
│   └── bq_data_viewer.json
├── eda/                   # exploratory notebooks
│   ├── data_analysis.ipynb
│   ├── data_quality.ipynb
│   └── store_dataset.ipynb
├── storage/
│   ├── Bronze/            # raw data (ignored by Git)
│   │   ├── cycle_hire_2022.parquet
│   │   └── cycle_stations.parquet
│   └── Silver/            # processed outputs
│       ├── kpi_summary.parquet
│       ├── maintenance_tasks.csv
│       └── station_capacity_report.csv
├── .gitignore
├── .gitattributes        # LFS settings
├── requirements.txt      # project dependencies
└── README.md
```

---

## .gitignore

```
# Sensitive or environment files
credentials/*.json
.venv/
__pycache__/
```
