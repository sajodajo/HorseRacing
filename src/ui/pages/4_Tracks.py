## IMPORTS ##

import streamlit as st
import pandas as pd
import sys
import pathlib 
import numpy as np
import pydeck as pdk
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from src.utils.winClassifier import winClassifier
from src.utils.winClassifier import strategyGuide
from src.utils.winClassifier import strategy_block


## PAGE VISUALS ##
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image('src/assets/NYRAlogo.png')

segment_colors = {
    "Q1": [255, 0, 0],      # Red
    "Q2": [255, 165, 0],    # Orange
    "Q3": [0, 128, 0],      # Green
    "Q4": [0, 0, 255]       # Blue
}


## DATA LOADING ##
overallDF = pd.read_parquet('data/processed/df_clean_temp.parquet')
df = pd.read_csv('data/processed/trackStrategy.csv')


## SIDEBAR ##
st.sidebar.header("Filter Race Conditions")

track_options = sorted(df['track_id'].unique())
selected_track = st.sidebar.selectbox("Track ID", track_options)

distance_options = sorted(df[df['track_id'] == selected_track]['distance_id'].unique())
selected_distance = st.sidebar.selectbox("Distance ID", distance_options)

course_options = sorted(df[(df['track_id'] == selected_track) & 
                           (df['distance_id'] == selected_distance)]['course_type'].unique())
selected_course = st.sidebar.selectbox("Course Type", course_options)

cond_options = sorted(df[(df['track_id'] == selected_track) & 
                         (df['distance_id'] == selected_distance) &
                         (df['course_type'] == selected_course)]['track_condition'].unique())
selected_condition = st.sidebar.selectbox("Track Condition", cond_options)

race_options = sorted(df[(df['track_id'] == selected_track) & 
                         (df['distance_id'] == selected_distance) &
                         (df['course_type'] == selected_course) &
                         (df['track_condition'] == selected_condition)]['race_type'].unique())
selected_race = st.sidebar.selectbox("Race Type", race_options)

filtered_df = df[(df['track_id'] == selected_track) &
                 (df['distance_id'] == selected_distance) &
                 (df['course_type'] == selected_course) &
                 (df['track_condition'] == selected_condition) &
                 (df['race_type'] == selected_race)]


## PAGE CONTENT ##
st.title("Track Strategy Tool :horse_racing:")


advice = strategyGuide(filtered_df, winClassifier(filtered_df))

col1, col2 = st.columns(2)

with col1:

    pQ1 = str(advice[advice['Feature']=='pos_Q1']['Strategy Tip'].values[0])
    pQ2 = str(advice[advice['Feature']=='pos_Q2']['Strategy Tip'].values[0])
    pQ3 = str(advice[advice['Feature']=='pos_Q3']['Strategy Tip'].values[0])
    pQ4 = str(advice[advice['Feature']=='pos_Q4']['Strategy Tip'].values[0])

    sQ1 = str(advice[advice['Feature']=='speed_Q1']['Strategy Tip'].values[0])
    sQ2 = str(advice[advice['Feature']=='speed_Q2']['Strategy Tip'].values[0])
    sQ3 = str(advice[advice['Feature']=='speed_Q3']['Strategy Tip'].values[0])
    sQ4 = str(advice[advice['Feature']=='speed_Q4']['Strategy Tip'].values[0])


    strategy_block("Q1", pQ1, sQ1,segment_colors)
    strategy_block("Q2", pQ2, sQ2,segment_colors)
    strategy_block("Q3", pQ3, sQ3,segment_colors)
    strategy_block("Q4", pQ4, sQ4,segment_colors)







overallDF = overallDF[(overallDF['track_id'] == selected_track) &
                 (overallDF['distance_id'] == selected_distance) &
                 (overallDF['course_type'] == selected_course) &
                 (overallDF['track_condition'] == selected_condition) &
                 (overallDF['race_type'] == selected_race)]

with col2:
    ## MAP VIZ 

    # Map segment to color
    overallDF['color'] = overallDF['Segment'].map(segment_colors)

    # Define the layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=overallDF,
        get_position='[longitude, latitude]',
        get_fill_color='color',
        get_radius=30,
        pickable=True,
        opacity=0.8
    )

    # Center the view around the data
    view_state = pdk.ViewState(
        latitude=overallDF['latitude'].mean(),
        longitude=overallDF['longitude'].mean(),
        zoom=15,
        pitch=0
    )


    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Segment: {Segment}"}
    ))

    def padded_paragraph(text):
        st.markdown(f"<div style='padding: 0.75rem 1rem; font-size: 1rem; line-height: 1.6;'>{text}</div>", unsafe_allow_html=True)

    if selected_track == "SAR":
        st.subheader("🏇 Saratoga Race Course (SAR)")
        padded_paragraph("""
            Saratoga is a <b>tactical track</b> known for its tight turns, shorter stretch, and often <b>quirky pace dynamics</b>.
            The main dirt track is a full mile, and two turf courses (inner and Mellon) present varying challenges for positioning.
            Summer conditions are usually firm on turf and fast on dirt, favoring <b>forwardly placed horses</b>, though closers can strike with well-timed moves.
            Riders must be decisive early — <b>losing position around the clubhouse turn can be costly</b>.
            The Saratoga meet runs July through early September, attracting large, high-quality fields and often unpredictable results.
        """)

    elif selected_track == "AQU":
        st.subheader("🐎 Aqueduct Racetrack (AQU)")
        padded_paragraph("""
            Aqueduct’s layout varies by season, with the <b>winterized inner dirt track</b> in play from late fall through early spring, when turf racing is suspended.
            The main dirt oval is relatively <b>kind to speed</b>, especially in colder months when the surface tightens.
            However, the <b>outer turns are more forgiving</b> than Belmont’s, giving mid-pack runners a better chance to re-engage.
            The track has a reputation for producing more <b>formful and pace-reliable races</b>, making it favorable for well-prepared horses.
            Riders should pay close attention to track bias during the meet, which can shift subtly with weather.
        """)

    elif selected_track == "BEL":
        st.subheader("🐴 Belmont Park (BEL)")
        padded_paragraph("""
            Belmont’s massive 1.5-mile main dirt track — the largest in North America — rewards horses with <b>efficient cruising speed</b> and <b>stamina</b>, especially in route races.
            The wide, sweeping turns and <b>long stretch (1,097 feet)</b> make early moves risky and often ineffective.
            On both dirt and turf, <b>deep closers are more viable</b> here than at other NYRA tracks.
            The inner turf can be tight, but the outer turf plays fairer.
            Belmont’s spring and fall meets often feature faster turf rails and can favor <b>outside posts in sprints</b>.
            Jockeys must be patient and manage energy carefully, particularly in late-stretch drives.
        """)
