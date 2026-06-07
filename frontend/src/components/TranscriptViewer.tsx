import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft, Play, Pause, Square, Loader2, Search, User, Headphones,
  ChevronDown, ChevronUp, AlertCircle, Volume2, VolumeX,
} from 'lucide-react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useSpeech } from '@/hooks/useSpeech'
import { TranscriptConversation } from './TranscriptConversation'
import type { Transcript } from '@/types'

export function TranscriptViewer() {
  const { jobId } = useParams<{ jobId: string }>()
  const [search, setSearch] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState<string>('all')

  const speech = useSpeech()
  const [playingId, setPlayingId] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['job-results', jobId],
    queryFn: () => api.getJobResults(jobId!),
    enabled: !!jobId,
    retry: false,
  })

  const transcripts = data?.transcripts ?? []
  const kpis = useMemo(() => computeKpis(transcripts), [transcripts])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return transcripts.filter((t) => {
      if (sentimentFilter !== 'all' && t.customer?.sentiment !== sentimentFilter) return false
      if (!q) return true
      return (
        t.scenario?.toLowerCase().includes(q) ||
        t.customer?.name?.toLowerCase().includes(q) ||
        t.agent?.name?.toLowerCase().includes(q) ||
        t.conversation?.some((turn) => turn.text.toLowerCase().includes(q))
      )
    })
  }, [transcripts, search, sentimentFilter])

  const playCall = (t: Transcript) => {
    setPlayingId(t.id)
    speech.play(t.conversation)
  }
  const stopCall = () => {
    speech.stop()
    setPlayingId(null)
  }

  // Clear the highlighted call when playback ends on its own (not just via Stop),
  // so playingId doesn't drift out of sync with the actual speech state.
  useEffect(() => {
    if (!speech.isPlaying) setPlayingId(null)
  }, [speech.isPlaying])

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Top bar */}
      <header className="border-b border-gray-800 bg-gray-900/50 sticky top-0 z-10 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link to="/" className="btn-secondary flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back
          </Link>
          <div>
            <h1 className="text-xl font-bold text-white">Transcript Viewer</h1>
            <p className="text-xs text-gray-500 font-mono">Job {jobId?.slice(0, 8)}</p>
          </div>
          {!speech.isSupported && (
            <span className="ml-auto flex items-center gap-1 text-xs text-yellow-400">
              <VolumeX className="w-4 h-4" /> Voice not supported in this browser
            </span>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {isLoading && (
          <div className="flex items-center justify-center py-20 text-gray-400">
            <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading transcripts…
          </div>
        )}

        {isError && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6 text-center text-red-400">
            <AlertCircle className="w-8 h-8 mx-auto mb-2" />
            <p>{(error as Error)?.message || 'Could not load transcripts.'}</p>
            <Link to="/" className="text-nvidia-green underline mt-3 inline-block">Return to generator</Link>
          </div>
        )}

        {!isLoading && !isError && transcripts.length > 0 && (
          <>
            {/* KPI bar */}
            <section>
              <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">Key Metrics</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Kpi label="Total Transcripts" value={kpis.total} />
                <Kpi label="Avg Duration" value={formatDuration(kpis.avgDuration)} />
                <Kpi label="Avg CSAT" value={kpis.avgCsat != null ? `${kpis.avgCsat.toFixed(1)}/5` : '—'} />
                <Kpi label="Resolution Rate" value={`${Math.round(kpis.resolutionRate * 100)}%`} />
                <Kpi label="Escalation Rate" value={`${Math.round(kpis.escalationRate * 100)}%`} />
                <Kpi label="Avg Turns" value={kpis.avgTurns.toFixed(1)} />
                <Kpi
                  label="Avg Quality"
                  value={kpis.avgQuality != null ? `${kpis.avgQuality.toFixed(1)}/10` : 'Not scored'}
                />
                <SentimentKpi sentiments={kpis.sentiments} total={kpis.total} />
              </div>
            </section>

            {/* Filters */}
            <section className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 flex items-center gap-2 bg-gray-800/50 rounded-lg px-3">
                <Search className="w-4 h-4 text-gray-500" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search scenario, name, or conversation text…"
                  className="flex-1 bg-transparent py-2.5 text-sm text-white focus:outline-none"
                />
              </div>
              <select
                value={sentimentFilter}
                onChange={(e) => setSentimentFilter(e.target.value)}
                className="select"
              >
                <option value="all">All sentiments</option>
                {Object.keys(kpis.sentiments).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </section>

            <p className="text-sm text-gray-500">
              Showing {filtered.length} of {transcripts.length} transcripts
            </p>

            {/* Transcript list */}
            <div className="space-y-4">
              {filtered.map((t, i) => (
                <TranscriptCard
                  key={t.id}
                  transcript={t}
                  defaultExpanded={i === 0}
                  isPlaying={playingId === t.id && speech.isPlaying}
                  isPaused={playingId === t.id && speech.isPaused}
                  activeIndex={playingId === t.id ? speech.currentIndex : null}
                  voiceSupported={speech.isSupported}
                  onPlay={() => playCall(t)}
                  onPause={speech.pause}
                  onResume={speech.resume}
                  onStop={stopCall}
                  onPlayTurn={(turn, idx) => { setPlayingId(t.id); speech.playTurn(turn, idx) }}
                />
              ))}
            </div>

            {/* Playback speed */}
            {speech.isSupported && (
              <div className="flex items-center gap-3 text-sm text-gray-400 border-t border-gray-800 pt-4">
                <Volume2 className="w-4 h-4" />
                <span>Playback speed</span>
                <input
                  type="range" min={0.5} max={1.5} step={0.1}
                  value={speech.rate}
                  onChange={(e) => speech.setRate(parseFloat(e.target.value))}
                  className="accent-nvidia-green w-40"
                />
                <span className="font-mono text-nvidia-green">{speech.rate.toFixed(1)}x</span>
              </div>
            )}
          </>
        )}

        {!isLoading && !isError && transcripts.length === 0 && (
          <div className="text-center py-20 text-gray-500">No transcripts found for this job.</div>
        )}
      </main>
    </div>
  )
}

