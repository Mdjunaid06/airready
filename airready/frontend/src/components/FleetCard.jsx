import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge'

export default function FleetCard({ engine }) {
  return (
    <Link
      to={`/engine/${engine.engine_id}`}
      className="block rounded border border-border bg-surface p-4 transition-colors hover:border-accent"
    >
      <div className="flex items-start justify-between">
        <span className="text-sm text-textMuted">{engine.engine_id}</span>
        <StatusBadge status={engine.status} />
      </div>
      <div className="mt-3 font-numeral text-2xl font-semibold">
        {engine.predicted_rul_cycles}
        <span className="ml-1 text-sm font-normal text-textMuted">cycles left</span>
      </div>
      <div className="mt-1 font-numeral text-xs text-textMuted">
        range {engine.confidence_low}–{engine.confidence_high}
      </div>
    </Link>
  )
}
