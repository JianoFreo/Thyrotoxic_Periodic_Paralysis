# Sample Data Files

Test files for TPP monitoring system. Use these to test the upload feature.

## Files

1. **heart-rate-sample.json** - Daytime heart rate data (8 records)
2. **heart-rate-sample.csv** - Extended daytime data (12 records)  
3. **night-monitoring.json** - Overnight sleep monitoring (5 records)

## How to Use

1. Start the app: `npm start`
2. Open frontend: http://localhost:8080
3. Go to "Data Upload" tab
4. Upload any of these sample files
5. Check the preview to see parsed data

## Data Fields

- `timestamp` - ISO 8601 datetime
- `heartRate` - Beats per minute (bpm)
- `hrv` - Heart rate variability (ms)
- `activity` - Activity type (resting, walking, exercise, sleeping)
- `device` - Smartwatch model
- `temperature` - Body temperature (°C, optional)
