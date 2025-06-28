import os
import streamlit as st
import polars as pl
import pathlib
from dotenv import load_dotenv
import sys

st.set_page_config(page_title="Home", layout="wide")

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.track_statistics import calculate_track_summary_stats_landingpage



# Custom CSS for clean white theme and style guide
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        background-color: #F9F7F1;
        color: #014421;
        font-family: 'Lato', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #014421;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.2em;
        margin-bottom: 0.5em;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: #014421;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1.5rem;
        margin: 0.5rem 0;
        font-family: 'Lato', sans-serif;
    }
    .stButton>button:hover {
        background-color: #014421;
        color: #D4AF37;
    }
    .card {
        background: #fff;
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(1,68,33,0.08);
        color: #014421;
        font-family: 'Lato', sans-serif;
    }
    .footer {
        left: 0;
        bottom: 0;
        width: 100%;
        background: #F9F7F1;
        color: #8B4513;
        text-align: center;
        padding: 0.5rem 0;
        font-size: 0.9rem;
        z-index: 100;
        border-top: 2px solid #D4AF37;
    }
    .sidebar-title {
        color: #D4AF37;
        font-family: 'Playfair Display', serif;
        font-size: 1.3em;
        margin-bottom: 0.5em;
        display: flex;
        align-items: center;
        gap: 0.5em;
    }
    .gold-icon {
        color: #D4AF37;
        font-size: 1.2em;
        margin-right: 0.3em;
    }
    </style>
''', unsafe_allow_html=True)


# Sidebar filters with gold icons and titles
with st.sidebar:
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>📅</span> Date</div>", unsafe_allow_html=True)
    st.date_input("", key="date_input_home")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>🏟️</span> Racecourse</div>", unsafe_allow_html=True)
    st.selectbox("", ["Saratoga", "Belmont", "Aqueduct"], key="racecourse_input_home")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>🐴</span> Horse</div>", unsafe_allow_html=True)
    st.text_input("", key="horse_input_home")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>👨‍✈️</span> Jockey</div>", unsafe_allow_html=True)
    st.text_input("", key="jockey_input_home")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>💰</span> Odds Range</div>", unsafe_allow_html=True)
    st.slider("", 1.0, 100.0, (1.0, 20.0), key="odds_input_home")
    st.markdown("---")
    st.markdown("<span style='color:#D4AF37;'>Use filters to refine your analysis.</span>", unsafe_allow_html=True)

# Main panel content (dummy)
st.markdown("## Welcome to the Home Page")
st.info("This page will provide an overview of key metrics and visualizations.")



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




