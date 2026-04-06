"""
TPP Monitoring Dashboard — Streamlit GUI.

Provides an interactive dashboard with tabs for:
  1. Vitals Input     — enter/upload vitals, generate predictions
  2. Prediction Hist  — view recent predictions and trends
  3. Dashboard        — analytics overview

Connects directly to service/DAO layers. No HTTP overhead.

Launch:
    streamlit run streamlit_app.py
"""

import streamlit as st

from config.database import init_db


# ── Page configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="TPP Monitoring Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── One-time database initialisation ─────────────────────────────────
@st.cache_resource
def _boot():
    init_db()

_boot()


# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.title("TPP Monitoring")
    st.caption("Real-time Thyrotoxic Periodic Paralysis risk prediction")
    st.divider()
    
    user_id = st.text_input("User ID", value="user-demo", key="sidebar_user_id")
    st.session_state["user_id"] = user_id
    
    st.markdown(
        """
        **How to use:**
        1. Enter vitals in the **Vitals Input** tab
        2. View predictions in **History**
        3. See trends in **Dashboard**
        """
    )


# ── Main tabbed interface ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Vitals Input",
    "Prediction History",
    "Dashboard",
])

from ui.vitals_input_tab import render as render_vitals
from ui.history_tab import render as render_history
from ui.dashboard_tab import render as render_dashboard

with tab1:
    render_vitals(st.session_state.get("user_id", "user-demo"))
with tab2:
    render_history(st.session_state.get("user_id", "user-demo"))
with tab3:
    render_dashboard(st.session_state.get("user_id", "user-demo"))
