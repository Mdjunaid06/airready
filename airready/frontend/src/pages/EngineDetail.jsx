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
    getEngineDetail(engineId)
      .then(setEngine)
      .catch(() => setError('Could not load this engine. It may not exist.'))
  }, [engineId])

  if (error) return <div className="p-8 text-urgent">{error}</div>
  if (!engine) return <div className="p-8 text-textMuted">Loading engine detail…</div>

  return (
    <div className="p-8">
      <Link to="/" className="mb-6 inline-block text-sm text-accent hover:underline">
        ← Back to fleet
      </Link>

      <div className="mb-6 flex items-center gap-4">
        <h1 className="font-numeral text-3xl font-semibold">{engine.engine_id}</h1>
        <StatusBadge status={engine.status} />
      </div>

      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Predicted RUL</div>
          <div className="font-numeral text-2xl">{engine.predicted_rul_cycles} cycles</div>
        </div>
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Confidence range</div>
          <div className="font-numeral text-2xl">{engine.confidence_low}–{engine.confidence_high}</div>
        </div>
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Linked spares</div>
          <div className="font-numeral text-sm">
            {engine.linked_spares?.length ? engine.linked_spares.join(', ') : '—'}
          </div>
        </div>
      </div>

      <h2 className="mb-3 text-lg font-medium">Sensor trend</h2>
      <div className="rounded border border-border bg-surface p-4">
        <RulTrendChart sensorHistory={engine.sensor_history} />
      </div>
    </div>
  )
}
