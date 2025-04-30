# HorseRacing Big Data Derby 2022 Competition 



## Data Sources

### Main dataset  Column Descriptions

- `nyra_2019_complete` [https://www.kaggle.com/competitions/big-data-derby-2022/overview](Link):`
- 2.000 races
- 3 racing tracks in the US (AQU = Aqueduct, BEL = Belmont , SAR = Saratoga)

| Column               | Description |
|----------------------|-------------|
| `track_id`           | 3-character ID for the track where the race took place. (AQU - Aqueduct, BEL - Belmont, SAR - Saratoga) |
| `race_date`          | Date of the race in YYYY-MM-DD format. |
| `race_number`        | Race number (3-character string, can be cast to int). |
| `program_number`     | Program number of the horse in the race (3-character string, may include letters). |
| `trakus_index`       | Ordered Index representing time intervals (~0.25 seconds) in tracking data. |
| `latitude`           | Latitude of the horse's position at the `trakus_index` time. |
| `longitude`          | Longitude of the horse's position at the `trakus_index` time. |
| `distance_id`        | Distance of the race in furlongs (e.g., 600 = 6 furlongs). |
| `course_type`        | Course surface type. (M - Hurdle, D - Dirt, O - Outer turf, I - Inner turf, T - Turf) |
| `track_condition`    | Condition of the course. (e.g., YL - Yielding, FM - Firm, FT - Fast, etc.) |
| `run_up_distance`    | Distance in feet from the gate to the actual start of the race. |
| `race_type`          | Classification of the race. (e.g., STK - Stakes, CLM - Claiming, MSW - Maiden Special Weight, etc.) |
| `post_time`          | Time the race began, in HHMM format (e.g., 01220 = 12:20). |
| `weight_carried`     | Weight carried by the horse (in pounds). |
| `jockey`             | Name of the jockey (up to 50 characters). |
| `odds`               | Odds to win multiplied by 100 (e.g., 1280 = 12.8-1). |
| `position_at_finish` | Finishing position of the horse in the race (integer). |


### Supplemenatry datasets
[https://www.kaggle.com/datasets/themarkgreen/big-data-derby-2022-global-horse-ids-and-places](Link):
- `horse_ids.csv`: Unique identifiers of horses to uniquely identify horses across races
- `horse_names.csv`: Name of the horses (optional)

## Research Focus

(tbd)

## Repo

High-level structure of the repository:

```
.
└── HorseRacing
    ├── data
    │   ├── raw                             # raw data files from Kaggle
    │   └── processed                       # cleaned and preprocess files for training
    ├── notebooks                           # EDA and reporting
    ├── src
    │   ├── ingestion_pipeline              # from raw to processed data files
    │   │   └── main.py                     # Scripts for pipeline
    │   └── models                          # Trained model files
    └── pyproject.toml                      # managing dependencies
```



## Prerequisites for Setup
- uv or pip (Python package installer)

To install `uv`, run the following command:

```bash
# windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or via `pip`:

```bash
pip install uv
```

### Project Setup


#### Clone the Repository

To get started run:

```bash
git clone <repo-url>
cd HorseRacing # move into directory
```

#### Setup the Virtual Environment

To install all necessary libraries and dependencies, run:

```bash
uv sync

# activate virtual environment
.venv/Scripts/activate # or source venv/bin/activate
```

To add new dependencies just run:

```bash
uv add <library-name>

# or to remove again
uv remove <library-name>
```

To run scripts:

```bash
uv run <script-name>.py
```


## Contributors
- Vandad Vafai
- Joaquin Miño
- Marius Gnoth
- Sam Jones
- Maine Isasi