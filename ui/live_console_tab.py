"""
Streamlit UI tab: Live Console

Combines manual vitals input and prediction history in one compact, side-by-side view.
"""

import pandas as pd
import streamlit as st

from model import VitalsInput
from service import TPPService


def _severity_badge(level: str) -> str:
    return {
        "low": "LOW",
        "moderate": "MODERATE",
        "high": "HIGH",
        "critical": "CRITICAL",
    }.get(level, level.upper())


def render(user_id: str):
    st.markdown("### Live Console")
    st.caption("Manual vitals input and prediction history in a single screen.")

    left, right = st.columns([1, 1], gap="medium")

    with left:
        with st.container(border=True, height=640):
            st.subheader("Vitals Input", divider="gray")

            input_left, input_right = st.columns(2)
            with input_left:
                heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=85, step=1)
                hrv = st.number_input("HRV (ms)", min_value=5, max_value=150, value=40, step=1)
                steps = st.number_input("Steps (5 min)", min_value=0, max_value=500, value=20, step=5)

            with input_right:
                activity_intensity = st.number_input("Activity Intensity", min_value=0, max_value=10, value=3, step=1)
                sleep_duration = st.number_input("Sleep (mins)", min_value=0, max_value=1200, value=480, step=10)
                is_sleeping = st.toggle("Currently sleeping", value=False)

            action_left, action_right = st.columns(2)
            with action_left:
                run_prediction = st.button("Generate Prediction", key="predict_btn_live", use_container_width=True)
            with action_right:
                run_demo_high = st.button("Run Demo: High Risk", key="demo_high_live", use_container_width=True)

            run_demo_low = st.button("Run Demo: Low Risk", key="demo_low_live", use_container_width=True)

            if run_prediction:
                vitals = VitalsInput(
                    user_id=user_id,
                    heart_rate=int(heart_rate),
                    hrv=int(hrv),
                    steps=int(steps),
                    activity_intensity=int(activity_intensity),
                    sleep_duration_mins=int(sleep_duration),
                    is_sleeping=bool(is_sleeping),
                    source="manual",
                )
                st.session_state["latest_prediction"] = TPPService.predict(vitals)

            if run_demo_high:
                vitals = VitalsInput(
                    user_id=user_id,
                    heart_rate=150,
                    hrv=15,
                    steps=2,
                    activity_intensity=8,
                    sleep_duration_mins=240,
                    is_sleeping=False,
                    source="demo",
                )
                st.session_state["latest_prediction"] = TPPService.predict(vitals)

            if run_demo_low:
                vitals = VitalsInput(
                    user_id=user_id,
                    heart_rate=78,
                    hrv=50,
                    steps=150,
                    activity_intensity=2,
                    sleep_duration_mins=480,
                    is_sleeping=False,
                    source="demo",
                )
                st.session_state["latest_prediction"] = TPPService.predict(vitals)

            latest = st.session_state.get("latest_prediction")
            if latest:
                st.success(f"Latest prediction: {_severity_badge(latest.severity_level)} ({latest.risk_score:.1%})")
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Risk", f"{latest.risk_score:.1%}")
                with m2:
                    st.metric("Severity", _severity_badge(latest.severity_level))
                with m3:
                    st.metric("Timeline", latest.predicted_timeline or "N/A")
                with m4:
                    st.metric("Latency", f"{latest.processing_time_ms}ms")
                st.caption(latest.recommendation)

    with right:
        with st.container(border=True, height=640):
            top_left, top_right = st.columns([3, 1])
            with top_left:
                st.subheader("Prediction History", divider="gray")
            with top_right:
                if st.button("Refresh", key="refresh_history_live", use_container_width=True):
                    st.rerun()

            history = TPPService.get_recent_history(user_id, limit=30)
            if not history:
                st.info("No predictions yet. Generate one from the left panel.")
                return

            records = []
            for item in history:
                vitals = item["vitals"]
                pred = item["prediction"]
                if pred:
                    records.append(
                        {
                            "Created": vitals.created_at,
                            "HR": vitals.heart_rate,
                            "HRV": vitals.hrv,
                            "Steps": vitals.steps,
                            "Risk": f"{pred.risk_score:.1%}",
                            "Severity": pred.severity_level.upper(),
                            "Timeline": pred.predicted_timeline,
                        }
                    )

            if not records:
                st.warning("No completed predictions in history yet.")
                return

            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True, height=390)

            stats_left, stats_mid, stats_right = st.columns(3)
            predictions = [item["prediction"] for item in history if item["prediction"]]
            with stats_left:
                critical_count = sum(1 for pred in predictions if pred.severity_level == "critical")
                st.metric("Critical", critical_count)
            with stats_mid:
                avg_hr = sum((r["HR"] or 0) for r in records) / max(1, len(records))
                st.metric("Avg HR", f"{avg_hr:.0f} bpm")
            with stats_right:
                st.metric("Latest", records[0]["Risk"])
