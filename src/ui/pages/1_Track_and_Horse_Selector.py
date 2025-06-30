import os
import sys
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
df_track = df.filter(pl.col("track_id") == selected_track)

# Date selection
date_options = df_track.select("race_date").drop_nulls().unique().to_series().sort().to_list()
selected_date = st.sidebar.selectbox(
    "Select Date",
    options=date_options
)
df_date = df_track.filter(pl.col("race_date") == selected_date)

# Course type selection
course_type_options = df_date.select("course_type").drop_nulls().unique().to_series().sort().to_list()
selected_course_type = st.sidebar.selectbox(
    "Select Course Type",
    options=course_type_options
)
df_course_type = df_date.filter(pl.col("course_type") == selected_course_type)

# Race selection
race_options = df_course_type.select("rid").drop_nulls().unique().to_series().sort().to_list()
selected_race = st.sidebar.selectbox(
    "Select Race",
    options=race_options
)
df_race = df_course_type.filter(pl.col("rid") == selected_race)


# Display key race information
st.markdown("### Race Information")
num_horses = df_race.select(pl.col("horse_pk").n_unique())[0, 0]
st.write(f"**Number of Horses in Race:** {num_horses}")

# Odds per horse
odds_per_horse = df_race.select(["horse_pk", "horse_name", "jockey", "implied_win_probability"]).unique().sort("implied_win_probability")
st.write("**Winning Probability per Horse:**")
st.dataframe(odds_per_horse.to_pandas())

# Winner horse
winner = df_race.filter(pl.col("position_at_finish") == 1).select(["horse_name", "jockey"]).to_pandas()
if not winner.empty:
    st.write(f"**Winner Horse and Jockey:** {winner.iloc[0]['horse_name']} (Jockey: {winner.iloc[0]['jockey']})")
else:
    st.write("**Winner Horse and Jockey:** Not available")

# Visualize race progress
st.markdown("### Race Progress Visualization")

# Calculate fixed axis ranges for the map visualization
x_min, x_max = df_race.select(
    pl.col("longitude").min().alias("x_min"),
    pl.col("longitude").max().alias("x_max")
).row(0)

y_min, y_max = df_race.select(
    pl.col("latitude").min().alias("y_min"),
    pl.col("latitude").max().alias("y_max")
).row(0)

# 1. Animated Scatter Plot: Race Progress on the Map
fig_map = px.scatter(
    df_race.to_pandas(),
    x="longitude",
    y="latitude",
    animation_frame="trakus_index",
    animation_group="horse_pk",
    color="speed_kmh",
    color_continuous_scale="hot",
    hover_data=["horse_pk", "speed_kmh", "cum_race_distance_m"],
    title=f"Race Progress for {selected_race}"
)

# Set fixed axis ranges
fig_map.update_layout(
    xaxis=dict(range=[x_min, x_max]),
    yaxis=dict(range=[y_min, y_max])
)

st.plotly_chart(fig_map, use_container_width=True)

df_race_pandas = df_race.to_pandas()


df_race_pandas = df_race.to_pandas()

# 2. Scatter Plot: Speed Over Time
fig_speed = px.line(
    df_race_pandas,
    x="trakus_index",
    y="speed_kmh",
    color="horse_name",
    title="Horse Speed Over Time",
    labels={"trakus_index": "Time (Trakus Index)", "speed_kmh": "Speed (km/h)"},
    hover_data=["cum_race_distance_m", "position_rank"]
)
st.plotly_chart(fig_speed, use_container_width=True)


# 3. Line Chart: Position Rank Over Time
fig_position = px.line(
    df_race_pandas,
    x="trakus_index",
    y="position_rank",
    color="horse_name",
    title="Horse Position Over Time",
    labels={"trakus_index": "Time (Trakus Index)", "position_rank": "Position Rank"},
    hover_data=["cum_race_distance_m", "speed_kmh"]
)
fig_position.update_layout(
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig_position, use_container_width=True)