import streamlit as st
import polars as pl
import pathlib
import sys

st.set_page_config(
    page_title="FinalFurlong: Home",
    page_icon='src/assets/LogoSmall.png',
    layout = 'wide'
)


# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.track_statistics import calculate_track_summary_stats_landingpage


col1, col2, col3,col4, col5  = st.columns([1,1, 0.5,1, 1])
with col3:
    st.image('src/assets/NYRAlogo.png')

st.html(
    """
    <style>
    [data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
    </style>
    """,
)


st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #da113d; font-size: 80px; margin-top: -30px; margin-bottom: -20px;">FinalFurlong</h1>
        <h2 style="font-size: 40px; color: #0c1c44; margin-top: 0px; margin-bottom: -10px;">The AI-Powered Horse Racing Strategy App</h2>
        <h3 style="font-size: 20px; color: grey; margin-top: 0px;">by Vandad Vafai, Joaquin Miño, Marius Gnoth, Sam Jones & Maine Isasi</h3>
    </div>
""", unsafe_allow_html=True)


st.markdown("""
    <div style="
        margin-top: 40px;
        margin-bottom: 40px;
        color: grey;
        font-size: 28px;
        max-width: 1700px;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
        line-height: 1.6;
    ">
        FinalFurlong is a multi-tool application designed to enhance the horse racing experience for fans, analysts, and professionals alike.
        It combines advanced data analytics, AI-driven insights, and interactive visualizations to provide a comprehensive platform for understanding
        and strategizing in the world of horse racing. The app is divided into four main tools, each tailored to specific aspects of the sport:
    </div>
""", unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4, border=True)

with col1:
    st.markdown("""
        <div style="text-align: center;">
            <h3 style="color: #da113d;">🏇 Race Analysis Dashboard</h3>
            <p style="text-align: center; font-size: 20px;">
                Explore past races in a dynamic, interactive format. The Race Analysis Dashboard brings archived data to life, 
                allowing users to track each horse’s movement, pace, and positioning throughout the race. 
                It’s designed to help identify patterns in performance, understand race dynamics, and reveal how critical decisions 
                impacted outcomes — all in a clear, visual context.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="text-align: center;">
            <h3 style="color: #da113d;">🏁 Competitor Analysis Tool</h3>
            <p style="text-align: center; font-size: 20px;">
                Gain a competitive edge with detailed profiles of rival horses, jockeys, and trainers. 
                The Competitor Analysis Tool surfaces key insights like historical performance trends, 
                preferred track conditions, typical running styles, and head-to-head matchups. 
                Whether for strategy planning or betting insight, this tool helps you know your competition inside and out.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style="text-align: center;">
            <h3 style="color: #da113d;">🗺️ Track Strategy Tool</h3>
            <p style="text-align: center; font-size: 20px;">
                Every track has its own quirks — and this tool decodes them. 
                The Track Strategy Tool analyzes historical outcomes, gate biases, course layouts, and surface types 
                to deliver tailored strategic recommendations. It’s built to help jockeys, trainers, and analysts 
                optimize tactics for specific tracks under specific conditions.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div style="text-align: center;">
            <h3 style="color: #da113d;">🔮 AI Assistant</h3>
            <p style="text-align: center; font-size: 20px;">
                Let the AI do the heavy lifting. This intelligent assistant integrates data from past races, 
                track conditions, competitor stats, and horse profiles to offer real-time strategic suggestions. 
                Whether you’re deciding on race pace, positioning, or tactical adjustments, 
                the AI Assistant provides actionable insights — fast, adaptive, and context-aware.
            </p>
        </div>
    """, unsafe_allow_html=True)






@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent # src/
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    return pl.scan_parquet(str(parquet_path))

df = load_preprocessed_df().collect()

# one column per track with some key statistics
st.markdown("""
    <h3 style="color: #da113d;">FinalFurlong Data Overview</h3>
""", unsafe_allow_html=True)

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

def display_track_metrics(track_name, stats):
    st.markdown(f"### {track_name}")
    st.metric("Number of Races", stats["num_races"])
    st.metric("Race Dates", stats["num_dates"])
    st.metric("Unique Horses", stats["num_horses"])
    st.metric("Unique Jockeys", stats["num_jockeys"])



with col1:
    display_track_metrics("Aqueduct Racetrack", aqu_stats)

with col2:
    display_track_metrics("Belmont Park", bel_stats)

with col3:
    display_track_metrics("Saratoga Race Course", sar_stats)






