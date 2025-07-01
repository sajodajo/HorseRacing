# HorseRacing Big Data Derby 2022 Competition 

**Race Strategy Profiling and Performance Feature Engineering**

## Data Sources

### Main dataset  Column Descriptions

### Main dataset Column Descriptions

- `nyra_2019_complete` [https://www.kaggle.com/competitions/big-data-derby-2022/overview](Link):
- 2.000 races
- 3 racing tracks in the US (AQU = Aqueduct, BEL = Belmont , SAR = Saratoga)

#### Original Raw Columns

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
| `purse`              | Purse in US dollars of the race passed as money with two decimal places. |
| `jockey`             | Name of the jockey (up to 50 characters). |
| `odds`               | Odds to win multiplied by 100 (e.g., 1280 = 12.8-1). |
| `position_at_finish` | Finishing position of the horse in the race (integer). |

#### Engineered Features

| Column                    | Description |
|---------------------------|-------------|
| **Distance & Scale Conversions** |             |
| `distance_id_m`           | Race distance converted from furlongs to meters (distance_id/100 * 201.168). |
| `run_up_distance_m`       | Run-up distance converted from feet to meters (run_up_distance / 3.28084). |
| **Primary Keys & Identifiers** |             |
| `horse_pk`                | Unique horse identifier per race: "{track_id}_{race_date}_{race_number}_{program_number}". |
| `rid`                     | Race identifier: "{track_id}_{race_date}_{race_number}". |
| `horse_id`                | Global unique horse identifier (joined from supplementary data). |
| `horse_name`              | Name of the horse (joined from supplementary data). |
| **Course Type Mapping**   |             |
| `course_type` (processed) | Simplified course types: "Turf" (T, I, O) or "Dirt" (D). Hurdle races (M) are filtered out. |
| **Betting & Performance** |             |
| `odds_to_one`             | Odds converted to decimal format (odds / 100). |
| `implied_win_probability` | Implied win probability: 1 / (odds_to_one + 1). |
| `win`                     | Binary flag: 1 if horse won (position_at_finish == 1), 0 otherwise. |
| **Time & Distance Calculations** |             |
| `time_seconds`            | Time in seconds (trakus_index * 0.25). |
| `distance_m`              | Distance between consecutive GPS points using Haversine formula (meters). |
| `cumulative_distance_m`   | Cumulative distance traveled by horse from race start (meters). |
| `cum_race_distance_m`     | Race distance corrected for run-up distance (cumulative_distance_m - run_up_distance_m). |
| `race_max_distance_m`     | Maximum cumulative distance for the entire race. |
| **Speed Calculations**    |             |
| `speed_kmh`               | Instantaneous speed in km/h calculated from GPS coordinates and time. |
| **Race Position Tracking** |             |
| `position_rank`           | Current position rank based on race progress (cum_race_distance_m) at each trakus_index. |
| **Race Progress Analysis** |             |
| `pctComplete`             | Percentage of race completed (cumulative_distance_m / race_max_distance_m). |
| `Segment`                 | Race segment: Q1 (<25%), Q2 (25-50%), Q3 (50-75%), Q4 (75-100%). |
| **Segment-Based Performance Metrics** |             |
| `speed_Q1`                | Average speed during first quarter of race (km/h). |
| `speed_Q2`                | Average speed during second quarter of race (km/h). |
| `speed_Q3`                | Average speed during third quarter of race (km/h). |
| `speed_Q4`                | Average speed during final quarter of race (km/h). |
| `pos_Q1`                  | Median position during first quarter of race. |
| `pos_Q2`                  | Median position during second quarter of race. |
| `pos_Q3`                  | Median position during third quarter of race. |
| `pos_Q4`                  | Median position during final quarter of race. |

#### Data Processing Notes

- **Finish Line Truncation**: GPS tracking data is truncated at the exact point each horse crosses the finish line to ensure accurate speed and tactical analysis.
- **Hurdle Race Filtering**: All hurdle races (course_type = "M") are removed from the dataset.
- **Missing Data Handling**: Horses without supplementary ID/name data are retained but flagged in processing logs.
- **Speed Calculation**: Uses Haversine formula for accurate distance calculation between GPS coordinates.
- **Position Ranking**: Dense ranking ensures horses at identical race progress receive the same position rank.


### Supplemenatry datasets
[https://www.kaggle.com/datasets/themarkgreen/big-data-derby-2022-global-horse-ids-and-places](Link):
- `horse_ids.csv`: Unique identifiers of horses to uniquely identify horses across races
- `horse_names.csv`: Name of the horses (optional)


## Repo Setup

High-level structure of the repository:


```
.
└── HorseRacing
    ├── data    
    │   ├── raw
    │   └── processed                           # data for streamlit app
    ├── notebooks                               # EDA
    └── src                                     # main app folder
        ├── assets                              # images, icons etc.
        ├── ingestion                           # preprocessing logic raw -> processed data
        │   └── preprocessing_pipeline.py
        ├── ui                                  # streamlit frontend
        │   ├── pages                           # sub-pages
        │   └── Home.py                         # entry/main page
        └── utils
```



## Prerequisites for Setup
- uv or pip (Python package installer)
- OpenAI API Key (optional)

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

#### AI Agent Setup (optional)

Add a `.env` file to the root of the repo and add your OpenAI API key `OPENAI_API_KEY="sk-...`

#### Instantiate database 

Run the script to clean and preprocess the initial dataset:

```bash
uv run src/ingestion/preprocessing_pipeline.py
```

A `.parquet` and `.db` file will be saved under `data/processed`.

### Run Streamlit App

To run the Streamlit app, run the following command from the root:

```bash
uv run streamlit run src/ui/Home.py
```

### Contributing
To add new dependencies just run:

```bash
uv add <library-name>

# or to remove again
uv remove <library-name>
```

To run any script use:

```
uv run <script-name>.py
```


## Contributors
- Sam Jones
- Marius Gnoth
- Vandad Vafai
- Joaquin Miño
- Maine Isasi