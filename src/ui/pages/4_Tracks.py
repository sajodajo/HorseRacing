import streamlit as st
import pandas as pd
import sys
import pathlib 


# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.winClassifier import winClassifier
from src.utils.winClassifier import strategyGuide

st.set_page_config(page_title="Tracks", layout="wide")

# Custom CSS for clean white theme and style guide
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        background-color: #F9F7F1;
        color: #014421;
        font-family: 'Lato', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #014421;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.2em;
        margin-bottom: 0.5em;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: #014421;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1.5rem;
        margin: 0.5rem 0;
        font-family: 'Lato', sans-serif;
    }
    .stButton>button:hover {
        background-color: #014421;
        color: #D4AF37;
    }
    .card {
        background: #fff;
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(1,68,33,0.08);
        color: #014421;
        font-family: 'Lato', sans-serif;
    }
    .footer {
        left: 0;
        bottom: 0;
        width: 100%;
        background: #F9F7F1;
        color: #8B4513;
        text-align: center;
        padding: 0.5rem 0;
        font-size: 0.9rem;
        z-index: 100;
        border-top: 2px solid #D4AF37;
    }
    .sidebar-title {
        color: #D4AF37;
        font-family: 'Playfair Display', serif;
        font-size: 1.3em;
        margin-bottom: 0.5em;
        display: flex;
        align-items: center;
        gap: 0.5em;
    }
    .gold-icon {
        color: #D4AF37;
        font-size: 1.2em;
        margin-right: 0.3em;
    }
    </style>
''', unsafe_allow_html=True)

# Single clean header with quick stats (dummy values)
st.markdown("""
<div style='display: flex; align-items: center; justify-content: space-between;'>
    <div style='display: flex; align-items: center;'>
        <h1 style='margin-bottom: 0;'>Tracks</h1>
    </div>
    <div style='text-align: right;'>
        <span style='font-size: 1.2rem; color: #800020;'>🏇 Track Overview</span>
    </div>
</div>
<hr style='border: 1px solid #D4AF37; margin-bottom: 2rem;'>
""", unsafe_allow_html=True)




df = pd.read_csv('data/processed/trackStrategy.csv')

st.sidebar.header("Filter Race Conditions")

# 1. Track ID selector
track_options = sorted(df['track_id'].unique())
selected_track = st.sidebar.selectbox("Track ID", track_options)

# 2. Distance ID options depend on selected track
distance_options = sorted(df[df['track_id'] == selected_track]['distance_id'].unique())
selected_distance = st.sidebar.selectbox("Distance ID", distance_options)

# 3. Course Type depends on track + distance
course_options = sorted(df[(df['track_id'] == selected_track) & 
                           (df['distance_id'] == selected_distance)]['course_type'].unique())
selected_course = st.sidebar.selectbox("Course Type", course_options)

# 4. Track Condition depends on prior 3
cond_options = sorted(df[(df['track_id'] == selected_track) & 
                         (df['distance_id'] == selected_distance) &
                         (df['course_type'] == selected_course)]['track_condition'].unique())
selected_condition = st.sidebar.selectbox("Track Condition", cond_options)

# 5. Race Type depends on all 4 prior
race_options = sorted(df[(df['track_id'] == selected_track) & 
                         (df['distance_id'] == selected_distance) &
                         (df['course_type'] == selected_course) &
                         (df['track_condition'] == selected_condition)]['race_type'].unique())
selected_race = st.sidebar.selectbox("Race Type", race_options)

# ✅ Final filtered DataFrame
filtered_df = df[(df['track_id'] == selected_track) &
                 (df['distance_id'] == selected_distance) &
                 (df['course_type'] == selected_course) &
                 (df['track_condition'] == selected_condition) &
                 (df['race_type'] == selected_race)]


advice = strategyGuide(filtered_df, winClassifier(filtered_df))

st.dataframe(advice)