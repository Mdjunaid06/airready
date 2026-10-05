/**
 * Design tokens for AirReady — see docs/FRONTEND.md Section 4.
 * Deliberate choice: a dark instrument-panel palette with a monospace numeral
 * face, because this is genuinely an operations/readiness dashboard, not a
 * marketing page — the vernacular should read like mission-control telemetry,
 * not a generic SaaS product.
 */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: '#0B1220',       // deep navy background
        surface: '#141D2E',    // panel background
        surfaceAlt: '#1B2740', // slightly raised panel
        border: '#2A3650',
        text: '#E8ECF1',
        textMuted: '#8C97AC',
        healthy: '#3FA34D',
        watch: '#D9A441',
        urgent: '#C44536',
        accent: '#5B8DEF',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
