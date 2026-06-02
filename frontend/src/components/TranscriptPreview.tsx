import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Play, Loader2, User, Headphones, ChevronDown, ChevronUp } from 'lucide-react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import type { Transcript } from '@/types'

export function TranscriptPreview() {
  const { config } = useConfigStore()
  const [transcripts, setTranscripts] = useState<Transcript[]>([])
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [minQuality, setMinQuality] = useState(0)

  const previewMutation = useMutation({
    mutationFn: () => api.generatePreview(config),
    onSuccess: (data) => {
      setTranscripts(data.transcripts)
      if (data.transcripts.length > 0) {
        setExpandedId(data.transcripts[0].id)
      }
    },
  })

  const filtered = transcripts.filter((t) => {
    if (minQuality === 0) return true
    return (t.qualityScores?.overall ?? 10) >= minQuality
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Preview Transcripts</h2>
          <p className="text-gray-400">
            Generate a preview batch to review before full generation
          </p>
        </div>
        <button
          onClick={() => previewMutation.mutate()}
          disabled={previewMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {previewMutation.isPending ? (
            <><Loader2 className="w-4 h-4 animate-spin" />Generating...</>
          ) : (
            <><Play className="w-4 h-4" />Generate Preview</>
          )}
        </button>
      </div>

      {previewMutation.isError && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400">
          Error: {previewMutation.error?.message || 'Failed to generate preview'}
        </div>
      )}

      {transcripts.length > 0 && (
        <div className="space-y-4">
          {/* Quality filter */}
          <div className="flex items-center gap-4 bg-gray-800/50 rounded-lg px-4 py-3">
            <span className="text-sm text-gray-400 whitespace-nowrap">Min Quality Score:</span>
            <input
              type="range"
              min={0} max={10} step={0.5}
              value={minQuality}
              onChange={(e) => setMinQuality(parseFloat(e.target.value))}
              className="flex-1 accent-nvidia-green"
            />
            <span className="text-nvidia-green font-mono text-sm w-8">{minQuality}</span>
            <span className="text-sm text-gray-500">
              {filtered.length}/{transcripts.length} shown
            </span>
          </div>

          <p className="text-sm text-nvidia-green">
            Generated {transcripts.length} preview transcript{transcripts.length > 1 ? 's' : ''}
          </p>

          {filtered.map((transcript) => (
            <TranscriptCard
              key={transcript.id}
              transcript={transcript}
              isExpanded={expandedId === transcript.id}
              onToggle={() => setExpandedId(expandedId === transcript.id ? null : transcript.id)}
            />
          ))}
        </div>
      )}

      {transcripts.length === 0 && !previewMutation.isPending && (
        <div className="text-center py-12 text-gray-500">
          <Play className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Click "Generate Preview" to see sample transcripts</p>
        </div>
      )}
    </div>
  )
}


interface TranscriptCardProps {
  transcript: Transcript
  isExpanded: boolean
  onToggle: () => void
}

function TranscriptCard({ transcript, isExpanded, onToggle }: TranscriptCardProps) {
  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-800/80 transition-colors"
      >
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-gray-500">{transcript.id.slice(0, 8)}</span>
          <span className="text-white font-medium">{transcript.scenario}</span>
          <span className={clsx(
            'text-xs px-2 py-0.5 rounded-full',
            transcript.customer.sentiment === 'satisfied' && 'bg-green-500/20 text-green-400',
            transcript.customer.sentiment === 'neutral' && 'bg-gray-500/20 text-gray-400',
            transcript.customer.sentiment === 'frustrated' && 'bg-orange-500/20 text-orange-400',
            transcript.customer.sentiment === 'angry' && 'bg-red-500/20 text-red-400',
            transcript.customer.sentiment === 'confused' && 'bg-yellow-500/20 text-yellow-400',
          )}>
            {transcript.customer.sentiment}
          </span>
          {transcript.language && transcript.language !== 'english' && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 capitalize">
              {transcript.language}
            </span>
          )}
          {transcript.qualityScores && (
            <span className={clsx(
              'text-xs px-2 py-0.5 rounded-full font-mono font-semibold',
              transcript.qualityScores.overall >= 8 ? 'bg-green-500/20 text-green-400' :
              transcript.qualityScores.overall >= 6 ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            )}>
              Q:{transcript.qualityScores.overall.toFixed(1)}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Participants */}
          <div className="flex gap-6 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-blue-400" />
              <span className="text-gray-400">Customer:</span>
              <span className="text-white">{transcript.customer.name}</span>
              <span className="text-gray-500">({transcript.customer.age})</span>
            </div>
            <div className="flex items-center gap-2">
              <Headphones className="w-4 h-4 text-nvidia-green" />
              <span className="text-gray-400">Agent:</span>
              <span className="text-white">{transcript.agent.name}</span>
              <span className="text-gray-500">({transcript.agent.experienceLevel})</span>
            </div>
          </div>

          {/* Conversation */}
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {transcript.conversation.map((turn, idx) => (
              <div
                key={idx}
                className={clsx(
                  'flex gap-3',
                  turn.speaker === 'customer' ? 'justify-start' : 'justify-end'
                )}
              >
                <div
                  className={clsx(
                    'max-w-[80%] px-4 py-2 rounded-lg text-sm',
                    turn.speaker === 'customer'
                      ? 'bg-blue-500/20 text-blue-100'
                      : 'bg-nvidia-green/20 text-green-100'
                  )}
                >
                  <span className="text-xs font-medium opacity-70 block mb-1">
                    {turn.speaker === 'customer' ? 'Customer' : 'Agent'}
                  </span>
                  {turn.text}
                </div>
              </div>
            ))}
          </div>

          {/* Metadata */}
          {transcript.metadata && (
            <div className="flex gap-4 text-xs text-gray-400 pt-2 border-t border-gray-700">
              <span>Duration: {Math.floor(transcript.metadata.durationSeconds / 60)}m {transcript.metadata.durationSeconds % 60}s</span>
              <span>Status: {transcript.metadata.resolutionStatus}</span>
              {transcript.metadata.csatScore && <span>CSAT: {transcript.metadata.csatScore}/5</span>}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
