"""
Streamlit UI tab: Analytics Dashboard

Shows charts and summary stats.
"""

import streamlit as st
import pandas as pd

from service import TPPService


def render(user_id: str):
    st.markdown(
        """
        <style>
            .tpp-shell {
                background: linear-gradient(180deg, #d7e9ff 0%, #eaf3ff 100%);
                border-radius: 18px;
                border: 1px solid #cadcf6;
                padding: 1.2rem 1.3rem;
            }
            .tpp-hero {
                background: #f7fbff;
                border: 1px solid #d9e7fa;
                border-radius: 16px;
                padding: 1.2rem 1.4rem;
                margin-bottom: 1rem;
            }
            .tpp-kpi {
                background: #f8fbff;
                border: 1px solid #d8e6f9;
                border-radius: 14px;
                padding: 0.8rem 1rem;
                margin-bottom: 0.4rem;
            }
            .tpp-kpi-label {
                color: #637389;
                font-size: 0.95rem;
                font-weight: 600;
            }
            .tpp-kpi-value {
                color: #1b2d42;
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.15;
            }
            .tpp-panel {
                background: #fbfdff;
                border: 1px solid #dce8fa;
                border-radius: 14px;
                padding: 1rem 1.1rem;
            }
            .tpp-risk-low {
                border-left: 6px solid #2f9a4d;
            }
            .tpp-alert {
                background: #e9f6ea;
                border: 1px solid #c7e8cb;
                border-radius: 12px;
                padding: 0.8rem 1rem;
                color: #1f5130;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    history = TPPService.get_recent_history(user_id, limit=120)

    if not history:
        st.info("No data yet. Go to Vitals Input to generate predictions.")
        return

    predictions = [item["prediction"] for item in history if item["prediction"]]
    vitals_list = [item["vitals"] for item in history if item.get("vitals")]

    if not predictions or not vitals_list:
        st.warning("No completed prediction records to display yet.")
        return

    latest_pred = predictions[0]
    latest_vitals = vitals_list[0]

    heart_rates = [v.heart_rate for v in vitals_list if v.heart_rate is not None]
    hrvs = [v.hrv for v in vitals_list if v.hrv is not None]

    avg_hr = round(sum(heart_rates) / len(heart_rates)) if heart_rates else 0
    avg_hrv = round(sum(hrvs) / len(hrvs)) if hrvs else 0
    high_hr_events = sum(1 for hr in heart_rates if hr >= 110)
    records_processed = len(vitals_list)

    st.markdown('<div class="tpp-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tpp-hero">
            <div style="font-size:0.78rem; letter-spacing:0.16em; color:#2b79d1; font-weight:700;">TPP SMARTWATCH MONITOR</div>
            <div style="font-size:2.2rem; color:#162639; font-weight:800; margin-top:0.2rem;">Real-Time Thyrotoxic Risk Dashboard</div>
            <div style="font-size:1.05rem; color:#58697d; margin-top:0.25rem;">Live physiological tracking with model-assisted risk forecasting for potential TPP attacks.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="tpp-kpi"><div class="tpp-kpi-label">Avg Heart Rate</div><div class="tpp-kpi-value">{avg_hr} bpm</div><div style="color:#7a8ca1;">Current monitoring window</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="tpp-kpi"><div class="tpp-kpi-label">Avg HRV</div><div class="tpp-kpi-value">{avg_hrv} ms</div><div style="color:#7a8ca1;">Higher is generally more resilient</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="tpp-kpi"><div class="tpp-kpi-label">High HR Events</div><div class="tpp-kpi-value">{high_hr_events}</div><div style="color:#7a8ca1;">Heart rate >= 110 bpm</div></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="tpp-kpi"><div class="tpp-kpi-label">Records Processed</div><div class="tpp-kpi-value">{records_processed}</div><div style="color:#7a8ca1;">Loaded from backend</div></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([0.9, 1.4])
    with left:
        st.markdown('<div class="tpp-panel tpp-risk-low">', unsafe_allow_html=True)
        st.markdown("### Predicted TPP Risk")
        st.markdown(f"## {latest_pred.risk_score:.0%}")
        st.caption("Severity")
        st.markdown(f"### {latest_pred.severity_level.upper()}")
        st.caption("Timeline Window")
        st.markdown(f"### {latest_pred.predicted_timeline or 'N/A'}")
        st.markdown(f"{latest_pred.recommendation}")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        chart_rows = []
        for idx, v in enumerate(reversed(vitals_list[:36])):
            chart_rows.append(
                {
                    "point": idx,
                    "heartRate": v.heart_rate or 0,
                    "hrv": v.hrv or 0,
                    "steps": v.steps or 0,
                }
            )
        chart_df = pd.DataFrame(chart_rows).set_index("point")

        st.markdown('<div class="tpp-panel">', unsafe_allow_html=True)
        st.markdown(f"### Time-Series Monitoring <span style='float:right; color:#7a8ca1; font-size:1rem;'>Last {len(chart_df)} points</span>", unsafe_allow_html=True)
        st.line_chart(chart_df, use_container_width=True)
        st.caption(
            f"Latest: heartRate={latest_vitals.heart_rate or 0}, hrv={latest_vitals.hrv or 0}, steps={latest_vitals.steps or 0}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Alerts and Recommendations")
    if latest_pred.severity_level in {"high", "critical"}:
        st.warning("Risk escalation detected. Keep patient at rest and increase monitoring frequency immediately.")
    elif latest_pred.severity_level == "moderate":
        st.info("Moderate risk trend observed. Continue close observation and avoid exertion spikes.")
    else:
        st.markdown(
            '<div class="tpp-alert">Stable Monitoring Window<br><span style="font-weight:500; color:#466957;">No urgent alert pattern detected from the latest records.</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
