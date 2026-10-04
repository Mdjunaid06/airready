import StatusBadge from './StatusBadge'

export default function AlertsPanel({ alerts }) {
  if (!alerts?.length) {
    return <div className="border border-border bg-surface px-4 py-5 text-sm text-textMuted">No engines currently require priority review.</div>
  }
  return (
    <div className="divide-y divide-border border-y border-border">
      {alerts.map((alert) => (
        <div
          key={alert.engine_id}
          className="flex flex-wrap items-center justify-between gap-3 bg-surface px-3 py-3 transition-colors hover:bg-surfaceAlt sm:px-4"
        >
          <div className="flex items-center gap-3">
            <span className="font-numeral text-sm">{alert.engine_id}</span>
            <StatusBadge status={alert.status} />
          </div>
          <div className="text-right text-xs text-textMuted">
            <span className="font-numeral text-text">{alert.predicted_rul_cycles}</span> cycles estimated
            {alert.linked_spares?.length > 0 && (
              <div>
                illustrative spare: {alert.linked_spares[0].part_id} ({alert.linked_spares[0].stock_quantity} in stock)
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
