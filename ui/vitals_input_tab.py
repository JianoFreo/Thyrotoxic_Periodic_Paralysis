"""
Streamlit UI tab: Vitals Input Form

Allows manual entry of physiological metrics or file upload.
Generates predictions on submit.
"""

import streamlit as st

from model import VitalsInput
from service import TPPService


def render(user_id: str):
    st.markdown(
        """
        <style>
            .vitals-shell {
                background: linear-gradient(180deg, #d7e9ff 0%, #eaf3ff 100%);
                border-radius: 18px;
                border: 1px solid #cadcf6;
                padding: 1.2rem 1.3rem;
            }
            .vitals-card {
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

    st.markdown('<div class="vitals-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="vitals-card">
            <div style="font-size:0.78rem; letter-spacing:0.14em; color:#2b79d1; font-weight:700;">VITALS CAPTURE</div>
            <div style="font-size:1.9rem; color:#162639; font-weight:800; margin-top:0.2rem;">Enter Physiological Signals</div>
            <div style="color:#5d6d80; margin-top:0.2rem;">Provide the latest biometrics to generate a model-assisted TPP risk estimate.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vitals-card">', unsafe_allow_html=True)
    st.markdown("### Manual Input")
    col1, col2 = st.columns(2)
    
    with col1:
        heart_rate = st.slider(
            "Heart Rate (bpm)",
            min_value=40,
            max_value=200,
            value=85,
            step=1,
        )
        hrv = st.slider(
            "Heart Rate Variability (HRV, ms)",
            min_value=5,
            max_value=150,
            value=40,
            step=1,
        )
        steps = st.slider(
            "Steps (in last 5 min)",
            min_value=0,
            max_value=500,
            value=20,
            step=10,
        )
    
    with col2:
        activity_intensity = st.slider(
            "Activity Intensity (0-10)",
            min_value=0,
            max_value=10,
            value=3,
            step=1,
        )
        sleep_duration = st.slider(
            "Recent Sleep (mins)",
            min_value=0,
            max_value=1200,
            value=480,
            step=30,
        )
        is_sleeping = st.checkbox("Currently sleeping?", value=False)

    st.markdown("</div>", unsafe_allow_html=True)

    # Prediction button
    st.markdown('<div class="vitals-card">', unsafe_allow_html=True)
    st.markdown("### Risk Inference")
    if st.button("Generate Prediction", key="predict_btn", use_container_width=True):
        with st.spinner("Computing TPP risk..."):
            vitals = VitalsInput(
                user_id=user_id,
                heart_rate=heart_rate,
                hrv=hrv,
                steps=steps,
                activity_intensity=activity_intensity,
                sleep_duration_mins=sleep_duration,
                is_sleeping=is_sleeping,
                source="manual",
            )
            
            pred = TPPService.predict(vitals)

            st.success(f"Prediction generated! (ID: {pred.prediction_id[:8]}...)")

            # Display result
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Risk Score", f"{pred.risk_score:.1%}")
            with col2:
                severity_emoji = {
                    "low": "🟢",
                    "moderate": "🟡",
                    "high": "🟠",
                    "critical": "🔴",
                }
                st.metric("Severity", f"{severity_emoji.get(pred.severity_level, '')} {pred.severity_level.upper()}")
            with col3:
                st.metric("Timeline", pred.predicted_timeline or "N/A")
            with col4:
                st.metric("Processing", f"{pred.processing_time_ms}ms")

            st.info(f"**Recommendation:** {pred.recommendation}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Demo data
    st.markdown('<div class="vitals-card">', unsafe_allow_html=True)
    st.markdown("### Quick Demo Scenarios")
    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        if st.button("Load Demo (High Risk)", key="load_demo_high", use_container_width=True):
            st.info("Demo: High HR (150bpm), Low HRV (15ms), Low steps -> High Risk")
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
            pred = TPPService.predict(vitals)
            st.success(f"Prediction: {pred.severity_level.upper()} risk ({pred.risk_score:.1%})")

    with demo_col2:
        if st.button("Load Demo (Low Risk)", key="load_demo_low", use_container_width=True):
            st.info("Demo: Normal HR (78bpm), Good HRV (50ms), Active -> Low Risk")
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
            pred = TPPService.predict(vitals)
            st.success(f"Prediction: {pred.severity_level.upper()} risk ({pred.risk_score:.1%})")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
