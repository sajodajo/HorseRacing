import os
import streamlit as st
import polars as pl
import pathlib
from dotenv import load_dotenv
import sys

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.track_statistics import calculate_track_summary_stats_landingpage

load_dotenv()

st.set_page_config(
    page_title="Big Data Derby App",
    page_icon="🏇",
    layout="wide"
)

# Title
st.title("Horse Racing Data Explorer")

@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent # src/
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    return pl.scan_parquet(str(parquet_path))

df = load_preprocessed_df().collect()

# one column per track with some key statistics
st.markdown("## Available Tracks")

col1, col2, col3 = st.columns(3, border=True)

# Get summary stats
stats = calculate_track_summary_stats_landingpage()

# Helper function to filter stats for a given track
def get_track_stats(df, track_code):
    # Filter for the specific track
    track_df = df.filter(pl.col("track_id") == track_code)
    num_races = track_df["rid"].n_unique() if "rid" in track_df.columns else track_df.select([pl.col("track_id"), pl.col("race_date"), pl.col("race_number")]).unique().height
    num_dates = track_df["race_date"].n_unique()
    num_horses = track_df["horse_id"].n_unique() if "horse_id" in track_df.columns else track_df["program_number"].n_unique()
    num_jockeys = track_df["jockey"].n_unique() if "jockey" in track_df.columns else None
    race_types = track_df.select([pl.col("race_type"), pl.col("distance_id")]).unique().to_dict(as_series=False) if "race_type" in track_df.columns and "distance_id" in track_df.columns else {}
    return {
        "num_races": num_races,
        "num_dates": num_dates,
        "num_horses": num_horses,
        "num_jockeys": num_jockeys,
        "race_types": race_types
    }

sar_stats = get_track_stats(df, "SAR")
bel_stats = get_track_stats(df, "BEL")
aqu_stats = get_track_stats(df, "AQU")

with col1:
    with st.container():
        st.markdown("### Saratoga Race Course")
        st.metric("Number of Races", sar_stats["num_races"])
        st.metric("Race Dates", sar_stats["num_dates"])
        st.metric("Unique Horses", sar_stats["num_horses"])
        st.metric("Unique Jockeys", sar_stats["num_jockeys"])
        # st.markdown("**Race Types & Lengths:**")
        # st.write(sar_stats["race_types"])

with col2:
    with st.container():
        st.markdown("### Belmont Park")
        st.metric("Number of Races", bel_stats["num_races"])
        st.metric("Race Dates", bel_stats["num_dates"])
        st.metric("Unique Horses", bel_stats["num_horses"])
        st.metric("Unique Jockeys", bel_stats["num_jockeys"])
        # st.markdown("**Race Types & Lengths:**")
        # st.write(bel_stats["race_types"])

with col3:
    with st.container():
        st.markdown("### Aqueduct Racetrack")
        st.metric("Number of Races", aqu_stats["num_races"])
        st.metric("Race Dates", aqu_stats["num_dates"])
        st.metric("Unique Horses", aqu_stats["num_horses"])
        st.metric("Unique Jockeys", aqu_stats["num_jockeys"])
        # st.markdown("**Race Types & Lengths:**")
        # st.write(aqu_stats["race_types"])




