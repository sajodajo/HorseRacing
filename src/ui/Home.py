import streamlit as st
import polars as pl
import pathlib
import sys

st.set_page_config(page_title="Home", layout="wide")

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.track_statistics import calculate_track_summary_stats_landingpage


# Load the logo
logo_path = "src/assets/ie_logo.png"
st.logo(
    logo_path,
    size="large",
)


# Hide the streamlit upper-right chrome
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

# Inject custom CSS for styling
st.markdown(
    """
    <style>
    /* Set primary colors */
    :root {
        --primary-green: #75C200;
        --primary-blue: #000066;
        --accent-blue: #47BFFF;
    }

    /* General body styling */
    body {
        font-family: 'Arial', sans-serif;
        background-color: var(--primary-blue);
        color: white;
    }

    /* Style links without underlining */
    a {
        color: var(--accent-blue);
        text-decoration: none;
    }
    a:hover {
        color: var(--primary-green);
        text-decoration: underline;
    }

    /* Style headers */
    h1, h2, h3 {
        color: var(--primary-green);
    }

    /* Style buttons */
    .stButton>button {
        background-color: var(--primary-green);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: var(--accent-blue);
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Welcome to the Horse Racing Strategy App")   
st.caption("MBD - Sports Analytics | Vandad Vafai, Joaquin Miño, Marius Gnoth, Sam Jones, Maine Isasi")


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


@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent # src/
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    return pl.scan_parquet(str(parquet_path))

df = load_preprocessed_df().collect()

# one column per track with some key statistics
st.markdown("### Available Tracks")

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

with col1: display_track_metrics("Saratoga Race Course", sar_stats)
with col2: display_track_metrics("Belmont Park", bel_stats)
with col3: display_track_metrics("Aqueduct Racetrack", aqu_stats)






