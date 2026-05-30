"""
AXTEA CNC HMI – Streamlit web launcher
Serves the standalone HTML HMI. Opens full-screen in an iframe.
"""
import streamlit as st
import os

st.set_page_config(
    page_title="AXTEA CNC HMI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Remove every Streamlit UI element; make iframe fill the viewport
st.markdown("""
<style>
  /* Hide Streamlit chrome */
  #MainMenu, header, footer,
  .stDeployButton, [data-testid="stToolbar"],
  [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
  }
  /* Zero out all padding/margins */
  html, body, [data-testid="stAppViewContainer"],
  [data-testid="stMain"], .main, .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    height: 100vh !important;
    overflow: hidden !important;
  }
  /* Make the component iframe fill everything */
  iframe {
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    display: block !important;
  }
</style>
""", unsafe_allow_html=True)

html_path = os.path.join(os.path.dirname(__file__), "hmi", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# height=0 lets the CSS override take full control
st.components.v1.html(html_content, height=980, scrolling=False)
