import os
import sys
import pathlib 
from dotenv import load_dotenv
import polars as pl

import streamlit as st

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain_openai import ChatOpenAI

from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationBufferMemory

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.prompt_template import AGENT_SYSTEM_MESSAGE
from src.utils.plotting_tool import plotly_graph_tool


st.set_page_config(
    page_title="Chat with your Data",
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
    
st.title("Chat with your AI Horse Racing Data Analyst :robot_face:")

@st.cache_data
def load_dataset_info():
    """Load dataset information for sidebar display"""
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent 
    parquet_path = base_dir / "data" / "processed" / "df_clean.parquet"
    
    # Load only the columns needed for dataset info
    df = pl.scan_parquet(str(parquet_path)).select([
        "track_id", "horse_name", "jockey", "course_type", 
        "race_date", "race_type", "distance_id"
    ]).collect()
    
    return {
        "tracks": sorted(df.select("track_id").drop_nulls().unique().to_series().to_list()),
        "horses": sorted(df.select("horse_name").drop_nulls().unique().to_series().to_list()),
        "jockeys": sorted(df.select("jockey").drop_nulls().unique().to_series().to_list()),
        "course_types": sorted(df.select("course_type").drop_nulls().unique().to_series().to_list()),
        "race_types": sorted(df.select("race_type").drop_nulls().unique().to_series().to_list()) if "race_type" in df.columns else [],
        "total_races": df.height,
        "date_range": {
            "start": df.select("race_date").min().item(),
            "end": df.select("race_date").max().item()
        }
    }


with st.sidebar:
    
    # Dataset Information Section
    st.markdown("### 📊 Dataset Overview")
    
    try:
        dataset_info = load_dataset_info()
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", f"{dataset_info['total_races']:,}")
            st.metric("Unique Horses", len(dataset_info['horses']))
        with col2:
            st.metric("Unique Jockeys", len(dataset_info['jockeys']))
            st.metric("Tracks", len(dataset_info['tracks']))
        
        # Date range
        if dataset_info['date_range']['start'] and dataset_info['date_range']['end']:
            st.info(f"**Date Range:** {dataset_info['date_range']['start']} to {dataset_info['date_range']['end']}")
        
        st.markdown("---")
        
        # Interactive dropdowns for exploring data
        st.markdown("### Explore Dataset Info")
        
        # Track selection
        if st.checkbox("View Tracks"):
            track_map = {"SAR": "Saratoga Race Course", "BEL": "Belmont Park", "AQU": "Aqueduct Racetrack"}
            for track in dataset_info['tracks']:
                track_name = track_map.get(track, track)
                st.write(f"• **{track}**: {track_name}")
        
        # Horse selection
        if st.checkbox("Browse Horses"):
            selected_horse = st.selectbox(
                "Select Horse",
                [""] + dataset_info['horses'],
                key="horse_selector"
            )
            if selected_horse:
                st.success(f"Selected: **{selected_horse}**")
                st.caption("💡 Try asking: 'Show me all races for [horse name]'")
        
        # Jockey selection
        if st.checkbox("Browse Jockeys"):
            selected_jockey = st.selectbox(
                "Select Jockey",
                [""] + dataset_info['jockeys'],
                key="jockey_selector"
            )
            if selected_jockey:
                st.success(f"Selected: **{selected_jockey}**")
                st.caption("💡 Try asking: 'What is [jockey name]'s win rate?'")
        
        # Course types
        if st.checkbox("View Course Types"):
            for course_type in dataset_info['course_types']:
                st.write(f"• {course_type}")
        
        st.markdown("---")
        
    except Exception as e:
        st.error(f"Could not load dataset info: {e}")
    
    # FAQ Section
    with st.expander("💡 Sample Questions"):
        st.markdown("- *Which jockey has the most wins at Saratoga?*")
        st.markdown("- *Plot speed distribution for winning horses*")


# Agent chatbot implementation

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("I am your Horse Analyst Agent, how can I help you?")
    st.session_state.steps = {}

def initialize_agent():

    load_dotenv()
    
    SQLITE_DB_PATH = "data/processed/horse_racing_data.db"
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )
        
        # Create database connection
        db = SQLDatabase.from_uri(f"sqlite:///{SQLITE_DB_PATH}")
        
        st.success(f"✅ Connected to horse racing database.")

        # Create SQL toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        # Add the Plotly graph tool
        tools.append(plotly_graph_tool)

        chat_agent = ConversationalChatAgent.from_llm_and_tools(
            llm=llm,
            tools=tools,
            system_message=AGENT_SYSTEM_MESSAGE,
        )

        agent = AgentExecutor.from_agent_and_tools(
            agent=chat_agent,
            tools=tools,
            memory=memory,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )
        
        return agent
    
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.stop()


def main():
    agent = initialize_agent()
    avatars = {"human": "user", "ai": "assistant"}
    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(avatars[msg.type]):
            st.write(msg.content)
            for step in st.session_state.steps.get(str(idx), []):
                if step[0].tool == "_Exception":
                    continue
                with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                    st.write(step[0].log)
                    st.write(step[1])
                st.write(msg.content)

    if prompt := st.chat_input(placeholder="Ask me anything about horse racing data!"):
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(
                st.container(), 
                max_thought_containers=10,
                expand_new_thoughts=False)
            cfg = RunnableConfig()
            cfg["callbacks"] = [st_cb]
            response = agent.invoke(
                prompt,
                cfg
            )
            st.write(response["output"])
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]


if __name__ == "__main__":
    main()

