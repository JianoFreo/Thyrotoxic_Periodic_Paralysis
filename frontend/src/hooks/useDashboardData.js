import { useCallback, useEffect, useMemo, useState } from 'react'
import { fetchPrediction, fetchWearableRecords } from '../services/api'

const toNum = (value, fallback = 0) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

const computeRiskFallback = (record) => {
  const hr = toNum(record.heartRate ?? record.heart_rate ?? record.bpm)
  const steps = toNum(record.steps ?? record.step_count)
  const hrv = toNum(record.hrv)

  let risk = 0.1
  if (hr > 110) risk += 0.3
  if (hr > 130) risk += 0.2
  if (steps < 20) risk += 0.15
  if (hrv > 0 && hrv < 25) risk += 0.25
  return Math.min(0.95, Math.max(0.05, risk))
}

const severityFromScore = (score) => {
  if (score >= 0.85) return 'critical'
  if (score >= 0.65) return 'high'
  if (score >= 0.35) return 'moderate'
  return 'low'
}

const timelineFromSeverity = (severity) => {
  if (severity === 'critical') return '0-3 hours'
  if (severity === 'high') return '3-12 hours'
  if (severity === 'moderate') return '12-24 hours'
  return '24-72 hours'
}

const recommendationFromSeverity = (severity) => {
  if (severity === 'critical') {
    return 'High-risk signature detected. Prioritize immediate rest, avoid exertion, and follow emergency care plan.'
  }
  if (severity === 'high') {
    return 'Elevated risk trend observed. Limit intense activity and monitor symptoms every 30 minutes.'
  }
  if (severity === 'moderate') {
    return 'Moderate risk. Continue hydration, maintain regular checks, and avoid sudden workload spikes.'
  }
  return 'Low risk currently. Keep routine monitoring and maintain medication adherence.'
}

const randomBetween = (min, max) => min + Math.random() * (max - min)

const createMockRecord = (timestamp, prev) => {
  const baselineHeartRate = prev ? toNum(prev.heart_rate ?? prev.heartRate, 84) : 84
  const baselineHrv = prev ? toNum(prev.hrv, 38) : 38

  const heartRate = Math.max(58, Math.round(baselineHeartRate + randomBetween(-6, 7)))
  const hrv = Math.max(12, Math.round(baselineHrv + randomBetween(-3, 3)))
  const steps = Math.max(0, Math.round(randomBetween(0, 70)))

  return {
    user_id: 'mock-user-1',
    timestamp,
    heart_rate: heartRate,
    hrv,
    steps,
  }
}

const createMockDataset = (count = 80) => {
  const now = Date.now()
  const out = []
  for (let i = 0; i < count; i += 1) {
    const timestamp = new Date(now - (count - i) * 60_000).toISOString()
    const previous = out.length > 0 ? out[out.length - 1] : null
    out.push(createMockRecord(timestamp, previous))
  }
  return out
}

const appendMockPoint = (records) => {
  const previous = records.length > 0 ? records[records.length - 1] : null
  const next = createMockRecord(new Date().toISOString(), previous)
  return [...records.slice(-119), next]
}

const buildFallbackPrediction = (records) => {
  if (!records.length) return null
  const latest = records[records.length - 1]
  const riskScore = computeRiskFallback(latest)
  const severityLevel = severityFromScore(riskScore)
  return {
    risk_score: riskScore,
    severity_level: severityLevel,
    predicted_timeline_window: timelineFromSeverity(severityLevel),
    recommendation: recommendationFromSeverity(severityLevel),
    source: 'fallback',
  }
}

