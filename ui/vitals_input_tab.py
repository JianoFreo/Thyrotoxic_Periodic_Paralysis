"""
Streamlit UI tab: Vitals Input Form

Allows manual entry of physiological metrics or file upload.
Generates predictions on submit.
"""

import streamlit as st

from model import VitalsInput
from service import TPPService


def render(user_id: str):
    st.header("📊 Enter Vitals")
    
    st.markdown(
        """
        Input your physiological metrics here. The system will compute your TPP risk 
        immediately.
        """
    )
    
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
    
    st.divider()
    
    # Prediction button
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
    
    st.divider()
    
    # Demo data
    if st.button("Load Demo (High Risk)", key="demo_high"):
        st.session_state["demo_high"] = True
    
    if st.button("Load Demo (Low Risk)", key="demo_low"):
        st.session_state["demo_low"] = True
    
    if st.session_state.get("demo_high"):
        st.info("Demo: High HR (150bpm), Low HRV (15ms), Low steps → High Risk")
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
        st.success(f"✅ Prediction: {pred.severity_level.upper()} risk ({pred.risk_score:.1%})")
        st.session_state["demo_high"] = False
    
    if st.session_state.get("demo_low"):
        st.info("Demo: Normal HR (78bpm), Good HRV (50ms), Active → Low Risk")
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
        st.success(f"✅ Prediction: {pred.severity_level.upper()} risk ({pred.risk_score:.1%})")
        st.session_state["demo_low"] = False
