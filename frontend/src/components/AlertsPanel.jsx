export default function AlertsPanel({ alerts }) {
  return (
    <section className="alerts-panel">
      <header className="panel-head">
        <h3>Alerts and Recommendations</h3>
      </header>
      <div className="alerts-list">
        {alerts.map((alert, index) => (
          <article key={`${alert.title}-${index}`} className={`alert-card alert-${alert.type}`}>
            <h4>{alert.title}</h4>
            <p>{alert.detail}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
