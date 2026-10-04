import { Routes, Route, NavLink } from 'react-router-dom'
import FleetOverview from './pages/FleetOverview'
import EngineDetail from './pages/EngineDetail'
import Comparison from './pages/Comparison'

const navLinkClass = ({ isActive }) =>
  `block rounded px-3 py-2 text-sm ${isActive ? 'bg-surfaceAlt text-text' : 'text-textMuted hover:text-text'}`

export default function App() {
  return (
    <div className="flex min-h-screen bg-base">
      <nav className="w-56 shrink-0 border-r border-border p-4">
        <div className="mb-6 px-2">
          <div className="font-numeral text-lg font-semibold">AirReady</div>
          <div className="text-xs text-textMuted">SIH 26249 · Fleet Readiness</div>
        </div>
        <NavLink to="/" end className={navLinkClass}>Fleet Overview</NavLink>
        <NavLink to="/comparison" className={navLinkClass}>Comparison</NavLink>
      </nav>
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<FleetOverview />} />
          <Route path="/engine/:engineId" element={<EngineDetail />} />
          <Route path="/comparison" element={<Comparison />} />
        </Routes>
      </main>
    </div>
  )
}
