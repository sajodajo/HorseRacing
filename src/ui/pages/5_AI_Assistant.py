import os
from dotenv import load_dotenv

import streamlit as st

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain_openai import ChatOpenAI

from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationBufferMemory

st.set_page_config(
    page_title="Chat with your Data", 
    page_icon=":horse_racing:")
st.title("Chat with your Data")

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
        
        st.success(f"✅ Connected to SQLite database.")

        # Create SQL toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        chat_agent = ConversationalChatAgent.from_llm_and_tools(
            llm=llm,
            tools=tools,
            system_message="""You are a Horse Racing Data Analysis Expert."""
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

