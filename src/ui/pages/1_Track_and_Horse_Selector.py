import os
import sys
import streamlit as st
import polars as pl
import pathlib
import plotly.express as px
import pydeck as pdk

st.set_page_config(
    page_title="Track and Race Selector",
    layout="wide",
)

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
st.markdown("### Race Lineup")

# Odds per horse
odds_per_horse = df_race.select(["horse_pk", "horse_name", "jockey", "odds_to_one", "implied_win_probability"]).unique().sort("implied_win_probability", descending=True)
st.dataframe(odds_per_horse.to_pandas())
# Winner horse
winner = df_race.filter(pl.col("position_at_finish") == 1).select(["horse_name", "jockey"]).to_pandas()
if not winner.empty:
    st.write(f"**Winner Horse:** {winner.iloc[0]['horse_name']} (Jockey: {winner.iloc[0]['jockey']})")
else:
    st.write("**Winner Horse:** Not available")



# Visualize race progress
st.markdown("### Race Replay")

# Calculate fixed axis ranges for the map visualization
x_min, x_max = df_race.select(
    pl.col("longitude").min().alias("x_min"),
    pl.col("longitude").max().alias("x_max")
).row(0)

y_min, y_max = df_race.select(
    pl.col("latitude").min().alias("y_min"),
    pl.col("latitude").max().alias("y_max")
).row(0)

# Convert to pandas once at the beginning
df_race_pandas = df_race.to_pandas()

col1, col2 = st.columns([1, 2])

# Create color mapping for horses
unique_horses = df_race_pandas['horse_pk'].unique()
colors = px.colors.qualitative.Set1[:len(unique_horses)]
color_map = dict(zip(unique_horses, colors))

# Add RGB color column for pydeck
def color_to_rgb(color):
    """Convert color (hex or CSS name) to RGB list for pydeck"""
    import matplotlib.colors as mcolors

    # Ensure the color is in a valid format for matplotlib
    if color.startswith("rgb"):
        # Convert 'rgb(r, g, b)' to a tuple of integers
        color = color.replace("rgb(", "").replace(")", "").split(",")
        rgb_tuple = tuple(int(c) / 255 for c in color)  # Normalize to 0-1 range
    else:
        # Convert named or hex color to RGB tuple
        rgb_tuple = mcolors.to_rgb(color)

    # Convert to 0-255 scale and add alpha
    return [int(rgb_tuple[0] * 255), int(rgb_tuple[1] * 255), int(rgb_tuple[2] * 255), 255]

df_race_pandas['color'] = df_race_pandas['horse_pk'].map(
    lambda x: color_to_rgb(color_map[x])
)
with col1:
    st.markdown("#### Static")

    df_paths = (
        df_race_pandas.groupby("horse_pk", group_keys=False)
        .apply(lambda x: x[["longitude", "latitude"]].values.tolist())
        .reset_index(name="path")
    )

    # Add a color column for each horse
    df_paths["color"] = df_paths["horse_pk"].map(lambda x: color_map[x]).apply(color_to_rgb)

    # Define the PathLayer
    path_layer = pdk.Layer(
        type="PathLayer",
        data=df_paths,
        pickable=True,
        get_path="path",
        get_color="color",
        width_scale=0.1,
        width_min_pixels=3,
        get_width=10,
        opacity=0.5
    )

    # Define the view state
    view_state = pdk.ViewState(
        latitude=df_race_pandas["latitude"].mean(),
        longitude=df_race_pandas["longitude"].mean(),
        zoom=15,
        pitch=0,
    )

    # Render the PathLayer
    st.pydeck_chart(
        pdk.Deck(
            layers=[path_layer],
            initial_view_state=view_state,
            tooltip={"text": "Horse: {horse_pk}"},
        )
    )

with col2:
    st.markdown("#### Animated Map")

    # Animated Scatter Plot: Race Progress on the Map
    fig_map = px.scatter(
        df_race_pandas,
        x="longitude",
        y="latitude",
        animation_frame="trakus_index",
        animation_group="horse_pk",
        color="horse_name",  # Color by horse name for better identification
        size="speed_kmh",    # Size represents speed
        size_max=15,
        hover_data={
            "horse_name": True,
            "speed_kmh": ":.1f",
            "cum_race_distance_m": ":.0f",
            "position_rank": True,
            "longitude": False,  # Hide coordinates in hover
            "latitude": False
        },
        labels={
            "longitude": "Longitude",
            "latitude": "Latitude",
            "speed_kmh": "Speed (km/h)"
        }
    )

    # Set fixed axis ranges and improve layout
    fig_map.update_layout(
        xaxis=dict(
            range=[x_min, x_max],
            title="Longitude"
        ),
        yaxis=dict(
            range=[y_min, y_max],
            title="Latitude"
        ),
        showlegend=True,
        height=600,
        # Ensure aspect ratio is maintained
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1
    )

    # Improve animation settings
    fig_map.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 100
    fig_map.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 50

    st.plotly_chart(fig_map, use_container_width=True)


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