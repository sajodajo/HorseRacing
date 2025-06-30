import os
import sys
import streamlit as st
import polars as pl
import pathlib
import plotly.express as px

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image('src/assets/NYRAlogo.png')

    
st.markdown("# Track and Race Selector")

@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent 
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    return pl.scan_parquet(str(parquet_path))

df = load_preprocessed_df().collect()

tab1, tab2 = st.tabs(["Race Analysis", "Performance History"])

# Track selection
selected_track = st.sidebar.selectbox(
    "Select Track",
    options=df.select("track_id").drop_nulls().unique().to_series().sort().to_list()
)

# Filter by selected track
df_track = df.filter(pl.col("track_id") == selected_track)

# Date selection
date_options = df_track.select("race_date").drop_nulls().unique().to_series().sort().to_list()
selected_date = st.sidebar.selectbox(
    "Select Date",
    options=date_options
)

# Filter by selected date
df_date = df_track.filter(pl.col("race_date") == selected_date)

# Race selection
race_options = df_date.select("rid").drop_nulls().unique().to_series().sort().to_list()
selected_race = st.sidebar.selectbox(
    "Select Race",
    options=race_options
)

# Filter by selected race
df_race = df_date.filter(pl.col("rid") == selected_race)

# Course type selection
course_type_options = df_race.select("course_type").drop_nulls().unique().to_series().sort().to_list()
selected_course_type = st.sidebar.selectbox(
    "Select Course Type",
    options=course_type_options
)

# Filter by selected course type
df_course_type = df_race.filter(pl.col("course_type") == selected_course_type)

# Horse selection
horse_options = df_course_type.select(["horse_pk", "horse_name"]).unique().sort("horse_name")
horse_names = horse_options.select("horse_name").to_series().to_list()
selected_horse_name = st.sidebar.selectbox(
    "Select Horse",
    options=horse_names
)

# Filter by selected horse
selected_horse_pk = horse_options.filter(pl.col("horse_name") == selected_horse_name).select("horse_pk")[0, 0]
horse_df = df_course_type.filter(pl.col("horse_pk") == selected_horse_pk)

# Display filtered data
st.write(horse_df.head())

# df with selected columns

# horse_df = horse_df.select([
# ["jockey", "horse_name", "race_date", "odds", "win", ]
# Show race info of selected horse
fig = px.scatter(
    horse_df,
    x="longitude",
    y="latitude",
    color="trakus_index",
    hover_data=["race_date", "horse_name", "jockey", "odds", "position_at_finish"],
    color_continuous_scale="greens"
)

st.plotly_chart(fig, use_container_width=True)