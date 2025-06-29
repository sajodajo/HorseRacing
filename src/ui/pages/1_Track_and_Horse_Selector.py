import streamlit as st
import polars as pl
import pathlib
import plotly.express as px


st.set_page_config(
    page_title="Track and Race Selector",
    layout="wide",
)

st.markdown("# Track and Race Selector")


@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent # src/
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    return pl.scan_parquet(str(parquet_path))

df = load_preprocessed_df().collect()

tab1, tab2 = st.tabs(["Race Analysis", "Performance History"])


# Track selection
selected_track = st.sidebar.selectbox(
    "Select Track", 
    options=df.select("track_id").drop_nulls().unique().to_series().sort().to_list()
)
track_df = df.filter(pl.col("track_id") == selected_track)

selected_race = st.sidebar.selectbox(
    "Select Race", 
    options=track_df.select("rid").drop_nulls().unique().to_series().sort().to_list()
)
race_df = track_df.filter(pl.col("rid") == selected_race)
horse_options = race_df.select(["horse_pk", "horse_name"]).unique().sort("horse_name")
horse_names = horse_options.select("horse_name").to_series().to_list()
selected_horse_name = st.sidebar.selectbox(
    "Select Horse", 
    options=horse_names
)
selected_horse_pk = horse_options.filter(pl.col("horse_name") == selected_horse_name).select("horse_pk")[0, 0]
horse_df = race_df.filter(pl.col("horse_pk") == selected_horse_pk)

st.write(df.head())

# Show race info of selected rid
fig = px.scatter(
    horse_df,
    x="longitude",
    y="latitude",
    color="trakus_index",
    hover_data=["race_date", "horse_name", "jockey", "odds", "position_at_finish"],
    color_continuous_scale="greens"
)

st.plotly_chart(fig, use_container_width=True)