from typing import Annotated
import streamlit as st
import plotly.graph_objects as go
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

repl = PythonREPL()

@tool
def plotly_graph_tool(
    code: Annotated[str, "The Python code to execute to generate a Plotly chart."],
):
    """Executes Python code to generate a Plotly chart and displays it in Streamlit."""
    try:
        # Prepare local variables for execution
        local_vars = {"st": st, "go": go}
        
        # Execute the Python code
        exec(code, local_vars)
        
        # Check if a Plotly figure was created and render it in a dedicated Streamlit container
        if "fig" in local_vars and isinstance(local_vars["fig"], go.Figure):
            with st.container():  # Create a dedicated container for the graph
                st.plotly_chart(local_vars["fig"])
            return f"Successfully rendered the chart inline:\n```python\n{code}\n```"
        else:
            return f"Code executed successfully, but no Plotly figure ('fig') was found:\n```python\n{code}\n```"
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"