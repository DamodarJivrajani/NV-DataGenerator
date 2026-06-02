import { clsx } from 'clsx'
import type { BiasReport } from '@/types'

interface Props {
  report: BiasReport
}

const GRADE_COLORS: Record<string, string> = {
  A: 'bg-green-900/30 border-green-600 text-green-400',
  B: 'bg-blue-900/30 border-blue-600 text-blue-400',
  C: 'bg-yellow-900/30 border-yellow-600 text-yellow-400',
  D: 'bg-orange-900/30 border-orange-600 text-orange-400',
  F: 'bg-red-900/30 border-red-600 text-red-400',
}

export function BiasReportPanel({ report }: Props) {
  const gradeClass = GRADE_COLORS[report.overallFairnessGrade] ?? GRADE_COLORS['C']

  const sentimentEntries = Object.entries(report.sentimentDistribution)
  const maxSentimentCount = Math.max(...sentimentEntries.map(([, v]) => v), 1)

  return (
    <div className="space-y-4">
      {/* Grade banner */}
      <div className={clsx('border rounded-lg p-4 flex items-center justify-between', gradeClass)}>
        <div>
          <div className="text-lg font-bold">Overall Fairness Grade</div>
          <div className="text-sm opacity-75">{report.totalAnalyzed} transcripts analyzed</div>
        </div>
        <div className="text-5xl font-black">{report.overallFairnessGrade}</div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-4">
        <MetricCard
          label="Gender Bias Score"
          value={report.genderBiasScore.toFixed(2)}
          description="0 = balanced, 1 = fully skewed"
          color={report.genderBiasScore < 0.3 ? 'text-green-400' : report.genderBiasScore < 0.6 ? 'text-yellow-400' : 'text-red-400'}
        />
        <MetricCard
          label="Demographic Diversity"
          value={`${(report.demographicDiversityScore * 100).toFixed(0)}%`}
          description="Name origin diversity"
          color={report.demographicDiversityScore > 0.6 ? 'text-green-400' : report.demographicDiversityScore > 0.3 ? 'text-yellow-400' : 'text-red-400'}
        />
      </div>

      {/* Sentiment distribution */}
      <div className="bg-gray-800/50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Sentiment Distribution</h4>
        <div className="space-y-2">
          {sentimentEntries.map(([sentiment, count]) => (
            <div key={sentiment} className="flex items-center gap-3">
              <span className="text-sm text-gray-400 w-24 capitalize">{sentiment}</span>
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div
                  className="bg-nvidia-green h-2 rounded-full transition-all"
                  style={{ width: `${(count / maxSentimentCount) * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-400 w-8 text-right">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Safety flags */}
      {report.safetyFlags.length > 0 ? (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-red-400 mb-2">⚠ Safety Flags Detected</h4>
          <ul className="space-y-1">
            {report.safetyFlags.map((flag, i) => (
              <li key={i} className="text-sm text-red-300">• {flag}</li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 text-sm text-green-400">
          ✓ No safety flags detected
        </div>
      )}
    </div>
  )
}

function MetricCard({ label, value, description, color }: { label: string; value: string; description: string; color: string }) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-4">
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-sm text-white mt-1">{label}</div>
      <div className="text-xs text-gray-500 mt-0.5">{description}</div>
    </div>
  )
}
