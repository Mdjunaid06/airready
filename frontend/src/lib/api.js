/**
 * Single Axios instance + every API call function. No component should import
 * axios directly — see docs/FRONTEND.md Section 3.
 * Shapes here must match docs/API_CONTRACTS.md exactly.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

export const getFleet = () => client.get('/fleet').then((r) => r.data)
export const getEngineDetail = (engineId) => client.get(`/engine/${engineId}`).then((r) => r.data)
export const getAlerts = () => client.get('/alerts').then((r) => r.data)
export const getSpares = () => client.get('/spares').then((r) => r.data)
export const getComparison = () => client.get('/comparison').then((r) => r.data)
