"""
Data models for TPP monitoring system.

Provides POJO-like classes for vitals input and predictions (similar to Java reference).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VitalsInput:
    """User-provided physiological metrics."""
    user_id: str
    heart_rate: Optional[int] = None
    hrv: Optional[int] = None
    steps: Optional[int] = None
    activity_intensity: Optional[int] = None
    sleep_duration_mins: Optional[int] = None
    sleep_stage: Optional[str] = None
    is_sleeping: bool = False
    source: str = "manual"  # 'manual', 'smartwatch', 'mock'
    input_id: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Prediction:
    """TPP risk prediction output."""
    input_id: str
    risk_score: float
    severity_level: str  # 'low', 'moderate', 'high', 'critical'
    predicted_timeline: Optional[str] = None
    recommendation: Optional[str] = None
    model_version: str = "baseline-1.0"
    processing_time_ms: Optional[int] = None
    prediction_id: Optional[str] = None
    created_at: Optional[str] = None
