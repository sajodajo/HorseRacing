# HorseRacing Big Data Derby 2022 Competition 



## Data Sources

Main dataset [https://www.kaggle.com/competitions/big-data-derby-2022/overview](Link):

- 2.000 races
- 3 racing tracks in the US (AQU = Aqueduct, BEL = Belmont , SAR = Saratoga)
- Different race track conditions (e.g., muddy, soft) or race types (e.g., Stakes, Handicap)
- For each race and horse the dataset contains the coordinates in a fixed time window, frame-by-frame. This allows for calculating relative positions, speeds, and visualization of the race

Supplemenatry datasets [https://www.kaggle.com/datasets/themarkgreen/big-data-derby-2022-global-horse-ids-and-places](Link):
- `horse_names.csv`: Unique identifiers of horses to uniquely identify horses across races
- `horse_name`: Name of the horses (optional)

## Research Focus


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