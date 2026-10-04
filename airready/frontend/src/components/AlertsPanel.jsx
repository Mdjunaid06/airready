import StatusBadge from './StatusBadge'

export default function AlertsPanel({ alerts }) {
  if (!alerts?.length) {
    return <div className="text-sm text-textMuted">No active alerts — fleet is healthy.</div>
  }
  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.engine_id}
          className="flex items-center justify-between rounded border border-border bg-surface p-3"
        >
          <div className="flex items-center gap-3">
            <span className="font-numeral text-sm">{alert.engine_id}</span>
            <StatusBadge status={alert.status} />
          </div>
          <div className="text-right text-xs text-textMuted">
            {alert.predicted_rul_cycles} cycles left
            {alert.linked_spares?.length > 0 && (
              <div>
                spare: {alert.linked_spares[0].part_id} ({alert.linked_spares[0].stock_quantity} in stock)
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
