import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getComparison } from '../lib/api'

export default function Comparison() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getComparison().then(setData).catch(() => setError('Could not load comparison data.'))
  }, [])

  if (error) {
    return (
      <div className="mx-auto max-w-screen-xl p-4 sm:p-6 lg:p-8">
        <h1 className="mb-5 text-2xl font-semibold">Maintenance comparison</h1>
        <section role="alert" className="border-l-2 border-urgent bg-surface p-5">
          <p className="font-medium text-text">Comparison data unavailable</p>
          <p className="mt-1 text-sm text-textMuted">{error}</p>
        </section>
      </div>
    )
  }
  if (!data) {
    return (
      <div role="status" className="mx-auto max-w-screen-xl animate-pulse p-4 sm:p-6 lg:p-8">
        <div className="mb-3 h-7 w-72 max-w-full bg-surfaceAlt" />
        <div className="mb-7 h-4 w-96 max-w-full bg-surfaceAlt" />
        <div className="h-80 w-full bg-surface" />
        <p className="sr-only">Loading comparison</p>
      </div>
    )
  }

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
    <div className="mx-auto max-w-screen-xl p-4 sm:p-6 lg:p-8">
      <header className="mb-7 border-b border-border pb-6">
        <p className="mb-2 font-numeral text-xs uppercase text-accent">Benchmark evaluation / FD001</p>
        <h1 className="mb-2 text-2xl font-semibold">Fixed-interval vs predictive maintenance</h1>
        <p className="max-w-3xl text-sm text-textMuted">
          Computed on {data.total_test_engines} held-out engines from the NASA C-MAPSS public test split.
          These benchmark results are a proxy, not operational fleet performance.
        </p>
        <p className="mt-2 text-xs text-textMuted">
          Predictive flags are recommendations for maintenance engineers to review.
        </p>
      </header>

      <section aria-label="Maintenance policy comparison" className="rounded border border-border bg-surface p-3 sm:p-5">
        <ResponsiveContainer width="100%" height={360}>
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
      </section>
      <p className="mt-3 text-xs text-textMuted">
        Lower counts are better. "Missed failure" and "unnecessary service" use the definitions in the evaluation pipeline.
      </p>
    </div>
  )
}
