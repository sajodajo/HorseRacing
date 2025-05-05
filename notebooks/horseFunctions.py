import pandas as pd
import numpy as np
import streamlit as st
import polars as pl

@st.cache_data
def loadData(main_file_path,horse_global_ids,horse_names):
    df = pd.read_parquet(main_file_path)

    df_horse_ids = pd.read_csv(horse_global_ids, 
                            header=0,
                            index_col=0)
                            
    df_horse_names = pd.read_csv(horse_names,
                                header=0,
                                index_col=0)

    df.columns = ['track_id','race_date','race_number','program_number','trakus_index','latitude','longitude','distance_id','course_type','track_condition','run_up_distance','race_type','purse','post_time','weight_carried','jockey','odds','position_at_finish']

    df["program_number"] = df["program_number"].apply(lambda x: str(x).rstrip())

    df["horse_pk"] = df.apply(lambda x: f"{x["track_id"]}_{x["race_date"]}_{x["race_number"]}_{x["program_number"]}", axis=1)

    df["win"] = np.where(df["position_at_finish"] == 1, 1, 0)

    df["rid"] = df.apply(lambda x: f"{x["track_id"]}_{x["race_date"]}_{x["race_number"]}", axis=1)

    df_horse_ids["horse_pk"] = df_horse_ids.apply(lambda x: f"{x["track_id"]}_{x["race_date"]}_{x["race"]}_{x["program_number"]}", axis=1)

    df_horse_ids["horse_id"] = df_horse_ids["horse_id"].astype(str).str.rstrip()

    df = df.merge(df_horse_ids[["horse_pk", "horse_id"]], on="horse_pk", how="left")

    df_horse_names["horse_id"] = df_horse_names["horse_id"].astype(str).str.rstrip()

    df = df.merge(df_horse_names[["horse_id","horse_name"]], on="horse_id", how="left")

    return df




def loadDataPolars(main_file_path, horse_global_ids, horse_names):
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

    df = df.with_columns([
        pl.col("program_number").cast(pl.Utf8).str.strip_chars(),
        (pl.col("position_at_finish") == 1).cast(pl.Int8).alias("win")
    ])

    df = df.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8) + "_" +
         pl.col("program_number")).alias("horse_pk"),
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race_number").cast(pl.Utf8)).alias("rid")
    ])

    df_horse_ids = df_horse_ids.with_columns([
        (pl.col("track_id").cast(pl.Utf8) + "_" +
         pl.col("race_date").cast(pl.Utf8) + "_" +
         pl.col("race").cast(pl.Utf8) + "_" +
         pl.col("program_number").cast(pl.Utf8)).alias("horse_pk"),
        pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    df = df.join(df_horse_ids.select(["horse_pk", "horse_id"]), on="horse_pk", how="left")

    df_horse_names = df_horse_names.with_columns([
        pl.col("horse_id").cast(pl.Utf8).str.strip_chars()
    ])

    df = df.join(df_horse_names.select(["horse_id", "horse_name"]), on="horse_id", how="left")

    return df