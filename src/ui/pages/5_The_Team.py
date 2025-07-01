import streamlit as st
import polars as pl
import pathlib
import plotly.graph_objects as go
import pandas as pd




import streamlit as st

st.set_page_config(
    page_title="About the Team",
    page_icon='Media/logoSmall.png',
    layout = 'wide'
)

col1, col2, col3,col4, col5  = st.columns([1,1, 2,1, 1])
with col3:
    st.image('src/assets/NYRAlogo.png')

st.title("About the Team")


# Create 5 columns
col1, col2, col3, col4, col5 = st.columns(5)


linkedinPic = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQVwpVlXEdO4SYUobUhd4C0DxLhsil1mNLpiw&s'
sjLI = 'https://www.linkedin.com/in/sajodajo/'
sjLIpic = 'https://media.licdn.com/dms/image/v2/D4D03AQEBnWkkwXXlzA/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1719831432445?e=1756339200&v=beta&t=ve9ofdglsFjmWTUjrAudnosirhlZqW4i-GyS9ZzRho4'
icLI = 'https://www.linkedin.com/in/marius-gnoth/'
icLIpic = 'https://media.licdn.com/dms/image/v2/D4E03AQHA5rgpMf7lrw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1684437962309?e=1756944000&v=beta&t=-qmZ0HrQxbDx4cQM7UsbN61Xxp9peLGEVEA4svOBC5A'
tsLI = 'https://www.linkedin.com/in/vandad-vafai-ba29b2207/'
tsLIpic = 'https://media.licdn.com/dms/image/v2/C4E03AQEzVv42PrCweA/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1662045545911?e=1756944000&v=beta&t=C-CwixIr2jsat4fvm_lS1VHBaNNpHThHNe-xGVtSjVM'
epLI = 'https://www.linkedin.com/in/maineisasi/'
epLIpic = 'https://media.licdn.com/dms/image/v2/D4D03AQH2h9YxPTo33w/profile-displayphoto-shrink_400_400/B4DZbfmcswIAAg-/0/1747508120782?e=1756944000&v=beta&t=hhx9O6Hagx1MfRDHA2cHfoHKUjz3VN6QTVUiRbHl7iw'
ckLI = 'https://www.linkedin.com/in/joaquin-mino-perez/'
ckLIpic = 'https://media.licdn.com/dms/image/v2/D4E03AQH80GUxmNjL_A/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1731686881859?e=1756944000&v=beta&t=5zhCrkhOeWUCWZEbW5-HZ1NLvCwLIaeD5ZoeFsNvvYk'




with col1:
    st.image(sjLIpic, use_container_width=True)
    st.subheader('🇮🇪 Sam Jones')
    st.write('MSc student of Data Science at IE University, with two years of experience in innovation consulting focused on sustainability, digital technologies, and startup engagement. Skilled in Python and SQL for data analytics and database management, with a solid understanding of machine learning, AI, and modern data architectures.')
    st.markdown(
    f'''
    <div style="text-align: center;">
        <a href="{sjLI}" target="_blank">
            <img src="{linkedinPic}" style="max-width:75px; height:auto;" />
        </a>
    </div>
    ''',
    unsafe_allow_html=True
    )

# Column 2
with col2:
    st.image(icLIpic, use_container_width=True)
    st.subheader('🇩🇪 Marius Gnoth')
    st.write('sample text')
    st.markdown(
    f'''
    <div style="text-align: center;">
        <a href="{icLI}" target="_blank">
            <img src="{linkedinPic}" style="max-width:75px; height:auto;" />
        </a>
    </div>
    ''',
    unsafe_allow_html=True
    )

with col3:
    st.image(tsLIpic, use_container_width=True)
    st.subheader('🇮🇷 Vandad Vafai')
    st.write('sample text')
    st.markdown(
    f'''
    <div style="text-align: center;">
        <a href="{tsLI}" target="_blank">
            <img src="{linkedinPic}" style="max-width:75px; height:auto;" />
        </a>
    </div>
    ''',
    unsafe_allow_html=True
    )
    
# Column 4
with col4:
    st.image(epLIpic, use_container_width=True)
    st.subheader('🇵🇪 Maine Isasi')
    st.write('sample text')
    st.markdown(
    f'''
    <div style="text-align: center;">
        <a href="{epLI}" target="_blank">
            <img src="{linkedinPic}" style="max-width:75px; height:auto;" />
        </a>
    </div>
    ''',
    unsafe_allow_html=True
    )
    
# Column 5
with col5:
    st.image(ckLIpic, use_container_width=True)
    st.subheader('🇪🇨 Joaquin Miño')
    st.write('sample text')
    st.markdown(
    f'''
    <div style="text-align: center;">
        <a href="{ckLI}" target="_blank">
            <img src="{linkedinPic}" style="max-width:75px; height:auto;" />
        </a>
    </div>
    ''',
    unsafe_allow_html=True
    )

