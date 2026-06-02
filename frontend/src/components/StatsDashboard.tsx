import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import type { DatasetStats } from '@/types'

const COLORS = ['#76b900', '#a3d948', '#4a7a00', '#c8e88a', '#2d5500', '#e8f5b0', '#1a3300']

interface Props {
  stats: DatasetStats
}

export function StatsDashboard({ stats }: Props) {
  const sentimentData = Object.entries(stats.sentimentDistribution).map(([name, value]) => ({ name, value }))
  const languageData = Object.entries(stats.languageDistribution).map(([name, value]) => ({ name, value }))
  const resolutionData = Object.entries(stats.resolutionStatusDistribution).map(([name, value]) => ({ name, value }))
  const industryData = Object.entries(stats.industryBreakdown).map(([name, value]) => ({ name, value }))
  const qualityData = Object.entries(stats.qualityScoreDistribution).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      {/* Summary row */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="Total Transcripts" value={stats.totalTranscripts} />
        <MetricCard label="Avg Duration" value={`${Math.round(stats.avgDurationSeconds)}s`} />
        <MetricCard label="Languages" value={Object.keys(stats.languageDistribution).length} />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Sentiment Distribution">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={sentimentData} cx="50%" cy="50%" outerRadius={70} dataKey="value" label={({ name }) => name}>
                {sentimentData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Resolution Status">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={resolutionData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="value" fill="#76b900" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Language Distribution">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={languageData} layout="vertical" margin={{ top: 5, right: 10, left: 60, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="value" fill="#76b900" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Conversation Turn Length">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stats.turnLengthHistogram} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="range" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="count" fill="#a3d948" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts row 3 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Industry Breakdown">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={industryData} cx="50%" cy="50%" outerRadius={70} dataKey="value">
                {industryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11, color: '#9ca3af' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Quality Score Distribution">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={qualityData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="value" fill="#76b900" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 text-center">
      <div className="text-2xl font-bold text-nvidia-green">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{label}</div>
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-4">
      <h4 className="text-sm font-semibold text-gray-300 mb-3">{title}</h4>
      {children}
    </div>
  )
}
