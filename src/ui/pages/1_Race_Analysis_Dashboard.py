import os
import sys
import streamlit as st
import polars as pl
import pandas as pd
import pathlib
import plotly.express as px
import pydeck as pdk
import plotly.graph_objects as go
import plotly.io as pio
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Race Analysis Dashboard",
    page_icon='src/assets/LogoSmall.png',
    layout = 'wide'
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

col1, col2, col3,col4, col5  = st.columns([1,1, 2,1, 1])
with col3:
    st.image('src/assets/NYRAlogo.png')

st.markdown("# Race Analysis Dashboard")

@st.cache_data
def load_preprocessed_df():
    """Load preprocess file and use polars Lazyframe"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent 
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    # Only select columns needed for this page
    required_columns = [
        # Filtering columns
        "track_id",
        "distance_id",
        "race_date", 
        "course_type",
        "rid",
        
        # Display columns
        "horse_pk",
        "horse_name",
        "jockey",
        "odds_to_one",
        "implied_win_probability",
        "position_at_finish",
        
        # Visualization columns
        "longitude",
        "latitude", 
        "trakus_index",
        "speed_kmh",
        "cum_race_distance_m",
        "position_rank"
    ]
    
    return pl.scan_parquet(str(parquet_path)).select(required_columns)

df = load_preprocessed_df().collect()

# Track selection
selected_track = st.sidebar.selectbox(
    "Select Track",
    options=df.select("track_id").drop_nulls().unique().to_series().sort().to_list()
)
df_track = df.filter(pl.col("track_id") == selected_track)


# DISTANCE SELECTION

distance_options = df_track.select("distance_id").drop_nulls().unique().to_series().sort().to_list()
selected_distance = st.sidebar.selectbox(
    "Select Distance",
    options=distance_options
)
df_distance = df_track.filter(pl.col("distance_id") == selected_distance)

# Date selection
date_options = df_distance.select("race_date").drop_nulls().unique().to_series().sort().to_list()
selected_date = st.sidebar.selectbox(
    "Select Date",
    options=date_options
)
df_date = df_distance.filter(pl.col("race_date") == selected_date)

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
st.markdown("### Starting Field & Odds")

# Odds per horse with finish position
odds_per_horse = df_race.select([
    "horse_pk", 
    "horse_name", 
    "jockey", 
    "odds_to_one", 
    "implied_win_probability",
    "position_at_finish"
]).unique().sort("implied_win_probability", descending=True)

odds_df = odds_per_horse.to_pandas()
odds_df = odds_df.rename(columns={
    'horse_name': 'Horse',
    'jockey': 'Jockey', 
    'odds_to_one': 'Odds',
    'implied_win_probability': 'Win Probability (%)',
    'position_at_finish': 'Finish Position'
})

# Format the display columns
odds_df['Win Probability (%)'] = (odds_df['Win Probability (%)'] * 100).round(1)
odds_df['Odds'] = odds_df['Odds'].apply(lambda x: f"{x:.1f}/1")

# Add status indicators
odds_df['Favorite'] = odds_df['Win Probability (%)'] == odds_df['Win Probability (%)'].max()
odds_df['Winner'] = odds_df['Finish Position'] == 1

# Create status column with both favorite and winner indicators
def get_status(row):
    if row['Winner']:
        return '🏆 WINNER'
    elif row['Favorite']:
        return '⭐ FAVORITE'
    else:
        return ''

odds_df['Status'] = odds_df.apply(get_status, axis=1)

odds_df['Finish Position'] = odds_df['Finish Position'].apply(
    lambda x: f"{int(x)}" if pd.notna(x) else "In Progress"
)

display_df = odds_df[['Horse', 'Jockey', 'Odds', 'Win Probability (%)', 'Finish Position', 'Status']]

def highlight_rows(row):
    if row['Status'] == '🏆 WINNER':
        return ['background-color: #90EE90; font-weight: bold; color: #006400'] * len(row)
    elif row['Status'] == '⭐ FAVORITE':
        return ['background-color: #FFD700; font-weight: bold; color: #8B4513'] * len(row)
    else:
        return [''] * len(row)

st.dataframe(
    display_df.style.apply(highlight_rows, axis=1),
    use_container_width=True,
    hide_index=True
)


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

# CREATE CONSISTENT COLOR MAPPING FOR ALL PLOTS
horse_ids = df_race_pandas["horse_pk"].unique()
horse_names = df_race_pandas["horse_name"].unique()

color_palette = px.colors.qualitative.Plotly
hex_colors = [c for c in color_palette if c.startswith("#")]

if not hex_colors:
    raise ValueError("Selected color palette contains no hex colors.")

colors = (hex_colors * ((len(horse_ids) // len(hex_colors)) + 1))[:len(horse_ids)]

# Create color mappings for both horse_pk and horse_name
horse_pk_colors = {horse: color for horse, color in zip(horse_ids, colors)}
horse_name_colors = {name: color for name, color in zip(horse_names, colors)}

horse_colors_rgb = {
    horse: px.colors.hex_to_rgb(color)
    for horse, color in zip(horse_ids, colors)
}

with col1:
    frames = []
    trakus_steps = sorted(df_race_pandas["trakus_index"].unique())

    frames = []

    for t in sorted(df_race_pandas["trakus_index"].unique()):
        frame_data = []

        for horse in horse_ids:
            df_horse = df_race_pandas[df_race_pandas["horse_pk"] == horse]
            df_up_to_t = df_horse[df_horse["trakus_index"] <= t]

            if df_up_to_t.empty:
                continue

            rgb = horse_colors_rgb[horse]
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

    initial_data = frames[0].data

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

    st.plotly_chart(fig_trails, use_container_width=True)

with col2:
    # 2. Speed Over Time 
    fig_speed = px.line(
        df_race_pandas,
        x="trakus_index",
        y="speed_kmh",
        color="horse_name",
        color_discrete_map=horse_name_colors,  
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
    color_discrete_map=horse_name_colors, 
    title="Position Rank Over Time",
    labels={"trakus_index": "Time (Trakus Index)", "position_rank": "Position Rank"},
    hover_data=["cum_race_distance_m", "speed_kmh"]
)
fig_position.update_layout(
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig_position, use_container_width=True)