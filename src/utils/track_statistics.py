import polars as pl
import pathlib

def calculate_track_summary_stats_landingpage():
    """
    For the landing page calculate summary stats for a track profile
    - # Number of available races
    - # Available race dates 
    - Available race types and length
    - # Number of unique horses
    - # Number of unique jockeys
    """
    current_file = pathlib.Path(__file__)
    project_root = current_file.parent.parent.parent  # Go from utils/ to src/ to HorseRacing/
    parquet_path = project_root / "data" / "processed" / "df_clean.parquet"

    # Load the data
    df = pl.scan_parquet(str(parquet_path)).collect()

    stats = {}

    # Number of available races (assuming each row is a horse in a race, so group by unique race id)
    if "rid" in df.columns:
        stats["num_races"] = df["rid"].n_unique()
    else:
        stats["num_races"] = df.select([pl.col("track_id"), pl.col("race_date"), pl.col("race_number")]).unique().height

    # Number of available race dates
    stats["num_race_dates"] = df["race_date"].n_unique()

    # Available race types and lengths
    if "race_type" in df.columns and "distance_id" in df.columns:
        stats["race_types_and_lengths"] = (
            df.select([pl.col("race_type"), pl.col("distance_id")])
              .unique()
              .to_dict(as_series=False)
        )
    else:
        stats["race_types_and_lengths"] = {}

    # Number of unique horses
    if "horse_id" in df.columns:
        stats["num_unique_horses"] = df["horse_id"].n_unique()
    else:
        stats["num_unique_horses"] = df["program_number"].n_unique()

    # Number of unique jockeys
    if "jockey" in df.columns:
        stats["num_unique_jockeys"] = df["jockey"].n_unique()
    else:
        stats["num_unique_jockeys"] = None

    # Available tracks
    stats["tracks"] = df["track_id"].unique().to_list()

    return stats


if __name__ == "__main__":
    stats = calculate_track_summary_stats_landingpage()
    print(stats)