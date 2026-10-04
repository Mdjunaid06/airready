import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getComparison } from '../lib/api'

export default function Comparison() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getComparison().then(setData).catch(() => setError('Could not load comparison data.'))
  }, [])

  if (error) return <div className="p-8 text-urgent">{error}</div>
  if (!data) return <div className="p-8 text-textMuted">Loading comparison…</div>

  const chartData = [
    {
      metric: 'Missed failures',
      'Fixed-interval': data.fixed_interval_missed_failures,
      'Predictive (AirReady)': data.predictive_missed_failures,
    },
    {
      metric: 'Unnecessary services',
      'Fixed-interval': data.fixed_interval_unnecessary_services,
      'Predictive (AirReady)': data.predictive_unnecessary_services,
    },
  ]

  return (
    <div className="p-8">
      <h1 className="mb-1 text-2xl font-semibold">Fixed-interval vs predictive maintenance</h1>
      <p className="mb-6 text-sm text-textMuted">
        Evaluated on {data.total_test_engines} held-out test engines (NASA C-MAPSS official test split).
      </p>

      <div className="rounded border border-border bg-surface p-4">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData}>
            <CartesianGrid stroke="#2A3650" strokeDasharray="3 3" />
            <XAxis dataKey="metric" stroke="#8C97AC" tick={{ fontSize: 12 }} />
            <YAxis stroke="#8C97AC" tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={{ background: '#141D2E', border: '1px solid #2A3650', color: '#E8ECF1' }} />
            <Legend />
            <Bar dataKey="Fixed-interval" fill="#C44536" radius={[3, 3, 0, 0]} />
            <Bar dataKey="Predictive (AirReady)" fill="#3FA34D" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
