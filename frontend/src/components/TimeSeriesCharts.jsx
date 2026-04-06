import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function TimeSeriesCharts({ data }) {
  return (
    <section className="chart-panel">
      <header className="panel-head">
        <h3>Time-Series Monitoring</h3>
        <span>Last {data.length} points</span>
      </header>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 12, right: 18, left: 6, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(130,145,166,0.25)" />
            <XAxis dataKey="idx" tick={{ fill: '#6a7888', fontSize: 11 }} />
            <YAxis yAxisId="left" tick={{ fill: '#6a7888', fontSize: 11 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fill: '#6a7888', fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="heartRate" stroke="#ea4f4f" strokeWidth={2} dot={false} />
            <Line yAxisId="left" type="monotone" dataKey="hrv" stroke="#3da5ff" strokeWidth={2} dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="steps" stroke="#11bf86" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
