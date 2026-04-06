const pct = (value) => `${Math.round((value || 0) * 100)}%`

export default function RiskPanel({ prediction }) {
  if (!prediction) {
    return (
      <section className="risk-panel">
        <h2>Predicted TPP Risk</h2>
        <p className="risk-empty">Upload or ingest data to generate a prediction.</p>
      </section>
    )
  }

  const severity = prediction.severity_level || 'low'
  return (
    <section className={`risk-panel severity-${severity}`}>
      <div>
        <h2>Predicted TPP Risk</h2>
        <p className="risk-score">{pct(prediction.risk_score)}</p>
      </div>
      <div className="risk-meta">
        <div>
          <span>Severity</span>
          <strong>{severity.toUpperCase()}</strong>
        </div>
        <div>
          <span>Timeline Window</span>
          <strong>{prediction.predicted_timeline_window || 'Not available'}</strong>
        </div>
      </div>
      <p className="risk-note">
        {prediction.recommendation ||
          'Use this score as early warning support and combine with medical guidance.'}
      </p>
    </section>
  )
}
