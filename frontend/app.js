const sections = [
  { key: 'overview', label: 'Overview' },
  { key: 'monitoring', label: 'Patient Monitoring' },
  { key: 'upload', label: 'Data Upload' },
  { key: 'insights', label: 'Model Insights' },
  { key: 'settings', label: 'Settings' },
]

const readings = [
  { label: 'Avg Resting HR', value: '72 bpm', change: '+3 vs last week' },
  { label: 'Nocturnal HRV', value: '58 ms', change: 'stable' },
  { label: 'Episodes Flagged', value: '2 in 24h', change: 'watch' },
  { label: 'Sync Health', value: '96% of devices' },
]

const patients = [
  {
    name: 'Sam R.',
    device: 'Apple Watch',
    status: 'watch',
    lastSync: '6 min ago',
    hr: 102,
  },
  {
    name: 'Avery L.',
    device: 'Fitbit',
    status: 'stable',
    lastSync: '18 min ago',
    hr: 76,
  },
  {
    name: 'Dana K.',
    device: 'Galaxy Watch',
    status: 'alert',
    lastSync: '2 min ago',
    hr: 118,
  },
]

const uploads = [
  { name: 'Watch HR JSON', size: '2.4 MB', time: 'just now' },
  { name: 'Clinical lab CSV', size: '640 KB', time: '1h ago' },
  { name: 'Manual note', size: '2 KB', time: 'yesterday' },
]

let activeSection = 'overview'

const root = document.getElementById('app')

function render() {
  if (!root) return

  const sectionTitle = sections.find((s) => s.key === activeSection)?.label ?? 'Overview'

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
        ${sections
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
          ${renderSection(activeSection)}
        </section>

        <aside class="aside">
          <h3>Recent Signals</h3>
          <div class="panel-header">
            <h2>${sectionTitle}</h2>
            <span class="badge">Sample data only</span>
          </div>
          <ul class="list">
            ${readings
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
          <div class="card">
            <p class="muted small">
              <!-- When the ML backend is ready, connect the watch ingestion endpoint here. Until then,
              use the mock upload area to stage CSV/JSON samples. -->
              connect the watch ingestion endpoint here.
            </p>
          </div>
        </aside>
      </main>
    </div>
  `

  attachTabHandlers()
}

function renderSection(section) {
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
      return `
        <div class="stack">
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
      return `
        <div class="stack">
          <div class="dropzone" role="button" tabindex="0">
            <p class="muted">Drop CSV/JSON here or click to browse</p>
            <p class="small">Accepts watch heart-rate streams and symptom logs</p>
          </div>
          <div class="table">
            <div class="table-head">
              <span>File</span>
              <span>Size</span>
              <span>When</span>
            </div>
            ${uploads
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

function attachTabHandlers() {
  const buttons = root.querySelectorAll('[data-section]')
  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-section')
      if (target) {
        activeSection = target
        render()
      }
    })
  })
}

render()
