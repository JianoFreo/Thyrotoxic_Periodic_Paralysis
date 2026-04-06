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

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 20% 0%, #232834 0%, #141824 45%, #0f131d 100%);
            color: #e7ecf5;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #121722 0%, #0b1018 100%);
            border-right: 1px solid #2a3140;
        }
        h1, h2, h3, h4, h5, h6, p, label, .stCaption {
            color: #e7ecf5 !important;
        }
        [data-testid="stMetric"] {
            background: #171d2a;
            border: 1px solid #2e3748;
            border-radius: 12px;
            padding: 0.3rem 0.6rem;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid #2e3748;
            border-radius: 12px;
            overflow: hidden;
        }
        .stButton > button {
            background: rgba(165, 114, 255, 0.10);
            color: #efe7ff;
            border: 1px solid rgba(189, 148, 255, 0.38);
            border-radius: 10px;
        }
        .stButton > button:hover {
            background: rgba(165, 114, 255, 0.16);
            border-color: rgba(204, 171, 255, 0.52);
        }
        .stNumberInput input,
        .stTextInput input,
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            background: #0f1522 !important;
            color: #e7ecf5 !important;
            border-color: #2c3747 !important;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0.7rem;
            max-height: 100vh;
        }
    </style>
    """,
    unsafe_allow_html=True,
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
        1. Enter vitals in **Live Console**
        2. Review predictions in the right-side history panel
        3. See trends in **Dashboard**
        """
    )


# ── Main tabbed interface ────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "Live Console",
    "Dashboard",
])

from ui.live_console_tab import render as render_live_console
from ui.dashboard_tab import render as render_dashboard

with tab1:
    render_live_console(st.session_state.get("user_id", "user-demo"))
with tab2:
    render_dashboard(st.session_state.get("user_id", "user-demo"))
