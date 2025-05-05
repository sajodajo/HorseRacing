import streamlit as st
import pandas as pd
import plotly.express as px
import horseFunctions as hf
import numpy as np
from datetime import date


# Title
st.title("Horse Racing Data Explorer")

main_file_path = r"../data/raw/nyra_2019_complete.parquet"
horse_global_ids = r"../data/raw/horse_ids.csv"
horse_names = r"../data/raw/horse_names.csv"

df = hf.loadData(main_file_path,horse_global_ids,horse_names)



selected_track = st.selectbox(
    "Select Track ID",
    options=sorted(df['track_id'].dropna().unique())
)
df_track = df[df['track_id'] == selected_track]

available_dates = sorted(df_track['race_date'].dropna().unique())
selected_date = st.selectbox(
    "Select Race Date",
    options=available_dates
)
df_date = df_track[df_track['race_date'] == selected_date]

available_races = sorted(df_date['race_number'].dropna().unique())
selected_race_number = st.selectbox(
    "Select Race Number",
    options=available_races
)
df_race = df_date[df_date['race_number'] == selected_race_number]

available_horses = sorted(df_race['horse_name'].dropna().unique())
selected_horse = st.selectbox(
    "Select Horse Name",
    options=available_horses
)

final_selection = df_race[df_race['horse_name'] == selected_horse]



st.write("Filtered Result:")
st.dataframe(final_selection)

st.subheader("Scatter Plot")
x_axis = final_selection['longitude']
y_axis = final_selection['latitude']

fig = px.scatter(
    final_selection,
    x=x_axis,
    y=y_axis,
    hover_data=["race_date", "horse_name", "jockey", "odds", "position_at_finish"]
)
st.plotly_chart(fig, use_container_width=True)