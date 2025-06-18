# London Bicycle Hires Dashboard

A simple dashboard to explore London cycle hire data. It has three main parts:

* **KPI Summary**: Shows total rides, average ride time, busiest stations and other key figures.
* **Bike Maintenance**: Lists bikes that need attention based on errors or unusual usage.
* **Station Capacity**: Checks how full each station is and suggests rebalancing.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MSS23/London-Bicycle-Hires-App.git
   cd London-Bicycle-Hires-App
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies (using UV):

   ```bash
   uv install
   ```

---

### Dashboard

To view all modules in one place, run:

```bash
python app/main.py
```

Open your browser at [http://localhost:8501](http://localhost:8501).

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
├── credentials/         # service keys (ignored)
├── eda/                 
├── storage/
│   ├── Bronze/         # raw data (ignored)
│   └── Silver/         # outputs
├── .gitignore
├── .gitattributes      # LFS settings
├── pyproject.toml
└── README.md
```

---

## .gitignore suggestions

* Ignore data folders and large files:

  ```gitignore
  eda/
  storage/Bronze/
  *.parquet
  *.csv
  ```

---

## Licence

MIT © MSS23