export function useDashboardData(pollIntervalMs = 10000) {
  const [records, setRecords] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dataMode, setDataMode] = useState('live')

  const loadData = useCallback(async () => {
    if (dataMode === 'mock') {
      setError('')
      setLoading(false)
      setRecords((prev) => {
        const nextRecords = prev.length > 0 ? appendMockPoint(prev) : createMockDataset()
        setPrediction(buildFallbackPrediction(nextRecords))
        return nextRecords
      })
      return
    }

    try {
      setError('')
      const data = await fetchWearableRecords()
      setRecords(data)

      if (data.length > 0) {
        const recent = data.slice(-60)
        try {
          const remotePrediction = await fetchPrediction(recent)
          setPrediction(remotePrediction)
        } catch {
          setPrediction(buildFallbackPrediction(recent))
        }
      } else {
        setPrediction(null)
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [dataMode])

  useEffect(() => {
    loadData()
    const id = setInterval(loadData, pollIntervalMs)
    return () => clearInterval(id)
  }, [loadData, pollIntervalMs])

  const enableMockMode = useCallback(() => {
    const initial = createMockDataset()
    setDataMode('mock')
    setError('')
    setLoading(false)
    setRecords(initial)
    setPrediction(buildFallbackPrediction(initial))
  }, [])

  const enableLiveMode = useCallback(() => {
    setDataMode('live')
    setLoading(true)
    setError('')
  }, [])

  const injectMockSpike = useCallback(() => {
    if (dataMode !== 'mock') return

    setRecords((prev) => {
      const baseline = prev.length > 0 ? prev : createMockDataset()
      const spike = {
        user_id: 'mock-user-1',
        timestamp: new Date().toISOString(),
        heart_rate: Math.round(randomBetween(138, 156)),
        hrv: Math.round(randomBetween(14, 21)),
        steps: Math.round(randomBetween(0, 9)),
      }
      const nextRecords = [...baseline.slice(-119), spike]
      setPrediction(buildFallbackPrediction(nextRecords))
      return nextRecords
    })
  }, [dataMode])

  const metrics = useMemo(() => {
    if (records.length === 0) {
      return {
        totalRecords: 0,
        avgHeartRate: 0,
        avgHrv: 0,
        highHeartRateEvents: 0,
      }
    }

    const heartRates = records
      .map((r) => toNum(r.heartRate ?? r.heart_rate ?? r.bpm, NaN))
      .filter((n) => Number.isFinite(n) && n > 0)

    const hrvValues = records
      .map((r) => toNum(r.hrv, NaN))
      .filter((n) => Number.isFinite(n) && n > 0)

    const avgHeartRate = heartRates.length
      ? Math.round(heartRates.reduce((a, b) => a + b, 0) / heartRates.length)
      : 0

    const avgHrv = hrvValues.length
      ? Math.round(hrvValues.reduce((a, b) => a + b, 0) / hrvValues.length)
      : 0

    return {
      totalRecords: records.length,
      avgHeartRate,
      avgHrv,
      highHeartRateEvents: heartRates.filter((v) => v >= 110).length,
    }
  }, [records])

  const chartData = useMemo(() => {
    return records.slice(-120).map((item, idx) => ({
      idx,
      time: item.timestamp || `${idx}`,
      heartRate: toNum(item.heartRate ?? item.heart_rate ?? item.bpm),
      hrv: toNum(item.hrv),
      steps: toNum(item.steps ?? item.step_count),
    }))
  }, [records])

  const alerts = useMemo(() => {
    if (!prediction) return []

    const severity = prediction.severity_level || 'low'
    const alertsList = []

    if (severity === 'critical') {
      alertsList.push({
        type: 'critical',
        title: 'Critical Risk Detected',
        detail: 'Potential TPP attack window is very near. Follow emergency protocol now.',
      })
    } else if (severity === 'high') {
      alertsList.push({
        type: 'high',
        title: 'High Risk Trend',
        detail: 'Risk score is elevated and requires close monitoring over the next few hours.',
      })
    }

    if (metrics.highHeartRateEvents > 10) {
      alertsList.push({
        type: 'warning',
        title: 'Frequent Tachycardia Events',
        detail: `${metrics.highHeartRateEvents} high heart-rate records detected in current dataset.`,
      })
    }

    if (alertsList.length === 0) {
      alertsList.push({
        type: 'ok',
        title: 'Stable Monitoring Window',
        detail: 'No urgent alert pattern detected from the latest records.',
      })
    }

    return alertsList
  }, [prediction, metrics.highHeartRateEvents])

  return {
    loading,
    error,
    dataMode,
    isMockMode: dataMode === 'mock',
    records,
    metrics,
    chartData,
    prediction,
    alerts,
    refresh: loadData,
    enableMockMode,
    enableLiveMode,
    injectMockSpike,
  }
}
