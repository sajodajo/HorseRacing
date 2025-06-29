import pandas as pd
import numpy as np
import streamlit as st
import polars as pl
import os
from datetime import datetime, timedelta
import sqlite3

##########################################
# Preprocessing pipeline for ingestion
##########################################

# Globals

BASE_DIR = os.path.dirname(__file__)  # Path to this script

BASE_DIR = os.path.dirname(__file__)
main_file_path = os.path.abspath(os.path.join(BASE_DIR, "../../data/raw/nyra_2019_complete.parquet"))
horse_global_ids = os.path.abspath(os.path.join(BASE_DIR, "../../data/raw/horse_ids.csv"))
horse_names = os.path.abspath(os.path.join(BASE_DIR, "../../data/raw/horse_names.csv"))
processed_data_dir = os.path.abspath(os.path.join(BASE_DIR, "../../data/processed"))


def load_data(main_file_path, horse_global_ids, horse_names):

    ##########################################
    # Loading, Re-Mapping, Formatting
    ##########################################


    df = pl.read_parquet(main_file_path)
    df_horse_ids = pl.read_csv(horse_global_ids)
    df_horse_names = pl.read_csv(horse_names)

    df = df.rename({
        df.columns[0]: 'track_id',
        df.columns[1]: 'race_date',
        df.columns[2]: 'race_number',
        df.columns[3]: 'program_number',
        df.columns[4]: 'trakus_index',
        df.columns[5]: 'latitude',
        df.columns[6]: 'longitude',
        df.columns[7]: 'distance_id',
        df.columns[8]: 'course_type',
        df.columns[9]: 'track_condition',
        df.columns[10]: 'run_up_distance',
        df.columns[11]: 'race_type',
        df.columns[12]: 'purse',
        df.columns[13]: 'post_time',
        df.columns[14]: 'weight_carried',
        df.columns[15]: 'jockey',
        df.columns[16]: 'odds',
        df.columns[17]: 'position_at_finish'
    })

    print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns")
   
   # Scale conversions
    df = df.with_columns([
        ((pl.col("distance_id") / 100) * 201.168).round(2).alias("distance_id_m"),  # convert distance_id (furlongs) to meters
        (pl.col("run_up_distance").cast(pl.Float64) / 3.28084).round(2).alias("run_up_distance_m")  # convert run_up_distance (feet) to meters
    ])

    ##########################################
    # Filtering
    ##########################################

    #TODO: FILTER OUT EDGE CASES, FOCUS ON RACE TYPES, NULLS etc.

    # filter out all hurdle races (course_type M)
    df = df.filter(pl.col("course_type") != "M")

    # make course types more readble. Combine all into one T,I, O into Turf
    course_type_map = {
        "T": "Turf",
        "I": "Turf",
        "O": "Turf",
        "D": "Dirt"
    }

    df = df.with_columns(
        pl.col("course_type").replace_strict(course_type_map, default=pl.col("course_type")).alias("course_type")
    )

    ##########################################
    # Create primary keys, join supplementary datasets
    ##########################################

    # create unique identifiers

    # identify unique horse per track, race, program_number

    df = df.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8) + "_" +
         pl.col("program_number").cast(pl.Utf8).str.strip_chars()).alias("horse_pk"),
         # race id (pk)
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8)).alias("rid")
    ])

    # same for supplementary dataset

    df_horse_ids = df_horse_ids.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race").cast(pl.Utf8) + "_" +
         pl.col("program_number").cast(pl.Utf8).str.strip_chars()).alias("horse_pk"),

         pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    # join id dataset and supplementary dataset

    df = df.join(df_horse_ids.select(["horse_pk", "horse_id"]), on="horse_pk", how="left")

    df_horse_names = df_horse_names.with_columns([
        pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    df = df.join(df_horse_names.select(["horse_id", "horse_name"]), on="horse_id", how="left")

    # log where joined datasets are missing values
    missing_horse_ids = df.filter(pl.col("horse_id").is_null())
    missing_horse_names = df.filter(pl.col("horse_name").is_null())
    if missing_horse_ids.shape[0] > 0:
        print(f"Warning: {missing_horse_ids.shape[0]} rows missing horse_id after join")
    if missing_horse_names.shape[0] > 0:
        print(f"Warning: {missing_horse_names.shape[0]} rows missing horse_name after join")

    ##########################################
    # Finish line truncation
    ##########################################

    # 1. Define finish line coordinates for each racetrack
    FINISH_LINE_COORDINATES = {
        "AQU": [[40.671541, -73.831052], [40.671813, -73.832118], 
                [40.671731, -73.832148], [40.671464, -73.831092]],
        "BEL": [[40.713841, -73.722387], [40.713086, -73.722747], 
                [40.713062, -73.722658], [40.713815, -73.722292]],
        "SAR": [[43.071827, -73.770376], [43.072490, -73.770852], 
                [43.072438, -73.770989], [43.071777, -73.770502]]
    }

    LONG_FURLONG_BUFFER = 200  # avoiding early misclassifications

    def point_in_polygon(lat: float, lon: float, polygon_coords: list[list[float]]) -> bool:
        """
        Determine if a point is inside a polygon using the ray casting algorithm.
        
        Args:
            lat: Latitude of the point
            lon: Longitude of the point  
            polygon_coords: List of [lat, lon] coordinate pairs defining the polygon
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        x, y = lat, lon
        n = len(polygon_coords)
        inside = False
        
        p1x, p1y = polygon_coords[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_coords[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside


    def create_finish_line_detector(track_coords: dict) -> pl.Expr:
        """
        Create a Polars expression to detect finish line crossings for all tracks.
        
        Args:
            track_coords: Dictionary mapping track IDs to their finish line coordinates
            
        Returns:
            Polars expression that evaluates to True when horse is inside finish line
        """
        # Build conditional expression for each track
        expr = pl.lit(False)  # Default case
        
        for track_id, coords in track_coords.items():
            track_condition = (
                pl.when(pl.col("track_id") == track_id)
                .then(
                    pl.struct(["latitude", "longitude"]).map_elements(
                        lambda x: point_in_polygon(x["latitude"], x["longitude"], coords),
                        return_dtype=pl.Boolean
                    )
                )
            )
            expr = track_condition.otherwise(expr)
        
        return expr


    def truncate_at_finish_line(df: pl.DataFrame) -> pl.DataFrame:
        """
        Truncate horse tracking data at the exact point each horse crosses the finish line.
        
        This ensures that post-race tracking data doesn't contaminate speed calculations
        and tactical analysis by removing all observations after finish line crossing.
        
        Args:
            df: DataFrame containing horse tracking data with columns:
                - horse_pk: Unique horse identifier per race
                - track_id: Track identifier (AQU, BEL, SAR)
                - latitude, longitude: GPS coordinates
                - trakus_index: Temporal sequence index
                
        Returns:
            DataFrame with tracking data truncated at finish line crossings
        """
        print("Starting finish line truncation process...")
        initial_rows = df.shape[0]
        
        # 2. Detect finish line crossings
        df = df.with_columns([
            create_finish_line_detector(FINISH_LINE_COORDINATES).alias("inside_finish_rect")
        ])
        
        # 3. Calculate metadata for long furlong race handling
        df = df.with_columns([
            pl.len().over("horse_pk").alias("total_observations"),
            (pl.len().over("horse_pk") - LONG_FURLONG_BUFFER).alias("min_trakus_threshold")
        ])
        
        # 4. Identify finish line trakus_index for each horse
        finish_indices = (
            df
            .filter(
                pl.col("inside_finish_rect") & 
                (pl.col("trakus_index") > pl.col("min_trakus_threshold"))
            )
            .sort(["horse_pk", "trakus_index"])
            .group_by("horse_pk")
            .agg(pl.col("trakus_index").first().alias("finish_trakus_index"))
        )

        # Debugging finish line detection
        print("Finish indices:")
        print(finish_indices.head(10))  # Inspect the first 10 rows of finish_trakus_index
        
        # Debugging rows where inside_finish_rect is True
        print("Rows where inside_finish_rect is True:")
        print(
            df.filter(pl.col("inside_finish_rect"))
            .select(["horse_pk", "trakus_index", "latitude", "longitude", "inside_finish_rect", "total_observations", "min_trakus_threshold"])
            .head(10)
        )
                
        # 5. Apply truncation
        df = (
            df
            .join(finish_indices, on="horse_pk", how="left")
            .filter(
                pl.col("finish_trakus_index").is_null() |
                (pl.col("trakus_index") <= pl.col("finish_trakus_index"))
            )
            .drop([
                "total_observations", 
                "min_trakus_threshold", 
                "inside_finish_rect", 
                "finish_trakus_index"
            ])
        )
        
        # 6. Report results
        final_rows = df.shape[0]
        removed_percentage = (initial_rows - final_rows) / initial_rows * 100
        
        print("Finish line truncation completed:")
        print(f"Initial rows: {initial_rows:,}")
        print(f"Final rows: {final_rows:,}")
        print(f"Removed: {removed_percentage:.2f}% of observations")
        
        return df


    df = truncate_at_finish_line(df)

    ##########################################
    # Feature Engineering
    ##########################################

    # binary winner flag

    df = df.with_columns([
        pl.col("program_number").cast(pl.Utf8).str.strip_chars(),
        (pl.col("position_at_finish") == 1).cast(pl.Int8).alias("win")
    ])

    ##########################################
    # Distance and Speed Calculation
    ##########################################

    df = df.sort(["horse_pk", "trakus_index"])

    # trackus_index = 0.25 sec

    df = df.with_columns([
        (pl.col("trakus_index") * 0.25).alias("time_seconds")
    ])

    def haversine_distance(lat1, lon1, lat2, lon2):
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371000 
        return c * r

    # Calculate previous position and time using lag
    df = df.with_columns(
        pl.col("latitude").shift(1).over("horse_pk").alias("prev_latitude"),
        pl.col("longitude").shift(1).over("horse_pk").alias("prev_longitude"),
        pl.col("time_seconds").shift(1).over("horse_pk").alias("prev_time_seconds"),
        (pl.col("trakus_index") == pl.col("trakus_index").min().over("horse_pk")).alias("is_first_obs")
    )
    
    # Calculate distance in meters using haversine formula
    # distance between two consecutive Trakus points.

    df = df.with_columns(
        pl.when(pl.col("is_first_obs"))
        .then(0.0)
        .when(
            (pl.col("prev_latitude").is_not_null()) & 
            (pl.col("horse_pk") == pl.col("horse_pk").shift(1))
        ).then(
            haversine_distance(
                pl.col("prev_latitude"),
                pl.col("prev_longitude"),
                pl.col("latitude"),
                pl.col("longitude")
            )
        ).otherwise(0).alias("distance_m")
    )

    # Calculate cumulative distance per horse
    df = df.with_columns([
        pl.col("distance_m").cum_sum().over("horse_pk").alias("cumulative_distance_m")
    ])

    # Corrected by run_up_distance_m
    df = df.with_columns([
        (pl.col("cumulative_distance_m") - pl.col("run_up_distance_m")).alias("cum_race_distance_m")
    ])

    # Calculate speed in km/h
    # Speed = Distance / Time * 3.6 (to convert m/s to km/h)

    df = df.with_columns([
        pl.when(pl.col("is_first_obs"))
        .then(0.0)
        .when(
            (pl.col("distance_m") > 0) & 
            (pl.col("time_seconds") - pl.col("prev_time_seconds") > 0)
        ).then(
            (pl.col("distance_m") / (pl.col("time_seconds") - pl.col("prev_time_seconds"))) * 3.6
        ).otherwise(None).alias("speed_kmh")
    ])

    # start and end of race AQU_2019-01-01_1_1
    print("Verify distance and speed calculations:")
    print("Start of race:")
    print(df.select(["horse_pk", "trakus_index", "time_seconds", "distance_m", "speed_kmh", "cum_race_distance_m"]).head(10))

    
    print("End of race:")
    print(f"{df.filter(pl.col("horse_pk") == "AQU_2019-01-01_1_1").select(["horse_pk","trakus_index", "time_seconds", "distance_m", "speed_kmh", "cum_race_distance_m"]).tail(10)}")

    print("Compare with original distance_id:")


    ##########################################
    # Race Progress per horse per race
    ##########################################

    # by covered distance (race progress)
    df = df.with_columns([
        pl.col("cum_race_distance_m")
        .rank("dense", descending=True)
        .over(["rid", "trakus_index"])
        .alias("position_rank")
    ])

    print(
        df.filter(pl.col("rid") == "AQU_2019-01-01_1")
        .select(["trakus_index", "horse_pk", "distance_id_m", "cumulative_distance_m", "position_rank", "cum_race_distance_m"])
        .sort(["trakus_index", "position_rank"])
    )
    print("Sample ranking at different time points:")
    sample_race = df.filter(pl.col("rid") == "AQU_2019-01-01_1")
    for time_point in [10, 50, 100]:
        print(f"\nAt trakus_index {time_point}:")
        print(
            sample_race
            .filter(pl.col("trakus_index") == time_point)
            .select(["horse_pk", "cum_race_distance_m", "position_rank"])
            .sort("position_rank")
        )

    ##########################################
    # Relative Rank per Horse per Race at each timestep
    ##########################################

    #TODO: calculate each horse's relative position at each race point


    #TODO: Log statistics after preporcessing (number of rows, horses)

    print(f"Final shape of {df.shape[0]} rows and {df.shape[1]} columns")


    return df

##########################################
# TODO: FILTERED SUBSET WITH ONLY TOP 3 RACE DISTANCES FOR STRATEGY PAGE
##########################################


##########################################
# Save to processed folder
##########################################

def store_processed_df(df):
    """
    Store cleaned and processed dataframe in subdirectory. If already exists overwrite last file.
    """
    processed_file_name = os.path.join(processed_data_dir, "df_clean.parquet")

    # if processed dir does not exist generate
    if not os.path.exists(processed_data_dir):
        os.makedirs(processed_data_dir)

    df.write_parquet(processed_file_name)

def parquet_to_sqlite(df, db_path):
    """
    Store polars cleaned and processed dataframe as sqlite file in subdirectory. If already exists overwrite last file.
    """

    # if processed dir does not exist generate
    if not os.path.exists(processed_data_dir):
        os.makedirs(processed_data_dir)

    # connect to sqlite db
    conn = sqlite3.connect(db_path)
    
    try:
        # convert polars to pandas for sqlite compatibility
        df_pandas = df.to_pandas()
        
        # write to sqlite table
        df_pandas.to_sql('horse_racing_data', conn, if_exists='replace', index=False)
        
        print(f"Successfully saved {len(df_pandas)} rows to SQLite database at {db_path}")
        
    except Exception as e:
        print(f"Error saving to SQLite: {e}")
    finally:
        conn.close()


# TEST

if __name__ == "__main__":
    df = load_data(main_file_path, horse_global_ids, horse_names)

    # save as parquet
    store_processed_df(df)
    
    # # save as sqlite database for LLM agents
    sqlite_db_path = os.path.join(processed_data_dir, "horse_racing_data.db")
    parquet_to_sqlite(df, sqlite_db_path)