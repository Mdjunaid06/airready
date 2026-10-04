import { Routes, Route, NavLink } from 'react-router-dom'
import FleetOverview from './pages/FleetOverview'
import EngineDetail from './pages/EngineDetail'
import Comparison from './pages/Comparison'

const navLinkClass = ({ isActive }) =>
  `block rounded border border-transparent px-3 py-2 text-sm transition-colors ${isActive ? 'border-border bg-surfaceAlt text-text' : 'text-textMuted hover:border-border hover:text-text'}`

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-base md:flex-row">
      <nav className="border-b border-border p-3 md:w-56 md:shrink-0 md:border-b-0 md:border-r md:p-4">
        <div className="mb-3 flex items-center justify-between gap-3 px-1 md:mb-6 md:block md:px-2">
          <div className="font-numeral text-lg font-semibold">AirReady</div>
          <div className="text-right text-xs text-textMuted md:mt-1 md:text-left">SIH 26249 · Fleet Readiness</div>
        </div>
        <div className="flex gap-2 md:flex-col">
          <NavLink to="/" end className={navLinkClass}>Fleet Overview</NavLink>
          <NavLink to="/comparison" className={navLinkClass}>Comparison</NavLink>
        </div>
      </nav>
      <main className="min-w-0 flex-1">
        <Routes>
          <Route path="/" element={<FleetOverview />} />
          <Route path="/engine/:engineId" element={<EngineDetail />} />
          <Route path="/comparison" element={<Comparison />} />
        </Routes>
      </main>
    </div>
  )
}
