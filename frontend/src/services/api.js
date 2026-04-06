const toNum = (value, fallback = 0) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

export async function fetchWearableRecords() {
  const response = await fetch('/api/data')
  if (!response.ok) {
    throw new Error('Failed to fetch wearable records from backend')
  }

  const payload = await response.json()
  return Array.isArray(payload.data) ? payload.data : []
}

export async function fetchPrediction(records) {
  const normalized = records.map((item) => ({
    user_id: String(item.user_id || item.device || 'user-1'),
    timestamp: item.timestamp || new Date().toISOString(),
    heart_rate: toNum(item.heartRate ?? item.heart_rate ?? item.bpm, 0),
    steps: toNum(item.steps ?? item.step_count, 0),
    activity_intensity: toNum(item.activity_intensity ?? item.activity ?? 0, 0),
    sleep_duration_minutes: toNum(item.sleep_duration_minutes ?? item.sleep_duration ?? 0, 0),
    sleep_stage: item.sleep_stage || 'awake',
    is_sleeping: Boolean(item.is_sleeping ?? false),
  }))

  const response = await fetch('/api/v1/predict/realtime', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ records: normalized }),
  })

  if (!response.ok) {
    throw new Error('Prediction API is unavailable')
  }

  return response.json()
}
