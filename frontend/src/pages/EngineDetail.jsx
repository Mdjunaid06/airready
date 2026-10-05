import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEngineDetail } from '../lib/api'
import StatusBadge from '../components/StatusBadge'
import RulTrendChart from '../components/RulTrendChart'

export default function EngineDetail() {
  const { engineId } = useParams()
  const [engine, setEngine] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setEngine(null)
    setError(null)
    getEngineDetail(engineId)
      .then(setEngine)
      .catch(() => setError('Could not load this engine. It may not exist.'))
  }, [engineId])

  if (error) {
    return (
      <div className="mx-auto max-w-screen-xl p-4 sm:p-6 lg:p-8">
        <Link to="/" className="mb-6 inline-block text-sm text-accent transition-colors hover:text-text">← Back to fleet</Link>
        <section role="alert" className="border-l-2 border-urgent bg-surface p-5">
          <p className="font-medium text-text">Engine data unavailable</p>
          <p className="mt-1 text-sm text-textMuted">{error}</p>
        </section>
      </div>
    )
  }
  if (!engine) {
    return (
      <div role="status" className="mx-auto max-w-screen-xl animate-pulse p-4 sm:p-6 lg:p-8">
        <div className="mb-7 h-4 w-32 bg-surfaceAlt" />
        <div className="mb-4 h-8 w-48 bg-surfaceAlt" />
        <div className="h-64 w-full bg-surface" />
        <p className="sr-only">Loading engine detail</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-screen-xl p-4 sm:p-6 lg:p-8">
      <Link to="/" className="mb-6 inline-block text-sm text-accent transition-colors hover:text-text">
        ← Back to fleet
      </Link>

      <header className="mb-7 border-b border-border pb-6">
        <p className="mb-2 font-numeral text-xs uppercase text-accent">NASA C-MAPSS / FD001 public benchmark</p>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-numeral text-3xl font-semibold">{engine.engine_id}</h1>
          <StatusBadge status={engine.status} />
        </div>
        <p className="mt-2 text-sm text-textMuted">Decision support for human maintenance review; not an automatic maintenance action.</p>
      </header>

      <div className="mb-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded border border-border bg-surface p-4 transition-colors hover:border-accent">
          <div className="text-xs uppercase text-textMuted">Estimated remaining life</div>
          <div className="mt-2 font-numeral text-2xl">{engine.predicted_rul_cycles}<span className="ml-2 text-sm text-textMuted">cycles</span></div>
        </div>
        <div className="rounded border border-border bg-surface p-4 transition-colors hover:border-accent">
          <div className="text-xs uppercase text-textMuted">Typical error band</div>
          <div className="mt-2 font-numeral text-2xl">{engine.confidence_low}–{engine.confidence_high}<span className="ml-2 text-sm text-textMuted">cycles</span></div>
          <p className="mt-1 text-xs text-textMuted">Based on held-out MAE; not a calibrated probability interval.</p>
        </div>
        <div className="rounded border border-border bg-surface p-4 transition-colors hover:border-accent">
          <div className="flex items-center justify-between gap-2">
            <div className="text-xs uppercase text-textMuted">Linked spares</div>
            <span className="text-xs text-watch">Illustrative</span>
          </div>
          <div className="mt-2 font-numeral text-sm">
            {engine.linked_spares?.length ? engine.linked_spares.join(', ') : '—'}
          </div>
        </div>
      </div>

      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-medium">Sensor trend</h2>
        <p className="text-xs text-textMuted">Sensor 2 · {engine.sensor_history.length} observed cycles</p>
      </div>
      <div className="rounded border border-border bg-surface p-3 sm:p-5">
        <RulTrendChart sensorHistory={engine.sensor_history} />
      </div>
    </div>
  )
}
