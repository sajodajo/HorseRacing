import streamlit as st

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
st.markdown(f"""
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

# Sidebar filters with gold icons and titles
with st.sidebar:
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>📅</span> Date</div>", unsafe_allow_html=True)
    st.date_input("", key="date_input_tracks")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>🏟️</span> Racecourse</div>", unsafe_allow_html=True)
    st.selectbox("", ["Belmont", "Saratoga", "Aqueduct"], key="racecourse_input_tracks")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>🐴</span> Horse</div>", unsafe_allow_html=True)
    st.text_input("", key="horse_input_tracks")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>👨‍✈️</span> Jockey</div>", unsafe_allow_html=True)
    st.text_input("", key="jockey_input_tracks")
    st.markdown("<div class='sidebar-title'><span class='gold-icon'>💰</span> Odds Range</div>", unsafe_allow_html=True)
    st.slider("", 1.0, 100.0, (1.0, 20.0), key="odds_input_tracks")
    st.markdown("---")
    st.markdown("<span style='color:#D4AF37;'>Use filters to refine your analysis.</span>", unsafe_allow_html=True)

# Main panel content (dummy)
st.markdown("## Explore Race Tracks")
st.info("This page will provide information and statistics about different tracks.")

