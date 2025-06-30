import os
import sys
import streamlit as st
import polars as pl
import pathlib
import plotly.express as px
import plotly.io as pio
import datetime
import plotly.graph_objects as go


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



# Convert race_date to datetime.date
date_options = (
    df_track
    .select("race_date")
    .drop_nulls()
    .unique()
    .to_series()
    .str.strptime(pl.Date, "%Y-%m-%d")  # or the correct format for your data
    .sort()
    .to_list()
)

default_date = date_options[-1]

selected_date = st.sidebar.date_input(
    "Select Date",
    value=default_date,
    min_value=min(date_options),
    max_value=max(date_options)
)

df_date = df_track.filter(pl.col("race_date") == selected_date.strftime("%Y-%m-%d"))

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

# Convert once to Pandas
df_race_pandas = df_race.to_pandas()

# Set lat/lon bounds
x_min, x_max = df_race_pandas["longitude"].min(), df_race_pandas["longitude"].max()
y_min, y_max = df_race_pandas["latitude"].min(), df_race_pandas["latitude"].max()

import plotly.graph_objects as go
import plotly.express as px

# Set up the animation frames with trails
frames = []
horse_ids = df_race_pandas["horse_pk"].unique()
trakus_steps = sorted(df_race_pandas["trakus_index"].unique())

horse_ids = df_race_pandas["horse_pk"].unique()

# Use a palette that is guaranteed to contain hex codes
color_palette = px.colors.qualitative.Plotly
hex_colors = [c for c in color_palette if c.startswith("#")]

if not hex_colors:
    raise ValueError("Selected color palette contains no hex colors.")

colors = (hex_colors * ((len(horse_ids) // len(hex_colors)) + 1))[:len(horse_ids)]

horse_colors = {
    horse: px.colors.hex_to_rgb(color)
    for horse, color in zip(horse_ids, colors)
}
# Filter palette to HEX colors only
hex_colors = [c for c in color_palette if c.startswith("#")]

# Repeat to match number of horses
colors = (hex_colors * ((len(horse_ids) // len(hex_colors)) + 1))[:len(horse_ids)]

# Convert hex to RGB tuples
horse_colors = {
    horse: px.colors.hex_to_rgb(color)
    for horse, color in zip(horse_ids, colors)
}

# Step 2: Build animation frames
frames = []

for t in sorted(df_race_pandas["trakus_index"].unique()):
    frame_data = []

    for horse in horse_ids:
        df_horse = df_race_pandas[df_race_pandas["horse_pk"] == horse]
        df_up_to_t = df_horse[df_horse["trakus_index"] <= t]

        if df_up_to_t.empty:
            continue

        # Get RGB color for this horse
        rgb = horse_colors[horse]
        rgba_trail = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.3)"   # transparent
        rgba_dot = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 1.0)"     # opaque

        # Trail line
        frame_data.append(go.Scattermapbox(
            lat=df_up_to_t["latitude"],
            lon=df_up_to_t["longitude"],
            mode="lines",
            line=dict(width=2, color=rgba_trail),
            name=horse,
            showlegend=False
        ))

        # Current dot
        current_point = df_up_to_t.iloc[-1]
        frame_data.append(go.Scattermapbox(
            lat=[current_point["latitude"]],
            lon=[current_point["longitude"]],
            mode="markers",
            marker=dict(size=8, color=rgba_dot),
            name=horse,
            showlegend=False
        ))

    frames.append(go.Frame(data=frame_data, name=str(t)))

# Initial frame
initial_data = frames[0].data

# Final animated map with trails
fig_trails = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title=f"Race Progress with Trails for {selected_race}",
        mapbox=dict(
            style="carto-positron",
            zoom=15,
            center=dict(
                lat=df_race_pandas["latitude"].mean(),
                lon=df_race_pandas["longitude"].mean()
            )
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 100, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 0}
                    }]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0}, "mode": "immediate", "transition": {"duration": 0}}]
                }
            ]
        }]
    ),
    frames=frames
)

# Display it
st.plotly_chart(fig_trails, use_container_width=True)


