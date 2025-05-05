import streamlit as st
import polars as pl
import plotly.express as px
import horseFunctions as hf
import numpy as np
from datetime import date


# Title
st.title("Horse Racing Data Explorer")

main_file_path = r"../data/raw/nyra_2019_complete.parquet"
horse_global_ids = r"../data/raw/horse_ids.csv"
horse_names = r"../data/raw/horse_names.csv"


df = hf.loadDataPolars(main_file_path, horse_global_ids, horse_names)

selected_track = st.selectbox(
    "Select Track ID",
    options=sorted(df.select("track_id").drop_nulls().unique().to_series().to_list())
)
df_track = df.filter(pl.col("track_id") == selected_track)

available_dates = sorted(df_track.select("race_date").drop_nulls().unique().to_series().to_list())
selected_date = st.selectbox(
    "Select Race Date",
    options=available_dates
)
df_date = df_track.filter(pl.col("race_date") == selected_date)

available_races = sorted(df_date.select("race_number").drop_nulls().unique().to_series().to_list())
selected_race_number = st.selectbox(
    "Select Race Number",
    options=available_races
)
df_race = df_date.filter(pl.col("race_number") == selected_race_number)

available_horses = sorted(df_race.select("horse_name").drop_nulls().unique().to_series().to_list())
selected_horse = st.selectbox(
    "Select Horse Name",
    options=available_horses
)

final_selection = df_race.filter(pl.col("horse_name") == selected_horse)

st.write("Filtered Result:")
final_df_pd = final_selection.to_pandas()

fig = px.scatter(
    final_df_pd,
    x="longitude",
    y="latitude",
    color="trakus_index",
    hover_data=["race_date", "horse_name", "jockey", "odds", "position_at_finish"],
    color_continuous_scale="greens"
)

st.plotly_chart(fig, use_container_width=True)