// ─── Transcript card ───────────────────────────────────────────────────────

interface CardProps {
  transcript: Transcript
  defaultExpanded: boolean
  isPlaying: boolean
  isPaused: boolean
  activeIndex: number | null
  voiceSupported: boolean
  onPlay: () => void
  onPause: () => void
  onResume: () => void
  onStop: () => void
  onPlayTurn: (turn: Transcript['conversation'][number], index: number) => void
}

function TranscriptCard({
  transcript: t, defaultExpanded, isPlaying, isPaused, activeIndex,
  voiceSupported, onPlay, onPause, onResume, onStop, onPlayTurn,
}: CardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-xs font-mono text-gray-500">{t.id.slice(0, 8)}</span>
          <span className="text-white font-medium">{t.scenario}</span>
          <SentimentBadge sentiment={t.customer?.sentiment} />
          {t.language && t.language !== 'english' && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 capitalize">
              {t.language}
            </span>
          )}
          {t.qualityScores && (
            <span className={clsx(
              'text-xs px-2 py-0.5 rounded-full font-mono font-semibold',
              t.qualityScores.overall >= 8 ? 'bg-green-500/20 text-green-400' :
              t.qualityScores.overall >= 6 ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400',
            )}>
              Q:{t.qualityScores.overall.toFixed(1)}
            </span>
          )}
        </div>

        {/* Voice controls */}
        <div className="flex items-center gap-2">
          {voiceSupported && (
            !isPlaying ? (
              <button onClick={onPlay} className="btn-primary flex items-center gap-1.5 py-1.5 text-sm">
                <Play className="w-4 h-4" /> Play call
              </button>
            ) : (
              <>
                {isPaused ? (
                  <button onClick={onResume} className="btn-primary flex items-center gap-1.5 py-1.5 text-sm">
                    <Play className="w-4 h-4" /> Resume
                  </button>
                ) : (
                  <button onClick={onPause} className="btn-secondary flex items-center gap-1.5 py-1.5 text-sm">
                    <Pause className="w-4 h-4" /> Pause
                  </button>
                )}
                <button onClick={onStop} className="btn-secondary flex items-center gap-1.5 py-1.5 text-sm">
                  <Square className="w-4 h-4" /> Stop
                </button>
              </>
            )
          )}
          <button
            onClick={() => setExpanded((v) => !v)}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-gray-700/50 pt-4">
          {/* Participants */}
          <div className="flex gap-6 text-sm flex-wrap">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-blue-400" />
              <span className="text-gray-400">Customer:</span>
              <span className="text-white">{t.customer?.name}</span>
              {t.customer?.age != null && <span className="text-gray-500">({t.customer.age})</span>}
            </div>
            <div className="flex items-center gap-2">
              <Headphones className="w-4 h-4 text-nvidia-green" />
              <span className="text-gray-400">Agent:</span>
              <span className="text-white">{t.agent?.name}</span>
              {t.agent?.experienceLevel && <span className="text-gray-500">({t.agent.experienceLevel})</span>}
            </div>
          </div>

          {/* Conversation (text) */}
          <div className="max-h-96 overflow-y-auto pr-1">
            <TranscriptConversation
              conversation={t.conversation}
              activeIndex={activeIndex}
              onPlayTurn={voiceSupported ? onPlayTurn : undefined}
            />
          </div>

          {/* Metadata */}
          {t.metadata && (
            <div className="flex gap-4 text-xs text-gray-400 pt-2 border-t border-gray-700 flex-wrap">
              <span>Duration: {formatDuration(t.metadata.durationSeconds)}</span>
              <span>Status: {t.metadata.resolutionStatus}</span>
              {t.metadata.csatScore != null && <span>CSAT: {t.metadata.csatScore}/5</span>}
              {t.metadata.escalated && <span className="text-orange-400">Escalated</span>}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── KPI helpers ─────────────────────────────────────────────────────────────

interface Kpis {
  total: number
  avgDuration: number
  avgCsat: number | null
  resolutionRate: number
  escalationRate: number
  avgTurns: number
  sentiments: Record<string, number>
  avgQuality: number | null
}

function computeKpis(transcripts: Transcript[]): Kpis {
  const total = transcripts.length
  const mean = (nums: number[]) => (nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : 0)

  const csats = transcripts.map((t) => t.metadata?.csatScore).filter((c): c is number => c != null)
  const quals = transcripts.map((t) => t.qualityScores?.overall).filter((q): q is number => q != null)
  const sentiments: Record<string, number> = {}
  for (const t of transcripts) {
    const s = t.customer?.sentiment ?? 'unknown'
    sentiments[s] = (sentiments[s] || 0) + 1
  }

  return {
    total,
    avgDuration: mean(transcripts.map((t) => t.metadata?.durationSeconds ?? 0)),
    avgCsat: csats.length ? mean(csats) : null,
    resolutionRate: total ? transcripts.filter((t) => t.metadata?.resolutionStatus === 'resolved').length / total : 0,
    escalationRate: total ? transcripts.filter((t) => t.metadata?.escalated).length / total : 0,
    avgTurns: mean(transcripts.map((t) => t.conversation?.length ?? 0)),
    sentiments,
    avgQuality: quals.length ? mean(quals) : null,
  }
}

function formatDuration(seconds: number): string {
  const s = Math.round(seconds)
  return `${Math.floor(s / 60)}m ${s % 60}s`
}

function Kpi({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 text-center">
      <div className="text-2xl font-bold text-nvidia-green">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{label}</div>
    </div>
  )
}

function SentimentKpi({ sentiments, total }: { sentiments: Record<string, number>; total: number }) {
  const top = Object.entries(sentiments).sort((a, b) => b[1] - a[1])[0]
  return (
    <div className="bg-gray-800 rounded-lg p-4 text-center">
      <div className="text-2xl font-bold text-nvidia-green capitalize">{top ? top[0] : '—'}</div>
      <div className="text-xs text-gray-400 mt-1">
        Top Sentiment{top && total ? ` (${Math.round((top[1] / total) * 100)}%)` : ''}
      </div>
    </div>
  )
}

function SentimentBadge({ sentiment }: { sentiment?: string }) {
  if (!sentiment) return null
  return (
    <span className={clsx(
      'text-xs px-2 py-0.5 rounded-full',
      sentiment === 'satisfied' && 'bg-green-500/20 text-green-400',
      sentiment === 'neutral' && 'bg-gray-500/20 text-gray-400',
      sentiment === 'frustrated' && 'bg-orange-500/20 text-orange-400',
      sentiment === 'angry' && 'bg-red-500/20 text-red-400',
      sentiment === 'confused' && 'bg-yellow-500/20 text-yellow-400',
    )}>
      {sentiment}
    </span>
  )
}
