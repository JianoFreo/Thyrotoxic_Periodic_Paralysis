// Renderer - Handles all UI rendering
class Renderer {
  constructor(dataManager) {
    this.dataManager = dataManager
  }

  renderSection(section) {
    switch (section) {
      case 'overview':
        return `
          <div class="grid">
            <div class="card">
              <h3>Goal</h3>
              <p>
                Provide an early warning layer for TPP by fusing smartwatch pulse data with lab and
                symptom diaries. Start simple: stable ingestion, basic heuristics, then layer deep
                learning.
              </p>
            </div>
            <div class="card">
              <h3>Ingestion</h3>
              <p>
                Accepts JSON or CSV from Apple Watch, Fitbit, Galaxy Watch, or raw Bluetooth LE
                exports. Current mode stores samples locally for demo.
              </p>
            </div>
            <div class="card">
              <h3>Roadmap</h3>
              <ul class="bullets">
                <li>Hook watch webhook → normalize HR, HRV, temp</li>
                <li>Train first anomaly detector on resting HR drift</li>
                <li>Add clinician notes and lab overlays</li>
              </ul>
            </div>
          </div>
        `
      case 'monitoring':
        const patients = this.dataManager.getPatients()
        return `
          <div class="stack">
            ${patients.length > 0 ? `
              <div class="table">
                <div class="table-head">
                  <span>Patient</span>
                  <span>Device</span>
                  <span>Status</span>
                  <span>Last sync</span>
                  <span>HR</span>
                </div>
                ${patients
                  .map(
                    (p) => `
                      <div class="table-row">
                        <span>${p.name}</span>
                        <span class="muted">${p.device}</span>
                        <span class="status ${p.status}">${p.status}</span>
                        <span class="muted">${p.lastSync}</span>
                        <span>${p.hr} bpm</span>
                      </div>
                    `,
                  )
                  .join('')}
              </div>
            ` : `
              <div class="empty-state">
                <h3>No Monitoring Data</h3>
                <p class="muted">Upload smartwatch data to start monitoring patient vitals</p>
                <p class="small muted">Go to Data Upload to get started</p>
              </div>
            `}
            <div class="card">
              <h4>Simple heuristic</h4>
              <p class="muted small">
                Alerts fire when resting HR exceeds baseline by 15% for 10+ minutes or when HRV dips
                below 30 ms. Replace this with your model outputs when ready.
              </p>
            </div>
          </div>
        `
      case 'upload':
        const uploadedData = this.dataManager.getUploadedData()
        return `
          <div class="stack">
            <input type="file" id="fileInput" accept=".csv,.json" style="display: none;" />
            <div class="dropzone" id="dropzone" role="button" tabindex="0">
              <p class="muted">Drop CSV/JSON here or click to browse</p>
              <p class="small">Accepts watch heart-rate streams and symptom logs</p>
            </div>
            ${this.dataManager.getUploads().length > 0 ? `
              <div class="table">
                <div class="table-head">
                  <span>File</span>
                  <span>Size</span>
                  <span>When</span>
                </div>
                ${this.dataManager.getUploads()
                  .map(
                    (file) => `
                      <div class="table-row">
                        <span>${file.name}</span>
                        <span class="muted">${file.size}</span>
                        <span class="muted">${file.time}</span>
                      </div>
                    `,
                  )
                  .join('')}
              </div>
            ` : `
              <div class="empty-state">
                <h3>No Files Uploaded Yet</h3>
                <p class="muted">Upload your first CSV or JSON file to begin tracking</p>
              </div>
            `}
            ${uploadedData.length > 0 ? `
              <div class="card">
                <h4>Uploaded Data Preview</h4>
                <div style="max-height: 300px; overflow: auto;">
                  <pre style="font-size: 12px;">${JSON.stringify(uploadedData.slice(0, 10), null, 2)}</pre>
                  ${uploadedData.length > 10 ? `<p class="muted small">Showing first 10 of ${uploadedData.length} records</p>` : ''}
                </div>
              </div>
            ` : ''}
          </div>
        `
      case 'insights':
        return `
          <div class="card">
            <h3>Model placeholder</h3>
            <p class="muted">
              This area will render risk curves, feature attributions, and episodic forecasts once the
              deep learning service is wired in. For now, it shows a static placeholder to keep the
              layout ready.
            </p>
            <div class="placeholder">Future chart</div>
          </div>
        `
      case 'settings':
        return `
          <div class="grid two">
            <div class="card">
              <h4>Device sources</h4>
              <ul class="bullets">
                <li>Apple Health webhook URL</li>
                <li>Fitbit nightly export</li>
                <li>Manual CSV upload</li>
              </ul>
            </div>
            <div class="card">
              <h4>Notification rules</h4>
              <p class="muted small">
                Set who gets notified when an alert fires. When backend is live, map alerts to SMS,
                email, or pager.
              </p>
            </div>
          </div>
        `
      default:
        return ''
    }
  }

  render(root, activeSection) {
    if (!root) return

    const sectionTitle = this.dataManager.getSections().find((s) => s.key === activeSection)?.label ?? 'Overview'

    root.innerHTML = `
      <div class="page">
        <header class="topbar">
          <div>
            <p class="eyebrow">Thyrotoxic Periodic Paralysis</p>
            <h1>Proactive Monitoring</h1>
            <p class="muted">
              Lightweight dashboard to stage the future deep-learning pipeline for
              predicting hyperthyroid-related paralysis episodes.
            </p>
          </div>
          <div class="status-chip">Pilot</div>
        </header>

        <nav class="tabs" aria-label="Sections">
          ${this.dataManager.getSections()
            .map(
              ({ key, label }) => `
                <button
                  class="${key === activeSection ? 'tab active' : 'tab'}"
                  data-section="${key}"
                >
                  ${label}
                </button>
              `,
            )
            .join('')}
        </nav>

        <main class="layout">
          <section class="panel">
            <div class="panel-header">
              <h2>${sectionTitle}</h2>
              <span class="badge">Sample data only</span>
            </div>
            ${this.renderSection(activeSection)}
          </section>

          <aside class="aside">
            <h3>Recent Signals</h3>
            <div class="panel-header">
              <h2>${sectionTitle}</h2>
              <span class="badge">Sample data only</span>
            </div>
            ${this.dataManager.getReadings().length > 0 && this.dataManager.getReadings()[0].value !== '0' ? `
              <ul class="list">
                ${this.dataManager.getReadings()
                  .map(
                    (item) => `
                      <li class="list-row">
                        <div>
                          <p class="label">${item.label}</p>
                          <p class="value">${item.value}</p>
                        </div>
                        ${item.change ? `<span class="pill">${item.change}</span>` : ''}
                      </li>
                    `,
                  )
                  .join('')}
              </ul>
            ` : `
              <div class="empty-state">
                <p class="muted">No signals yet</p>
                <p class="small">Upload data to see vital statistics</p>
              </div>
            `}
            <div class="card">
              <p class="muted small">
                connect the watch ingestion endpoint here.
              </p>
            </div>
          </aside>
        </main>
      </div>
    `
  }
}
