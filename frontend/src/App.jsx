import AlertsPanel from './components/AlertsPanel'
import MetricCard from './components/MetricCard'
import RiskPanel from './components/RiskPanel'
import TimeSeriesCharts from './components/TimeSeriesCharts'
import { useDashboardData } from './hooks/useDashboardData'

export default function App() {
  const {
    loading,
    error,
    metrics,
    chartData,
    prediction,
    alerts,
    refresh,
    isMockMode,
    enableMockMode,
    enableLiveMode,
    injectMockSpike,
  } = useDashboardData()

  return (
    <main className="dashboard-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">TPP SMARTWATCH MONITOR</p>
          <h1>Real-Time Thyrotoxic Risk Dashboard</h1>
          <p className="subtitle">
            Live physiological tracking with model-assisted risk forecasting for potential TPP attacks.
          </p>
        </div>
        <button className="refresh-btn" onClick={refresh} type="button">
          Refresh Data
        </button>
      </header>

      <section className="mode-controls">
        <div className="mode-state">
          Data Source:
          <strong>{isMockMode ? ' Mock Feed' : ' Live Backend'}</strong>
        </div>
        <div className="mode-actions">
          {isMockMode ? (
            <>
              <button className="mode-btn" onClick={injectMockSpike} type="button">
                Inject Risk Spike
              </button>
              <button className="mode-btn secondary" onClick={enableLiveMode} type="button">
                Switch to Live
              </button>
            </>
          ) : (
            <button className="mode-btn" onClick={enableMockMode} type="button">
              Use Mock Feed
            </button>
          )}
        </div>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}
      {loading ? <p className="loading">Loading monitoring feed...</p> : null}

      <section className="metrics-grid">
        <MetricCard label="Avg Heart Rate" value={`${metrics.avgHeartRate} bpm`} hint="Current monitoring window" />
        <MetricCard label="Avg HRV" value={`${metrics.avgHrv} ms`} hint="Higher is generally more resilient" />
        <MetricCard label="High HR Events" value={`${metrics.highHeartRateEvents}`} hint="Heart rate >= 110 bpm" />
        <MetricCard label="Records Processed" value={`${metrics.totalRecords}`} hint="Loaded from backend" />
      </section>

      <section className="dashboard-main-grid">
        <RiskPanel prediction={prediction} />
        <TimeSeriesCharts data={chartData} />
      </section>

      <AlertsPanel alerts={alerts} />
    </main>
  )
}
