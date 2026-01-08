"""
TPP Utilities Module

Common utilities for Thyrotoxic Periodic Paralysis data analysis.
Provides data validation, processing, and helper functions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json


class DataValidator:
    """Validate TPP monitoring data for required fields and formats."""
    
    REQUIRED_FIELDS = ['timestamp', 'heartRate', 'hrv', 'activity']
    OPTIONAL_FIELDS = ['device', 'temperature']
    VALID_ACTIVITIES = ['resting', 'walking', 'exercise', 'sleeping']
    
    @staticmethod
    def validate_record(record: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate a single data record.
        
        Args:
            record: Dictionary containing monitoring data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        for field in DataValidator.REQUIRED_FIELDS:
            if field not in record:
                return False, f"Missing required field: {field}"
        
        # Validate timestamp
        try:
            pd.to_datetime(record['timestamp'])
        except Exception as e:
            return False, f"Invalid timestamp: {e}"
        
        # Validate heart rate (30-220 bpm is reasonable range)
        hr = record['heartRate']
        if not isinstance(hr, (int, float)) or hr < 30 or hr > 220:
            return False, f"Heart rate out of valid range (30-220): {hr}"
        
        # Validate HRV (must be positive)
        hrv = record['hrv']
        if not isinstance(hrv, (int, float)) or hrv < 0:
            return False, f"Invalid HRV value: {hrv}"
        
        # Validate activity
        activity = record['activity']
        if activity not in DataValidator.VALID_ACTIVITIES:
            return False, f"Invalid activity: {activity}. Must be one of {DataValidator.VALID_ACTIVITIES}"
        
        # Validate optional temperature if present
        if 'temperature' in record:
            temp = record['temperature']
            if temp is not None and (not isinstance(temp, (int, float)) or temp < 30 or temp > 45):
                return False, f"Temperature out of valid range (30-45°C): {temp}"
        
        return True, None
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate a DataFrame of monitoring data.
        
        Args:
            df: DataFrame containing monitoring data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns
        for field in DataValidator.REQUIRED_FIELDS:
            if field not in df.columns:
                errors.append(f"Missing required column: {field}")
        
        if errors:
            return False, errors
        
        # Validate each record
        for idx, row in df.iterrows():
            is_valid, error = DataValidator.validate_record(row.to_dict())
            if not is_valid:
                errors.append(f"Row {idx}: {error}")
        
        return len(errors) == 0, errors


class DataProcessor:
    """Process and transform TPP monitoring data."""
    
    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features to the DataFrame.
        
        Args:
            df: DataFrame with 'timestamp' column
            
        Returns:
            DataFrame with additional time features
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        return df
    
    @staticmethod
    def calculate_rolling_stats(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """
        Calculate rolling statistics for heart rate and HRV.
        
        Args:
            df: DataFrame with 'heartRate' and 'hrv' columns
            window: Window size for rolling calculations
            
        Returns:
            DataFrame with additional rolling statistic columns
        """
        df = df.copy()
        
        # Ensure data is sorted by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Rolling mean
        df['hr_rolling_mean'] = df['heartRate'].rolling(window=window, min_periods=1).mean()
        df['hrv_rolling_mean'] = df['hrv'].rolling(window=window, min_periods=1).mean()
        
        # Rolling std
        df['hr_rolling_std'] = df['heartRate'].rolling(window=window, min_periods=1).std()
        df['hrv_rolling_std'] = df['hrv'].rolling(window=window, min_periods=1).std()
        
        return df
    
    @staticmethod
    def detect_rapid_changes(df: pd.DataFrame, threshold: float = 20.0) -> pd.DataFrame:
        """
        Detect rapid changes in heart rate.
        
        Args:
            df: DataFrame with 'heartRate' column
            threshold: Threshold for rapid change detection (bpm)
            
        Returns:
            DataFrame with 'rapid_change' flag column
        """
        df = df.copy()
        
        # Ensure data is sorted by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Calculate heart rate change
        df['hr_change'] = df['heartRate'].diff().abs()
        df['rapid_change'] = (df['hr_change'] > threshold).astype(int)
        
        return df


class SyntheticDataGenerator:
    """Generate synthetic monitoring data for testing."""
    
    @staticmethod
    def generate_daily_pattern(
        date: datetime,
        num_records: int = 48,
        base_hr: int = 70,
        noise_level: float = 5.0
    ) -> List[Dict]:
        """
        Generate synthetic data with realistic daily patterns.
        
        Args:
            date: Start date for the data
            num_records: Number of records to generate
            base_hr: Base heart rate (bpm)
            noise_level: Amount of random noise to add
            
        Returns:
            List of data records
        """
        np.random.seed(int(date.timestamp()) % 1000)
        
        records = []
        time_interval = timedelta(minutes=30)
        
        for i in range(num_records):
            timestamp = date + (time_interval * i)
            hour = timestamp.hour
            
            # Realistic activity and heart rate patterns
            if 0 <= hour < 6:
                activity = 'sleeping'
                hr = base_hr - 20 + np.random.normal(0, 3)
                hrv = 70 + np.random.normal(0, 10)
            elif 6 <= hour < 8:
                activity = 'resting'
                hr = base_hr - 10 + np.random.normal(0, 5)
                hrv = 60 + np.random.normal(0, 8)
            elif 8 <= hour < 12:
                activity = np.random.choice(['walking', 'resting', 'exercise'], p=[0.5, 0.4, 0.1])
                if activity == 'exercise':
                    hr = base_hr + 40 + np.random.normal(0, 10)
                    hrv = 30 + np.random.normal(0, 5)
                elif activity == 'walking':
                    hr = base_hr + 15 + np.random.normal(0, 8)
                    hrv = 45 + np.random.normal(0, 8)
                else:
                    hr = base_hr + np.random.normal(0, 5)
                    hrv = 55 + np.random.normal(0, 8)
            elif 12 <= hour < 18:
                activity = np.random.choice(['walking', 'resting'], p=[0.6, 0.4])
                hr = base_hr + (10 if activity == 'walking' else 0) + np.random.normal(0, 8)
                hrv = 50 + np.random.normal(0, 10)
            elif 18 <= hour < 22:
                activity = 'resting'
                hr = base_hr - 5 + np.random.normal(0, 5)
                hrv = 55 + np.random.normal(0, 8)
            else:
                activity = 'sleeping'
                hr = base_hr - 15 + np.random.normal(0, 3)
                hrv = 65 + np.random.normal(0, 8)
            
            # Add noise
            hr += np.random.normal(0, noise_level)
            hr = max(40, min(200, int(hr)))  # Clamp to reasonable range
            hrv = max(10, int(hrv))  # Ensure positive HRV
            
            record = {
                'timestamp': timestamp.isoformat(),
                'heartRate': hr,
                'hrv': hrv,
                'activity': activity,
                'device': 'Synthetic Generator'
            }
            
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_tpp_episode(
        start_time: datetime,
        duration_minutes: int = 120
    ) -> List[Dict]:
        """
        Generate synthetic data simulating a TPP episode.
        
        Args:
            start_time: Start time of the episode
            duration_minutes: Duration of the episode
            
        Returns:
            List of data records showing TPP episode pattern
        """
        records = []
        interval = timedelta(minutes=5)
        num_records = duration_minutes // 5
        
        for i in range(num_records):
            timestamp = start_time + (interval * i)
            progress = i / num_records  # 0 to 1
            
            # Simulate TPP: low HR during episode, gradual recovery
            if progress < 0.3:  # Episode onset
                hr = 45 + int(15 * (1 - progress / 0.3))
                hrv = 20 + int(10 * progress / 0.3)
                activity = 'resting'
            elif progress < 0.7:  # Peak episode
                hr = 40 + np.random.randint(-5, 5)
                hrv = 15 + np.random.randint(-3, 3)
                activity = 'resting'
            else:  # Recovery
                recovery_progress = (progress - 0.7) / 0.3
                hr = 45 + int(25 * recovery_progress)
                hrv = 20 + int(30 * recovery_progress)
                activity = 'resting'
            
            record = {
                'timestamp': timestamp.isoformat(),
                'heartRate': hr,
                'hrv': hrv,
                'activity': activity,
                'device': 'TPP Episode Simulator'
            }
            
            records.append(record)
        
        return records


def load_monitoring_data(file_path: str) -> pd.DataFrame:
    """
    Load monitoring data from CSV or JSON file.
    
    Args:
        file_path: Path to data file
        
    Returns:
        DataFrame containing the data
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    # Convert timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df


def save_monitoring_data(df: pd.DataFrame, file_path: str):
    """
    Save monitoring data to CSV or JSON file.
    
    Args:
        df: DataFrame to save
        file_path: Output file path
    """
    if file_path.endswith('.csv'):
        df.to_csv(file_path, index=False)
    elif file_path.endswith('.json'):
        # Convert timestamp to ISO string
        df_copy = df.copy()
        if 'timestamp' in df_copy.columns:
            df_copy['timestamp'] = df_copy['timestamp'].astype(str)
        
        data = df_copy.to_dict('records')
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
