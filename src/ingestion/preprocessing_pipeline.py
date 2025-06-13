import pandas as pd
import numpy as np
import streamlit as st
import polars as pl
import os
from datetime import datetime, timedelta

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

##########################################
# Preprocessing for Data Explorer
##########################################

def load_data(main_file_path, horse_global_ids, horse_names):

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

    #TODO: FILTER OUT EDGE CASES, FOCUS ON RACE TYPES, NULLS etc.

    # binary winner flag

    df = df.with_columns([
        pl.col("program_number").cast(pl.Utf8).str.strip_chars(),
        (pl.col("position_at_finish") == 1).cast(pl.Int8).alias("win")
    ])

    # trackus_index = 0.25 sec

    df = df.with_columns([
        (pl.col("trakus_index") * 0.25).alias("time_seconds")
    ])

    # create unique identifiers

    # identify unique horse per track, race, program_number

    df = df.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8) + "_" +
         pl.col("program_number")).alias("horse_pk"),
         # race id (pk)
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8)).alias("rid")
    ])

    print(f"Unique horses: {df['horse_pk'].n_unique()}")

    # same for supplementary dataset

    df_horse_ids = df_horse_ids.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race").cast(pl.Utf8) + "_" +
         pl.col("program_number").cast(pl.Utf8)).alias("horse_pk"),
        pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    # join id dataset and supplementary dataset

    df = df.join(df_horse_ids.select(["horse_pk", "horse_id"]), on="horse_pk", how="left")

    df_horse_names = df_horse_names.with_columns([
        pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    df = df.join(df_horse_names.select(["horse_id", "horse_name"]), on="horse_id", how="left")

    # calculate speed and distance features

    df = df.sort(["horse_pk", "trakus_index"])

    def haversine_distance(lat1, lon1, lat2, lon2):
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Radius of earth in km
        return c * r

    
    df = df.with_columns(
        pl.col("latitude").shift(1).over("horse_pk").alias("prev_latitude"),
        pl.col("longitude").shift(1).over("horse_pk").alias("prev_longitude"),
        pl.col("time_seconds").shift(1).over("horse_pk").alias("prev_time_seconds")
        )

    df = df.with_columns(
        pl.when(
            (pl.col("prev_latitude").is_not_null()) & 
            (pl.col("horse_pk") == pl.col("horse_pk").shift(1))
        ).then(
            haversine_distance(
                pl.col("prev_latitude"),
                pl.col("prev_longitude"),
                pl.col("latitude"),
                pl.col("longitude")
            )
        ).otherwise(0).alias("distance_meters")
    )

    # speed in km/h

    df = df.with_columns(
        pl.when(
            (pl.col("distance_meters") > 0) & 
            (pl.col("time_seconds") - pl.col("prev_time_seconds") > 0)
        ).then(
            (pl.col("distance_meters") / (pl.col("time_seconds") - pl.col("prev_time_seconds"))) * 3.6
        ).otherwise(None).alias("speed_kmh")
    )

    # race progress percentage
    # per horse per race cumsum of trakus_index / max trakus_index
    # TODO: FIX, USING TRACKUS INDEX DOESNT MAKE SENSE BECAUSE IT RELATES TO TIME NOT DISTANCE
    df = df.with_columns(
        (
            (
                pl.col("trakus_index").cum_sum().over("horse_pk") / pl.col("trakus_index").max().over("horse_pk")
            ).alias("race_progress")
        )    
    )   

    print(df.select(["horse_pk", "trakus_index", "race_progress"]).head(20))

    #TODO: FINISH LINE TRUNCATION: REMOVE ALL ROWS OF HORSE AFTER PASSES FINISH LINE

    # categorize into 4 race stages
    #TODO: MAYBE ONLY IN SUBSET 

    df = df.with_columns(
        pl.when(
            pl.col.race_progress < 25
        ).then(
            pl.lit("stage1")
        ).when(
            pl.col.race_progress <= 50
        ).then(
            pl.lit("stage2")
        ).when(
            pl.col.race_progress <= 75
        ).then(
            pl.lit("stage3")
        ).when(
            pl.col.race_progress <= 100
        ).then(
            pl.lit("stage4")
        ).otherwise(
            pl.lit("other")
        ).alias("race_stage")
    )


    #TODO: calculate each horse's relative position at each race point using race_progress


    #TODO: CHECK FOR ANY CODE IN EDA NOTEBOOKS TO IMPLEMENT HERE




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


# TEST

if __name__ == "__main__":
    df = load_data(main_file_path, horse_global_ids, horse_names)
    print(df.head())

    # feature test
    # print(df.select(["horse_pk", "trakus_index", "race_progress"]).head())


    store_processed_df(df)