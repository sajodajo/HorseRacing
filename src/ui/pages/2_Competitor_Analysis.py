import streamlit as st
import polars as pl
import pathlib
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Competitor Analysis",
    page_icon='src/assets/LogoSmall.png',
    layout = 'wide'
)

col1, col2, col3,col4, col5  = st.columns([1,1, 2,1, 1])
with col3:
    st.image('src/assets/NYRAlogo.png')

@st.cache_data
def load_competitor_data():
    parquet_path = pathlib.Path.cwd() / "data" / "processed" / "df_clean.parquet"
    
    required_columns = [
        "track_id",
        "horse_name", 
        "jockey",
        "race_number",
        "position_at_finish",
        "race_date" 
    ]
    
    return pl.scan_parquet(str(parquet_path)).select(required_columns).collect()

@st.cache_data 
def get_filter_options():
    """Pre-compute filter options to avoid repeated calculations"""
    df = load_competitor_data()
    
    track_ids = df.select("track_id").unique().sort("track_id").to_series().to_list()
    horses = df.select("horse_name").unique().sort("horse_name").to_series().to_list()
    
    return {
        "track_ids": track_ids,
        "horses": horses
    }

filter_options = get_filter_options()
df = load_competitor_data()

# Define track mapping
track_names_map = {"SAR": "Saratoga Race Course", "BEL": "Belmont Park", "AQU": "Aqueduct Racetrack"}
track_options = [track_names_map.get(t, t) for t in filter_options["track_ids"]]
track_id_map = {v: k for k, v in track_names_map.items()}

st.title("Competitor Analysis")
st.write("Compare multiple horses on the same track, or the same horse across multiple tracks.")

# --- Mode Selection ---
mode = st.radio(
    "Comparison Mode",
    ["Compare Horses on Same Track", "Compare Tracks for Same Horse"],
    horizontal=True
)

results = []

if mode == "Compare Horses on Same Track":
    selected_track_name = st.selectbox("Select Racetrack", track_options)
    selected_track_id = track_id_map.get(selected_track_name, selected_track_name)
    track_df = df.filter(pl.col("track_id") == selected_track_id)
    jockeys = track_df.select("jockey").unique().sort("jockey").to_series().to_list()
    selected_jockey = st.selectbox("Filter by Jockey (optional)", ["All"] + jockeys)
    if selected_jockey != "All":
        horse_df = track_df.filter(pl.col("jockey") == selected_jockey)
    else:
        horse_df = track_df
    horses = horse_df.select("horse_name").unique().sort("horse_name").to_series().to_list()
    selected_horses = st.multiselect("Select Horses to Compare", horses)
    for horse in selected_horses:
        horse_data = horse_df.filter(pl.col("horse_name") == horse)
        num_races = horse_data.select("race_number").height
        avg_horse_position = horse_data.select("position_at_finish").mean().item() if num_races > 0 else None
        jockeys_for_horse = horse_data.select("jockey").unique().to_series().to_list()
        jockey_str = ", ".join(jockeys_for_horse)
        avg_jockey_position = horse_data.select("position_at_finish").mean().item() if num_races > 0 else None
        results.append({
            "racetrack": selected_track_name,
            "jockey": jockey_str,
            "num_races": num_races,
            "avg_horse_position": avg_horse_position,
            "avg_jockey_position": avg_jockey_position,
            "horse": horse
        })
elif mode == "Compare Tracks for Same Horse":
    horses = df.select("horse_name").unique().sort("horse_name").to_series().to_list()
    selected_horse = st.selectbox("Select Horse", horses)
    horse_df = df.filter(pl.col("horse_name") == selected_horse)
    jockeys = horse_df.select("jockey").unique().sort("jockey").to_series().to_list()
    selected_jockey = st.selectbox("Filter by Jockey (optional)", ["All"] + jockeys)
    if selected_jockey != "All":
        horse_df = horse_df.filter(pl.col("jockey") == selected_jockey)
    tracks = horse_df.select("track_id").unique().sort("track_id").to_series().to_list()
    track_names = [track_names_map.get(t, t) for t in tracks]
    selected_tracks = st.multiselect("Select Tracks to Compare", track_names)
    for track_name in selected_tracks:
        track_id = track_id_map.get(track_name, track_name)
        track_data = horse_df.filter(pl.col("track_id") == track_id)
        num_races = track_data.select("race_number").height
        avg_horse_position = track_data.select("position_at_finish").mean().item() if num_races > 0 else None
        jockeys_for_track = track_data.select("jockey").unique().to_series().to_list()
        jockey_str = ", ".join(jockeys_for_track)
        avg_jockey_position = track_data.select("position_at_finish").mean().item() if num_races > 0 else None
        results.append({
            "racetrack": track_name,
            "jockey": jockey_str,
            "num_races": num_races,
            "avg_horse_position": avg_horse_position,
            "avg_jockey_position": avg_jockey_position,
            "horse": selected_horse
        })

# --- Results Table ---
if results:
    results_df = pd.DataFrame(results)
    st.markdown("### Comparison Table")
    st.dataframe(results_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Comparison Plots")
    # 1. Number of Races
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=results_df['horse'] if mode == "Compare Horses on Same Track" else results_df['racetrack'],
        y=results_df['num_races'],
        name='Number of Races',
        text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(results_df['horse'], results_df['jockey'])],
        marker_color='royalblue'
    ))
    fig1.update_layout(title='Number of Races', xaxis_title='Horse' if mode == "Compare Horses on Same Track" else 'Racetrack', yaxis_title='Number of Races', hovermode='x unified', height=400)
    st.plotly_chart(fig1, use_container_width=True)
    # 2. Horse Avg. Finishing Position
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=results_df['horse'] if mode == "Compare Horses on Same Track" else results_df['racetrack'],
        y=results_df['avg_horse_position'],
        name='Horse Avg. Finishing Position',
        text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(results_df['horse'], results_df['jockey'])],
        marker_color='orange'
    ))
    fig2.update_layout(title='Horse Avg. Finishing Position', xaxis_title='Horse' if mode == "Compare Horses on Same Track" else 'Racetrack', yaxis_title='Avg. Finishing Position', hovermode='x unified', height=400)
    st.plotly_chart(fig2, use_container_width=True)
    # 3. Jockey Avg. Finishing Position
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=results_df['horse'] if mode == "Compare Horses on Same Track" else results_df['racetrack'],
        y=results_df['avg_jockey_position'],
        name='Jockey Avg. Finishing Position',
        text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(results_df['horse'], results_df['jockey'])],
        marker_color='green'
    ))
    fig3.update_layout(title='Jockey Avg. Finishing Position', xaxis_title='Horse' if mode == "Compare Horses on Same Track" else 'Racetrack', yaxis_title='Avg. Finishing Position', hovermode='x unified', height=400)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Select at least one horse or track to compare.")

