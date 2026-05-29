"""
AXTEA CNC HMI – Streamlit wrapper
Serves the standalone HTML HMI from hmi/index.html
"""
import streamlit as st
import os

st.set_page_config(
    page_title="AXTEA CNC HMI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome so only the HMI is visible
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton { display: none !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  iframe { border: none; }
</style>
""", unsafe_allow_html=True)

html_path = os.path.join(os.path.dirname(__file__), "hmi", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=900, scrolling=False)
