import streamlit as st
import polars as pl
import pathlib
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Competitor Analysis", layout="wide")


col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image('src/assets/NYRAlogo.png')

    
@st.cache_data
def load_competitor_data():
    parquet_path = pathlib.Path.cwd() / "data" / "processed" / "df_clean.parquet"
    df = pl.scan_parquet(str(parquet_path)).collect()
    return df

df = load_competitor_data()

track_ids = df.select("track_id").unique().sort("track_id").to_series().to_list()
track_names_map = {"SAR": "Saratoga Race Course", "BEL": "Belmont Park", "AQU": "Aqueduct Racetrack"}
track_options = [track_names_map.get(t, t) for t in track_ids]
track_id_map = {v: k for k, v in track_names_map.items()}

st.title("Competitor Analysis")
st.write("Compare up to 6 combinations of racetrack, jockey, and horse.")

num_cards = 6
results = []

for row in range(2):
    cols = st.columns(3)
    for i in range(3):
        card_idx = row * 3 + i
        with cols[i]:
            st.subheader(f"Flashcard {card_idx+1}")
            with st.expander("Selection", expanded=True):
                selected_track_name = st.selectbox(f"Select Racetrack {card_idx+1}", track_options, key=f"track_{card_idx}")
                selected_track_id = track_id_map.get(selected_track_name, selected_track_name)
                track_df = df.filter(pl.col("track_id") == selected_track_id)
                jockeys = track_df.select("jockey").unique().sort("jockey").to_series().to_list()
                if jockeys:
                    selected_jockey = st.selectbox(f"Select Jockey {card_idx+1}", jockeys, key=f"jockey_{card_idx}")
                    jockey_df = track_df.filter(pl.col("jockey") == selected_jockey)
                else:
                    selected_jockey = None
                    jockey_df = None
                horses = jockey_df.select("horse_name").unique().sort("horse_name").to_series().to_list() if jockey_df is not None else []
                if horses:
                    selected_horse = st.selectbox(f"Select Horse {card_idx+1}", horses, key=f"horse_{card_idx}")
                    horse_df = jockey_df.filter(pl.col("horse_name") == selected_horse)
                else:
                    selected_horse = None
                    horse_df = None
            if horse_df is not None and horse_df.height > 0:
                num_races = horse_df.select("race_number").height
                horse_all_df = track_df.filter(pl.col("horse_name") == selected_horse)
                avg_horse_position = horse_all_df.select("position_at_finish").mean().item()
                avg_jockey_position = jockey_df.select("position_at_finish").mean().item()
                st.markdown(f"**Racetrack:** {selected_track_name}")
                st.markdown(f"**Jockey:** {selected_jockey}")
                st.markdown(f"**Horse:** {selected_horse}")
                st.metric("Number of Races at Track", num_races)
                st.metric("Horse Avg. Finishing Position", f"{avg_horse_position:.2f}")
                st.metric("Jockey Avg. Finishing Position", f"{avg_jockey_position:.2f}")
                results.append({
                    "racetrack": selected_track_name,
                    "jockey": selected_jockey,
                    "num_races": num_races,
                    "avg_horse_position": avg_horse_position,
                    "avg_jockey_position": avg_jockey_position,
                    "horse": selected_horse,
                    "flashcard": f"Flashcard {card_idx+1}"
                })
            elif selected_jockey and not horses:
                st.info("No horses found for this jockey at this racetrack.")
                results.append(None)
            elif selected_track_id and not jockeys:
                st.info("No jockeys found for this racetrack.")
                results.append(None)
            else:
                results.append(None)

st.markdown("---")
st.subheader("Comparison Plots by Racetrack and Metric")
results_df = pd.DataFrame([r for r in results if r is not None])
if not results_df.empty:
    for racetrack in results_df['racetrack'].unique():
        racetrack_df = results_df[results_df['racetrack'] == racetrack]
        if racetrack_df.empty:
            continue
        st.markdown(f"### {racetrack}")
        # 1. Number of Races
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=racetrack_df['flashcard'],
            y=racetrack_df['num_races'],
            name='Number of Races',
            text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(racetrack_df['horse'], racetrack_df['jockey'])],
            marker_color='royalblue'
        ))
        fig1.update_layout(title='Number of Races', xaxis_title='Flashcard', yaxis_title='Number of Races', hovermode='x unified', height=400)
        st.plotly_chart(fig1, use_container_width=True)
        # 2. Horse Avg. Finishing Position
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=racetrack_df['flashcard'],
            y=racetrack_df['avg_horse_position'],
            name='Horse Avg. Finishing Position',
            text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(racetrack_df['horse'], racetrack_df['jockey'])],
            marker_color='orange'
        ))
        fig2.update_layout(title='Horse Avg. Finishing Position', xaxis_title='Flashcard', yaxis_title='Avg. Finishing Position', hovermode='x unified', height=400)
        st.plotly_chart(fig2, use_container_width=True)
        # 3. Jockey Avg. Finishing Position
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=racetrack_df['flashcard'],
            y=racetrack_df['avg_jockey_position'],
            name='Jockey Avg. Finishing Position',
            text=[f"Horse: {h}<br>Jockey: {j}" for h, j in zip(racetrack_df['horse'], racetrack_df['jockey'])],
            marker_color='green'
        ))
        fig3.update_layout(title='Jockey Avg. Finishing Position', xaxis_title='Flashcard', yaxis_title='Avg. Finishing Position', hovermode='x unified', height=400)
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No valid flashcard results to plot.")

