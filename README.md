# London Bicycle Hires Dashboard

A simple dashboard to explore London cycle hire data. It has three main parts:

* **KPI Summary**: Shows total rides, average ride time, busiest stations and other key figures.
* **Bike Maintenance**: Lists bikes with errors or unusual usage patterns. For each flagged bike, you can filter by error type, view its metadata, see its most recent faulty trip, and locate where that trip ended on a map.
* **Station Capacity**: Monitors station fill levels, highlights stations above 75% capacity or under 25% capacity, and finds up to five nearby stations under 50% capacity for rebalancing bikes from a selected station.

---

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/MSS23/London-Bicycle-Hires-App.git
   cd London-Bicycle-Hires-App
   ```
2. **Create and activate a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies** (using UV installer):

   ```bash
   uv install
   ```

> **Note:** UV reads from `pyproject.toml`, so you don’t strictly need a `requirements.txt` file. If you prefer `pip`, you can generate one with:
>
> ```bash
> pip freeze > requirements.txt
> ```

---

## Running the App

Once dependencies are installed, launch the dashboard with:

```bash
# from the project root
to run Streamlit dashboard:
streamlit run app/main.py
```

Open your browser at [http://localhost:8501](http://localhost:8501) to view the app.

---

## Notebooks

Under `eda/` you’ll find Jupyter notebooks for exploratory work:

* **data\_analysis.ipynb**: Initial exploration of ride and station data, generating charts and summary tables.
* **data\_quality.ipynb**: Checks data consistency, finds missing or outlier values, and documents cleaning steps.
* **store\_dataset.ipynb**: Demonstrates loading raw data into Parquet format and storing it in `storage/Bronze`.

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
├── credentials/            # service keys (ignored)
├── eda/                    # exploratory notebooks
│   ├── data_analysis.ipynb
│   ├── data_quality.ipynb
│   └── store_dataset.ipynb
├── storage/
│   ├── Bronze/            # raw data (ignored)
│   │   ├── cycle_hire_2022.parquet
│   │   └── cycle_stations.parquet
│   └── Silver/            # processed outputs
│       ├── kpi_summary.parquet
│       ├── maintenance_tasks.csv
│       └── station_capacity_report.csv
├── .gitignore
├── .gitattributes         # LFS settings
├── pyproject.toml
└── README.md

```

---

```

gitignore


# Sensitive or environment files
credentials/*.json
.venv/
__pycache__/
````

This setup keeps your code and notebooks under version control but virtual environment and secrets.
