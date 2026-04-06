"""
Streamlit UI tab: Prediction History

Displays recent predictions and vitals.
"""

import streamlit as st
import pandas as pd

from service import TPPService


def render(user_id: str):
    st.markdown(
        """
        <style>
            .history-shell {
                background: linear-gradient(180deg, #d7e9ff 0%, #eaf3ff 100%);
                border-radius: 18px;
                border: 1px solid #cadcf6;
                padding: 1.2rem 1.3rem;
            }
            .history-card {
                background: #f9fcff;
                border: 1px solid #d9e7fa;
                border-radius: 14px;
                padding: 0.9rem 1rem;
                margin-bottom: 0.8rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="history-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="history-card">
            <div style="font-size:0.78rem; letter-spacing:0.14em; color:#2b79d1; font-weight:700;">PREDICTION LOG</div>
            <div style="font-size:1.9rem; color:#162639; font-weight:800; margin-top:0.2rem;">Historical Risk Records</div>
            <div style="color:#5d6d80; margin-top:0.2rem;">Review generated predictions, signal context, and aggregate trends over time.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Refresh History", use_container_width=True):
        st.cache_data.clear()

    history = TPPService.get_recent_history(user_id, limit=50)

    if not history:
        st.info("No predictions yet. Go to **Vitals Input** to create one!")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Build dataframe
    records = []
    for item in history:
        v = item["vitals"]
        p = item["prediction"]
        if p:
            records.append({
                "Created": v.created_at,
                "Heart Rate": v.heart_rate,
                "HRV": v.hrv,
                "Steps": v.steps,
                "Risk Score": f"{p.risk_score:.1%}",
                "Severity": p.severity_level.upper(),
                "Timeline": p.predicted_timeline,
                "Processing (ms)": p.processing_time_ms,
            })

    if records:
        df = pd.DataFrame(records)
        st.markdown('<div class="history-card">', unsafe_allow_html=True)
        st.markdown("### Detailed Records")
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="history-card">', unsafe_allow_html=True)
        st.markdown("### Summary Stats")

        col1, col2, col3 = st.columns(3)

        with col1:
            predictions = [item["prediction"] for item in history if item["prediction"]]
            if predictions:
                critical_count = sum(1 for p in predictions if p.severity_level == "critical")
                st.metric("Critical Alerts", critical_count)

        with col2:
            if records:
                avg_hr = sum(r["Heart Rate"] or 0 for r in records) / len(records)
                st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")

        with col3:
            if records:
                latest_risk = records[0]["Risk Score"]
                st.metric("Latest Risk", latest_risk)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No completed predictions in history.")

    st.markdown("</div>", unsafe_allow_html=True)
