"""
Streamlit UI tab: Prediction History

Displays recent predictions and vitals.
"""

import streamlit as st
import pandas as pd

from service import TPPService


def render(user_id: str):
    st.header("📋 Prediction History")
    
    if st.button("Refresh History", use_container_width=True):
        st.cache_data.clear()
    
    history = TPPService.get_recent_history(user_id, limit=50)
    
    if not history:
        st.info("No predictions yet. Go to **Vitals Input** to create one!")
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
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("Summary Stats")
        
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
    else:
        st.warning("No completed predictions in history.")
