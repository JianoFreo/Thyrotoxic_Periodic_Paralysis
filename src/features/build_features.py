"""Feature engineering for physiological and behavioral time-series signals.

Input: raw or minimally processed pandas DataFrame with timestamped smartwatch data.
Output: pandas DataFrame feature matrix that can be fed to an ML model.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureConfig:
    """Configuration for rolling windows and expected column names."""

    timestamp_col: str = "timestamp"
    user_col: str = "user_id"
    heart_rate_cols: tuple[str, ...] = ("heart_rate", "bpm", "hr")
    steps_cols: tuple[str, ...] = ("steps", "step_count")
    activity_cols: tuple[str, ...] = ("activity_intensity", "activity_level_score", "activity")
    sleep_duration_cols: tuple[str, ...] = ("sleep_duration_minutes", "sleep_minutes", "sleep_duration")
    sleep_stage_col: str = "sleep_stage"
    is_sleeping_col: str = "is_sleeping"
    rolling_windows: tuple[int, ...] = (5, 15, 60)


def _choose_col(dataframe: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for col in candidates:
        if col in dataframe.columns:
            return col
    return None


def _prepare_base_frame(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        raise ValueError("Input dataframe is empty.")

    features = dataframe.copy()

    if config.timestamp_col in features.columns:
        features[config.timestamp_col] = pd.to_datetime(features[config.timestamp_col], utc=True, errors="coerce")
    elif isinstance(features.index, pd.DatetimeIndex):
        features[config.timestamp_col] = pd.to_datetime(features.index, utc=True, errors="coerce")
    else:
        raise ValueError(
            "A timestamp column or DatetimeIndex is required for feature extraction."
        )

    features = features.dropna(subset=[config.timestamp_col]).sort_values(config.timestamp_col)

    if config.user_col not in features.columns:
        features[config.user_col] = "global"

    features = features.reset_index(drop=True)
    return features


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def add_hrv_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Add heart-rate and HRV surrogate features from HR time-series."""
    features = dataframe.copy()
    hr_col = _choose_col(features, config.heart_rate_cols)
    if hr_col is None:
        return features

    features["heart_rate"] = _safe_numeric(features[hr_col])
    rr_ms = 60000.0 / features["heart_rate"].clip(lower=1)

    # SDNN proxy from RR intervals in rolling windows.
    for window in config.rolling_windows:
        features[f"hrv_sdnn_w{window}"] = (
            rr_ms.groupby(features[config.user_col]).transform(
                lambda x: x.rolling(window=window, min_periods=max(2, window // 3)).std()
            )
        )

    rr_diff = rr_ms.groupby(features[config.user_col]).diff()
    for window in config.rolling_windows:
        features[f"hrv_rmssd_w{window}"] = (
            rr_diff.pow(2)
            .groupby(features[config.user_col])
            .transform(lambda x: x.rolling(window=window, min_periods=max(2, window // 3)).mean())
            .pow(0.5)
        )

    return features


def add_rolling_average_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Add rolling means and standard deviations for key physiological signals."""
    features = dataframe.copy()

    signal_map = {
        "heart_rate": _choose_col(features, config.heart_rate_cols),
        "steps": _choose_col(features, config.steps_cols),
        "activity_intensity": _choose_col(features, config.activity_cols),
    }

    for canonical_name, original_col in signal_map.items():
        if original_col is None:
            continue

        values = _safe_numeric(features[original_col])
        features[canonical_name] = values

        for window in config.rolling_windows:
            min_points = max(1, window // 3)
            features[f"{canonical_name}_roll_mean_w{window}"] = (
                values.groupby(features[config.user_col]).transform(
                    lambda x: x.rolling(window=window, min_periods=min_points).mean()
                )
            )
            features[f"{canonical_name}_roll_std_w{window}"] = (
                values.groupby(features[config.user_col]).transform(
                    lambda x: x.rolling(window=window, min_periods=min_points).std()
                )
            )

    return features


def add_rate_of_change_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Add first-order and percentage change features."""
    features = dataframe.copy()

    candidate_columns = {
        "heart_rate": _choose_col(features, config.heart_rate_cols),
        "steps": _choose_col(features, config.steps_cols),
        "activity_intensity": _choose_col(features, config.activity_cols),
    }

    for name, col in candidate_columns.items():
        if col is None:
            continue

        series = _safe_numeric(features[col])
        grouped = series.groupby(features[config.user_col])
        features[f"{name}_diff_1"] = grouped.diff(1)
        features[f"{name}_diff_5"] = grouped.diff(5)
        features[f"{name}_pct_change_1"] = grouped.pct_change(1).replace([np.inf, -np.inf], np.nan)

    return features


def add_circadian_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Encode time-of-day and day-of-week periodic patterns."""
    features = dataframe.copy()
    ts = features[config.timestamp_col]

    hour = ts.dt.hour + (ts.dt.minute / 60.0)
    dow = ts.dt.dayofweek

    features["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    features["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    features["dow_sin"] = np.sin(2 * np.pi * dow / 7.0)
    features["dow_cos"] = np.cos(2 * np.pi * dow / 7.0)
    features["is_weekend"] = (dow >= 5).astype(int)
    features["is_night"] = ((ts.dt.hour >= 22) | (ts.dt.hour <= 5)).astype(int)

    return features


def add_activity_level_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Derive activity level and movement-intensity features."""
    features = dataframe.copy()

    steps_col = _choose_col(features, config.steps_cols)
    activity_col = _choose_col(features, config.activity_cols)

    if steps_col is not None:
        steps = _safe_numeric(features[steps_col]).fillna(0)
        features["steps"] = steps
        features["active_flag"] = (steps > 0).astype(int)
        features["high_steps_flag"] = (steps >= steps.quantile(0.75)).astype(int)

    if activity_col is not None:
        intensity = _safe_numeric(features[activity_col])
        features["activity_intensity"] = intensity
        if intensity.notna().any():
            q1, q2 = intensity.quantile([0.33, 0.66])
            features["activity_level_bin"] = pd.cut(
                intensity,
                bins=[-np.inf, q1, q2, np.inf],
                labels=[0, 1, 2],
            ).astype("float")

    return features


def add_sleep_features(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Create sleep quantity and stage-distribution features."""
    features = dataframe.copy()

    duration_col = _choose_col(features, config.sleep_duration_cols)
    if duration_col is not None:
        sleep_minutes = _safe_numeric(features[duration_col]).fillna(0)
        features["sleep_duration_minutes"] = sleep_minutes
        features["sleep_duration_hours"] = sleep_minutes / 60.0

        # 24-hour rolling cumulative sleep quantity.
        features["sleep_rolling_24h_hours"] = (
            features.groupby(config.user_col)["sleep_duration_hours"]
            .transform(lambda x: x.rolling(window=96, min_periods=1).sum())
        )

    if config.is_sleeping_col in features.columns:
        sleeping = features[config.is_sleeping_col].astype(int)
        features["is_sleeping"] = sleeping
        features["sleep_episode_change"] = sleeping.groupby(features[config.user_col]).diff().fillna(0)

    if config.sleep_stage_col in features.columns:
        sleep_stage = features[config.sleep_stage_col].astype(str).str.lower()
        dummies = pd.get_dummies(sleep_stage, prefix="sleep_stage", dtype=float)
        features = pd.concat([features, dummies], axis=1)

        stage_cols = [col for col in dummies.columns]
        if stage_cols:
            for col in stage_cols:
                features[f"{col}_roll_mean_w15"] = (
                    features[col]
                    .groupby(features[config.user_col])
                    .transform(lambda x: x.rolling(window=15, min_periods=1).mean())
                )

    return features


def finalize_feature_matrix(dataframe: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Keep numeric model features and preserve time/user identifiers."""
    features = dataframe.copy()

    id_cols = [col for col in (config.user_col, config.timestamp_col) if col in features.columns]
    numeric_cols = features.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    selected_cols = id_cols + [col for col in numeric_cols if col not in id_cols]

    matrix = features[selected_cols].copy()
    if id_cols:
        matrix = matrix.sort_values(id_cols).reset_index(drop=True)
    else:
        matrix = matrix.reset_index(drop=True)

    # Forward/backward fill inside each user stream for short gaps.
    feature_cols = [col for col in matrix.columns if col not in id_cols]
    if config.user_col in matrix.columns and feature_cols:
        matrix[feature_cols] = (
            matrix.groupby(config.user_col, group_keys=False)[feature_cols]
            .apply(lambda x: x.ffill().bfill())
        )
    elif feature_cols:
        matrix[feature_cols] = matrix[feature_cols].ffill().bfill()

    matrix[feature_cols] = matrix[feature_cols].fillna(0.0)
    return matrix


def build_features(data: pd.DataFrame, config: FeatureConfig | None = None) -> pd.DataFrame:
    """Transform raw wearable time-series data into an ML-ready feature matrix.

    Parameters
    ----------
    data
        Raw time-series dataframe containing timestamped physiological signals.
    config
        Optional FeatureConfig for custom column names and windows.

    Returns
    -------
    pd.DataFrame
        Feature matrix with engineered numeric features plus user/timestamp keys.
    """
    cfg = config or FeatureConfig()

    features = _prepare_base_frame(data, cfg)
    features = add_hrv_features(features, cfg)
    features = add_rolling_average_features(features, cfg)
    features = add_rate_of_change_features(features, cfg)
    features = add_circadian_features(features, cfg)
    features = add_activity_level_features(features, cfg)
    features = add_sleep_features(features, cfg)
    return finalize_feature_matrix(features, cfg)