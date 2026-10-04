/**
 * Single source of truth for Healthy/Watch/Urgent colour + label.
 * Every other component must reuse this, never re-implement the mapping —
 * see docs/FRONTEND.md Section 3.
 */
const STATUS_CONFIG = {
  healthy: { label: 'Healthy', color: 'text-healthy', dot: 'bg-healthy' },
  watch: { label: 'Watch', color: 'text-watch', dot: 'bg-watch' },
  urgent: { label: 'Urgent', color: 'text-urgent', dot: 'bg-urgent' },
}

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.healthy
  return (
    <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${config.color}`}>
      <span className={`h-2 w-2 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  )
}
