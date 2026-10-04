import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'

export default function RulTrendChart({ sensorHistory, dataKey = 'sensor_2' }) {
  if (!sensorHistory?.length) {
    return <div className="text-sm text-textMuted">No sensor history available.</div>
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={sensorHistory} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#2A3650" strokeDasharray="3 3" />
        <XAxis dataKey="cycle" stroke="#8C97AC" tick={{ fontSize: 12 }} />
        <YAxis stroke="#8C97AC" tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: '#141D2E', border: '1px solid #2A3650', color: '#E8ECF1' }}
        />
        <Line type="monotone" dataKey={dataKey} stroke="#5B8DEF" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
