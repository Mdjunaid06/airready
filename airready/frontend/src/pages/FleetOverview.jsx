import { useEffect, useState } from 'react'
import { getAlerts, getFleet } from '../lib/api'
import FleetCard from '../components/FleetCard'
import AlertsPanel from '../components/AlertsPanel'

export default function FleetOverview() {
  const [fleet, setFleet] = useState(null)
  const [alerts, setAlerts] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getFleet(), getAlerts()])
      .then(([fleetData, alertsData]) => {
        setFleet(fleetData)
        setAlerts(alertsData.alerts)
      })
      .catch(() => setError('Could not reach the AirReady API. Is the backend running?'))
  }, [])

  if (error) return <div className="p-8 text-urgent">{error}</div>
  if (!fleet) return <div className="p-8 text-textMuted">Loading fleet status…</div>

  return (
    <div className="p-8">
      <div className="mb-8 flex items-end gap-4">
        <div className="font-numeral text-6xl font-semibold">{fleet.fleet_availability_pct}%</div>
        <div className="pb-2 text-textMuted">fleet availability · {fleet.total_engines} engines tracked</div>
      </div>

      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Healthy</div>
          <div className="font-numeral text-2xl text-healthy">{fleet.healthy_count}</div>
        </div>
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Watch</div>
          <div className="font-numeral text-2xl text-watch">{fleet.watch_count}</div>
        </div>
        <div className="rounded border border-border bg-surface p-4">
          <div className="text-sm text-textMuted">Urgent</div>
          <div className="font-numeral text-2xl text-urgent">{fleet.urgent_count}</div>
        </div>
      </div>

      <h2 className="mb-3 text-lg font-medium">Active alerts</h2>
      <div className="mb-8">
        <AlertsPanel alerts={alerts} />
      </div>

      <h2 className="mb-3 text-lg font-medium">All engines</h2>
      <div className="grid grid-cols-4 gap-4">
        {fleet.engines.map((engine) => (
          <FleetCard key={engine.engine_id} engine={engine} />
        ))}
      </div>
    </div>
  )
}
