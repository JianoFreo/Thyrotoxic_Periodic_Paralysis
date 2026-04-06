"""
Streamlit UI tab: Analytics Dashboard

Shows charts and summary stats.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from service import TPPService


def render(user_id: str):
    st.header("📈 Analytics Dashboard")
    
    history = TPPService.get_recent_history(user_id, limit=100)
    
    if not history:
        st.info("No data yet. Go to **Vitals Input** to generate predictions.")
        return
    
    # Prepare data
    predictions = [item["prediction"] for item in history if item["prediction"]]
    vitals_list = [item["vitals"] for item in history]
    
    if not predictions:
        st.warning("No completed predictions to display.")
        return
    
    # Risk score trend
    st.subheader("Risk Score Trend")
    risk_data = pd.DataFrame({
        "Timestamp": [p.created_at for p in predictions],
        "Risk Score": [p.risk_score for p in predictions],
    })
    risk_data = risk_data.sort_values("Timestamp").reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(range(len(risk_data)), risk_data["Risk Score"], marker="o", color="#0f8bff")
    ax.axhline(y=0.35, color="yellow", linestyle="--", alpha=0.5, label="Moderate")
    ax.axhline(y=0.65, color="orange", linestyle="--", alpha=0.5, label="High")
    ax.axhline(y=0.85, color="red", linestyle="--", alpha=0.5, label="Critical")
    ax.set_xlabel("Prediction #")
    ax.set_ylabel("Risk Score")
    ax.set_title("TPP Risk Score Over Time")
    ax.legend()
    ax.set_ylim(0, 1.0)
    st.pyplot(fig)
    
    # Severity distribution
    st.subheader("Severity Distribution")
    severity_counts = {}
    for p in predictions:
        severity_counts[p.severity_level] = severity_counts.get(p.severity_level, 0) + 1
    
    if severity_counts:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🟢 Low", severity_counts.get("low", 0))
        with col2:
            st.metric("🟡 Moderate", severity_counts.get("moderate", 0))
        with col3:
            st.metric("🟠 High", severity_counts.get("high", 0))
        with col4:
            st.metric("🔴 Critical", severity_counts.get("critical", 0))
    
    # Vitals distribution
    st.subheader("Vitals Statistics")
    
    heart_rates = [v.heart_rate for v in vitals_list if v.heart_rate]
    hrvs = [v.hrv for v in vitals_list if v.hrv]
    steps_list = [v.steps for v in vitals_list if v.steps]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if heart_rates:
            st.metric("Avg HR", f"{sum(heart_rates) / len(heart_rates):.0f} bpm")
            st.metric("Max HR", f"{max(heart_rates)} bpm")
            st.metric("Min HR", f"{min(heart_rates)} bpm")
    
    with col2:
        if hrvs:
            st.metric("Avg HRV", f"{sum(hrvs) / len(hrvs):.0f} ms")
            st.metric("Max HRV", f"{max(hrvs)} ms")
            st.metric("Min HRV", f"{min(hrvs)} ms")
    
    with col3:
        if steps_list:
            st.metric("Avg Steps", f"{sum(steps_list) / len(steps_list):.0f}")
            st.metric("Total Steps", f"{sum(steps_list)}")
