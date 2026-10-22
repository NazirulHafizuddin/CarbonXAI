"""
app.py
CarbonXAI entry point. Run with:

    streamlit run app.py

It only sets up the page and routes between the two screens:
  landing_page.py -> story-style introduction (opens first)
  dashboard.py    -> the dashboard (Prediction, Model comparison, SHAP explanations, Sustainability insights)

The dashboard can also be opened directly at  /dashboard
"""

import streamlit as st

st.set_page_config(
    page_title="CarbonXAI | Carbon Emission Prediction",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

pages = [
    st.Page("landing_page.py", title="Intro", icon="", default=True),
    st.Page("dashboard.py", title="Dashboard", icon="", url_path="dashboard"),
]
st.navigation(pages, position="hidden").run()
