import streamlit as st
import pandas as pd
from service import TPPService


def render(user_id: str):
    # ------------------ STYLES ------------------
    st.markdown(
        """
        <style>
            .tpp-hero {
                background: #171f2d;
                border: 1px solid #2b3648;
                border-radius: 16px;
                padding: 1.2rem 1.4rem;
                height: 100%;
            }

            .tpp-kpi {
                background: #171f2d;
                border: 1px solid #2b3648;
                border-radius: 14px;
                padding: 0.8rem 1rem;
            }

            .tpp-kpi-label {
                color: #a3b1c9;
                font-size: 0.95rem;
                font-weight: 600;
            }

            .tpp-kpi-value {
                color: #e7ecf5;
                font-size: 2rem;
                font-weight: 800;
            }

            .tpp-alert {
                background: #123025;
                border: 1px solid #25543f;
                border-radius: 12px;
                padding: 1rem;
                color: #d7f5df;
                font-weight: 600;

                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 100%;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ------------------ DATA ------------------
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

    # ------------------ HERO + ALERT ------------------
    hero_col, alert_col = st.columns([2, 1], gap="large")

    with hero_col:
        with st.container(border=True):
            st.caption("TPP SMARTWATCH MONITOR")
            st.markdown("## Real-Time Thyrotoxic Risk Dashboard")
            st.write("Live physiological tracking with model-assisted risk forecasting for potential TPP attacks.")

    with alert_col:
        with st.container(border=True):
            st.markdown("### Monitoring Status")
            if latest_pred.severity_level in {"high", "critical"}:
                st.warning("Risk escalation detected. Keep patient at rest and increase monitoring frequency immediately.")
            elif latest_pred.severity_level == "moderate":
                st.info("Moderate risk trend observed. Continue close observation and avoid exertion spikes.")
            else:
                st.success("Stable Monitoring Window\n\nNo urgent alert pattern detected.")

    # ------------------ KPI ROW ------------------
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f"""
            <div class="tpp-kpi">
                <div class="tpp-kpi-label">Avg Heart Rate</div>
                <div class="tpp-kpi-value">{avg_hr} bpm</div>
                <div style="color:#98a7bf;">Current monitoring window</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f"""
            <div class="tpp-kpi">
                <div class="tpp-kpi-label">Avg HRV</div>
                <div class="tpp-kpi-value">{avg_hrv} ms</div>
                <div style="color:#98a7bf;">Higher is generally more resilient</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f"""
            <div class="tpp-kpi">
                <div class="tpp-kpi-label">High HR Events</div>
                <div class="tpp-kpi-value">{high_hr_events}</div>
                <div style="color:#98a7bf;">Heart rate ≥ 110 bpm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f"""
            <div class="tpp-kpi">
                <div class="tpp-kpi-label">Records Processed</div>
                <div class="tpp-kpi-value">{records_processed}</div>
                <div style="color:#98a7bf;">Loaded from backend</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------ LOWER SECTION ------------------
    left, right = st.columns([0.9, 1.4])

    with left:
        st.markdown("### Predicted TPP Risk")
        st.markdown(f"## {latest_pred.risk_score:.0%}")

        st.caption("Severity")
        st.markdown(f"### {latest_pred.severity_level.upper()}")

        st.caption("Timeline Window")
        st.markdown(f"### {latest_pred.predicted_timeline or 'N/A'}")

        st.markdown(latest_pred.recommendation)

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

        st.markdown(
            f"### Time-Series Monitoring <span style='float:right; color:#98a7bf; font-size:1rem;'>Last {len(chart_df)} points</span>",
            unsafe_allow_html=True,
        )

        st.line_chart(chart_df, use_container_width=True)

        st.caption(
            f"Latest: heartRate={latest_vitals.heart_rate or 0}, "
            f"hrv={latest_vitals.hrv or 0}, "
            f"steps={latest_vitals.steps or 0}"
        )

        st.markdown("</div>", unsafe_allow_html=True)