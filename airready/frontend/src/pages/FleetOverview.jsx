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

  if (error) {
    return (
      <div className="mx-auto max-w-screen-2xl p-4 sm:p-6 lg:p-8">
        <h1 className="mb-5 text-2xl font-semibold">Fleet overview</h1>
        <section role="alert" className="border-l-2 border-urgent bg-surface p-5">
          <p className="font-medium text-text">Fleet data unavailable</p>
          <p className="mt-1 text-sm text-textMuted">{error}</p>
        </section>
      </div>
    )
  }
  if (!fleet) {
    return (
      <div role="status" className="mx-auto max-w-screen-2xl animate-pulse p-4 sm:p-6 lg:p-8">
        <div className="mb-7 h-5 w-40 bg-surfaceAlt" />
        <div className="mb-3 h-20 w-56 bg-surfaceAlt" />
        <div className="h-4 w-72 max-w-full bg-surfaceAlt" />
        <p className="sr-only">Loading fleet status</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-screen-2xl p-4 sm:p-6 lg:p-8">
      <header className="mb-7 flex flex-col justify-between gap-6 border-b border-border pb-7 sm:flex-row sm:items-end">
        <div>
          <p className="mb-2 font-numeral text-xs uppercase text-accent">Fleet readiness / FD001</p>
          <h1 className="text-2xl font-semibold">Fleet overview</h1>
          <p className="mt-2 max-w-2xl text-sm text-textMuted">
            NASA C-MAPSS public benchmark data. Decision support for maintenance engineers;
            designed to connect to real sensor feeds.
          </p>
        </div>
        <div className="sm:min-w-64 sm:text-right">
          <p className="text-xs uppercase text-textMuted">Fleet availability</p>
          <div className="mt-1 font-numeral text-6xl font-semibold leading-none text-text sm:text-7xl">
            {fleet.fleet_availability_pct}<span className="ml-1 text-3xl text-healthy">%</span>
          </div>
          <p className="mt-2 text-sm text-textMuted">
            {fleet.healthy_count} of {fleet.total_engines} engines currently healthy
          </p>
        </div>
      </header>

      <div className="mb-8 grid grid-cols-3 divide-x divide-border border-y border-border py-4">
        <div className="px-3 first:pl-0 sm:px-5">
          <div className="text-xs uppercase text-textMuted">Healthy</div>
          <div className="mt-1 font-numeral text-2xl text-healthy">{fleet.healthy_count}</div>
        </div>
        <div className="px-3 sm:px-5">
          <div className="text-xs uppercase text-textMuted">Watch</div>
          <div className="mt-1 font-numeral text-2xl text-watch">{fleet.watch_count}</div>
        </div>
        <div className="px-3 sm:px-5">
          <div className="text-xs uppercase text-textMuted">Urgent</div>
          <div className="mt-1 font-numeral text-2xl text-urgent">{fleet.urgent_count}</div>
        </div>
      </div>

      <section className="mb-9">
        <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-lg font-medium">Priority review</h2>
          <p className="text-xs text-textMuted">Linked spares inventory is illustrative</p>
        </div>
        <AlertsPanel alerts={alerts} />
      </section>

      <h2 className="mb-3 text-lg font-medium">All engines <span className="ml-2 font-numeral text-xs text-textMuted">{fleet.total_engines}</span></h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {fleet.engines.map((engine) => (
          <FleetCard key={engine.engine_id} engine={engine} />
        ))}
      </div>
    </div>
  )
}
