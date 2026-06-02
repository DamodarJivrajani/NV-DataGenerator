import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Download, Loader2, CheckCircle, XCircle, Clock, FileJson, FileText, Table, 
         Brain, Shield, BarChart2, Upload, Mic, Sparkles } from 'lucide-react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { JobHistory } from './JobHistory'
import { StatsDashboard } from './StatsDashboard'
import { BiasReportPanel } from './BiasReport'
import { HFUploadModal } from './HFUploadModal'
import type { GenerationJob, DatasetStats, BiasReport, CurationResult } from '@/types'

export function ExportPanel() {
  const { config } = useConfigStore()
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const [showStats, setShowStats] = useState(false)
  const [showBias, setShowBias] = useState(false)
  const [showHFModal, setShowHFModal] = useState(false)
  const [curationOpts, setCurationOpts] = useState({ min_quality_score: 0, deduplicate: true, filter_pii: true })
  const [curationResult, setCurationResult] = useState<CurationResult | null>(null)
  const [audioResult, setAudioResult] = useState<{ riva_available: boolean } | null>(null)
  const [dpoStarted, setDpoStarted] = useState(false)
  const [scoringDone, setScoringDone] = useState(false)
  const [stats, setStats] = useState<DatasetStats | null>(null)
  const [biasReport, setBiasReport] = useState<BiasReport | null>(null)

  const startJobMutation = useMutation({
    mutationFn: () => api.startGeneration(config),
    onSuccess: (job) => {
      setActiveJobId(job.id)
      // Reset all derivative state when starting new job
      setCurationResult(null)
      setAudioResult(null)
      setDpoStarted(false)
      setScoringDone(false)
      setStats(null)
      setBiasReport(null)
    },
  })

  const { data: job } = useQuery({
    queryKey: ['job', activeJobId],
    queryFn: () => api.getJob(activeJobId!),
    enabled: !!activeJobId,
    refetchInterval: (query) => {
      const data = query.state.data as GenerationJob | undefined
      return data?.status === 'running' || data?.status === 'pending' ? 2000 : false
    },
  })

  const downloadMutation = useMutation({
    mutationFn: ({ jobId, format }: { jobId: string; format: string }) =>
      api.downloadJob(jobId, format as 'json'),
    onSuccess: (blob, { format }) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const ext = format === 'csv' ? 'csv' : format === 'json' ? 'json' : 'jsonl'
      a.download = `transcripts_${format}.${ext}`
      a.click()
      URL.revokeObjectURL(url)
    },
  })

  const scoreMutation = useMutation({
    mutationFn: (jobId: string) => api.scoreJob(jobId),
    onSuccess: () => setScoringDone(true),
  })

  const curateMutation = useMutation({
    mutationFn: ({ jobId, opts }: { jobId: string; opts: typeof curationOpts }) =>
      api.curateJob(jobId, opts),
    onSuccess: (result) => setCurationResult(result),
  })

  const statsMutation = useMutation({
    mutationFn: (jobId: string) => api.getJobStatistics(jobId),
    onSuccess: (data) => { setStats(data); setShowStats(true) },
  })

  const biasMutation = useMutation({
    mutationFn: (jobId: string) => api.getBiasReport(jobId),
    onSuccess: (data) => { setBiasReport(data); setShowBias(true) },
  })

  const dpoMutation = useMutation({
    mutationFn: (jobId: string) => api.generateDPO(jobId),
    onSuccess: () => setDpoStarted(true),
  })

  const audioMutation = useMutation({
    mutationFn: (jobId: string) => api.generateAudio(jobId),
    onSuccess: (data) => setAudioResult(data),
  })

  const isCompleted = job?.status === 'completed'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Generate & Export</h2>
        <p className="text-gray-400">
          Start full generation and download your synthetic transcripts
        </p>
      </div>

      {/* Config Summary */}
      <div className="bg-gray-800/50 rounded-lg p-4 space-y-2">
        <h3 className="text-sm font-semibold text-gray-400 uppercase">Generation Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Industry:</span>
            <span className="text-white ml-2 capitalize">{config.industry}</span>
          </div>
          <div>
            <span className="text-gray-500">Scenarios:</span>
            <span className="text-white ml-2">{config.scenarios.length}</span>
          </div>
          <div>
            <span className="text-gray-500">Records:</span>
            <span className="text-white ml-2">{config.numRecords}</span>
          </div>
          <div>
            <span className="text-gray-500">Language:</span>
            <span className="text-white ml-2 capitalize">{config.language}</span>
          </div>
        </div>
      </div>

      {/* Start Generation */}
      {!activeJobId && (
        <button
          onClick={() => startJobMutation.mutate()}
          disabled={startJobMutation.isPending}
          className="btn-primary w-full py-4 text-lg flex items-center justify-center gap-2"
        >
          {startJobMutation.isPending ? (
            <><Loader2 className="w-5 h-5 animate-spin" />Starting...</>
          ) : (
            <><Download className="w-5 h-5" />Generate {config.numRecords} Transcripts</>
          )}
        </button>
      )}

      {/* Job Status */}
      {job && (
        <div className="space-y-4">
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <JobStatusIcon status={job.status} />
                <div>
                  <span className="text-white font-medium capitalize">{job.status}</span>
                  <span className="text-gray-500 text-sm ml-2">Job {job.id.slice(0, 8)}</span>
                </div>
              </div>
              <span className="text-gray-400 text-sm">
                {job.completedRecords} / {job.totalRecords} records
              </span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={clsx(
                  'h-full transition-all duration-500',
                  job.status === 'completed' ? 'bg-nvidia-green' :
                  job.status === 'failed' ? 'bg-red-500' : 'bg-nvidia-green/70'
                )}
                style={{ width: `${job.progress}%` }}
              />
            </div>
            {job.error && <p className="text-red-400 text-sm mt-2">{job.error}</p>}
          </div>

          {isCompleted && (
            <>
              {/* ── Download ─────────────────────────────────────── */}
              <Section title="Download" icon={<Download className="w-4 h-4" />}>
                <div className="grid grid-cols-3 gap-3">
                  {(['json', 'jsonl', 'csv'] as const).map((fmt) => (
                    <DownloadButton
                      key={fmt}
                      label={fmt.toUpperCase()}
                      icon={fmt === 'csv' ? <Table className="w-5 h-5" /> : <FileJson className="w-5 h-5" />}
                      onClick={() => downloadMutation.mutate({ jobId: job.id, format: fmt })}
                      isLoading={downloadMutation.isPending}
                    />
                  ))}
                </div>
              </Section>

              {/* ── Fine-Tuning Formats ──────────────────────────── */}
              <Section title="Fine-Tuning Formats" icon={<Sparkles className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Export for LLM fine-tuning pipelines</p>
                <div className="grid grid-cols-2 gap-3">
                  <DownloadButton
                    label="SFT Format"
                    icon={<FileText className="w-5 h-5" />}
                    onClick={() => downloadMutation.mutate({ jobId: job.id, format: 'sft' })}
                    isLoading={downloadMutation.isPending}
                    description="{prompt, response}"
                  />
                  <DownloadButton
                    label="SFT Instruct"
                    icon={<FileText className="w-5 h-5" />}
                    onClick={() => downloadMutation.mutate({ jobId: job.id, format: 'sft_instruct' })}
                    isLoading={downloadMutation.isPending}
                    description="{messages: [...]}"
                  />
                  <div className="col-span-2">
                    {!dpoStarted ? (
                      <button
                        onClick={() => dpoMutation.mutate(job.id)}
                        disabled={dpoMutation.isPending}
                        className="btn-secondary w-full flex items-center justify-center gap-2 py-3"
                      >
                        {dpoMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                        Generate DPO Dataset (chosen/rejected)
                      </button>
                    ) : (
                      <div className="flex gap-3">
                        <div className="flex-1 bg-green-900/20 border border-green-700 rounded-lg p-3 text-sm text-green-400">
                          ✓ DPO generation started in background
                        </div>
                        <DownloadButton
                          label="Download DPO"
                          icon={<Download className="w-4 h-4" />}
                          onClick={() => downloadMutation.mutate({ jobId: job.id, format: 'dpo' })}
                          isLoading={downloadMutation.isPending}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </Section>

              {/* ── Quality Scoring ──────────────────────────────── */}
              <Section title="Quality Scoring" icon={<Brain className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Score transcripts using LLM judge (coherence, diversity, factual consistency)</p>
                {!scoringDone ? (
                  <button
                    onClick={() => scoreMutation.mutate(job.id)}
                    disabled={scoreMutation.isPending}
                    className="btn-secondary w-full flex items-center justify-center gap-2"
                  >
                    {scoreMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                    {scoreMutation.isPending ? 'Scoring...' : 'Run Quality Scoring'}
                  </button>
                ) : (
                  <div className="bg-green-900/20 border border-green-700 rounded-lg p-3 text-sm text-green-400">
                    ✓ Quality scores added to all transcripts
                  </div>
                )}
                {scoreMutation.isError && (
                  <p className="text-red-400 text-sm mt-2">{(scoreMutation.error as Error).message}</p>
                )}
              </Section>

              {/* ── NeMo Curator ─────────────────────────────────── */}
              <Section title="NeMo Curator-Inspired Curation" icon={<Shield className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Deduplicate, remove PII, and filter by quality threshold</p>
                <div className="space-y-3 mb-4">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={curationOpts.deduplicate}
                      onChange={(e) => setCurationOpts(o => ({ ...o, deduplicate: e.target.checked }))}
                      className="w-4 h-4 accent-nvidia-green"
                    />
                    <span className="text-sm text-white">Deduplicate (Jaccard similarity ≥ 0.85)</span>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={curationOpts.filter_pii}
                      onChange={(e) => setCurationOpts(o => ({ ...o, filter_pii: e.target.checked }))}
                      className="w-4 h-4 accent-nvidia-green"
                    />
                    <span className="text-sm text-white">Remove PII (phone, SSN, email, card numbers)</span>
                  </label>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-white w-40">Min Quality Score:</span>
                    <input
                      type="range"
                      min="0" max="10" step="0.5"
                      value={curationOpts.min_quality_score}
                      onChange={(e) => setCurationOpts(o => ({ ...o, min_quality_score: parseFloat(e.target.value) }))}
                      className="flex-1 accent-nvidia-green"
                    />
                    <span className="text-nvidia-green font-mono w-8">{curationOpts.min_quality_score}</span>
                  </div>
                </div>
                {!curationResult ? (
                  <button
                    onClick={() => curateMutation.mutate({ jobId: job.id, opts: curationOpts })}
                    disabled={curateMutation.isPending}
                    className="btn-secondary w-full flex items-center justify-center gap-2"
                  >
                    {curateMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                    {curateMutation.isPending ? 'Curating...' : 'Run Curation'}
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-3 text-center text-sm">
                      <StatBox label="Original" value={curationResult.originalCount} />
                      <StatBox label="After Dedup" value={curationResult.deduplicatedCount} />
                      <StatBox label="Final" value={curationResult.finalCount} color="text-nvidia-green" />
                    </div>
                    <DownloadButton
                      label="Download Curated"
                      icon={<Download className="w-4 h-4" />}
                      onClick={() => downloadMutation.mutate({ jobId: job.id, format: 'curated' })}
                      isLoading={downloadMutation.isPending}
                    />
                  </div>
                )}
              </Section>

              {/* ── Statistics Dashboard ─────────────────────────── */}
              <Section title="Dataset Statistics" icon={<BarChart2 className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Visualize distribution and quality metrics of the generated dataset</p>
                <button
                  onClick={() => statsMutation.mutate(job.id)}
                  disabled={statsMutation.isPending}
                  className="btn-secondary w-full flex items-center justify-center gap-2"
                >
                  {statsMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <BarChart2 className="w-4 h-4" />}
                  {statsMutation.isPending ? 'Computing...' : stats ? 'Refresh Statistics' : 'Compute Statistics'}
                </button>
                {showStats && stats && (
                  <div className="mt-4">
                    <StatsDashboard stats={stats} />
                  </div>
                )}
              </Section>

              {/* ── Bias & Safety Report ─────────────────────────── */}
              <Section title="Bias & Safety Analysis" icon={<Shield className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Analyze gender bias, sentiment distribution, demographic diversity, and safety flags</p>
                <button
                  onClick={() => biasMutation.mutate(job.id)}
                  disabled={biasMutation.isPending}
                  className="btn-secondary w-full flex items-center justify-center gap-2"
                >
                  {biasMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                  {biasMutation.isPending ? 'Analyzing...' : biasReport ? 'Refresh Report' : 'Run Bias Analysis'}
                </button>
                {showBias && biasReport && (
                  <div className="mt-4">
                    <BiasReportPanel report={biasReport} />
                  </div>
                )}
              </Section>

              {/* ── Audio Generation ─────────────────────────────── */}
              <Section title="Audio Generation (NVIDIA Riva TTS)" icon={<Mic className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Generate audio files for each conversation using NVIDIA Riva TTS</p>
                {!audioResult ? (
                  <button
                    onClick={() => audioMutation.mutate(job.id)}
                    disabled={audioMutation.isPending}
                    className="btn-secondary w-full flex items-center justify-center gap-2"
                  >
                    {audioMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
                    {audioMutation.isPending ? 'Starting...' : 'Generate Audio'}
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className={clsx(
                      'rounded-lg p-3 text-sm',
                      audioResult.riva_available
                        ? 'bg-green-900/20 border border-green-700 text-green-400'
                        : 'bg-yellow-900/20 border border-yellow-700 text-yellow-400'
                    )}>
                      {audioResult.riva_available
                        ? '✓ Audio generation started (NVIDIA Riva connected)'
                        : '⚠ Audio generation started (fallback to silence WAV — set RIVA_ENDPOINT to use real TTS)'}
                    </div>
                    <DownloadButton
                      label="Download Audio ZIP"
                      icon={<Download className="w-4 h-4" />}
                      onClick={() => downloadMutation.mutate({ jobId: job.id, format: 'audio' })}
                      isLoading={downloadMutation.isPending}
                    />
                  </div>
                )}
              </Section>

              {/* ── HuggingFace Hub ──────────────────────────────── */}
              <Section title="Publish to HuggingFace Hub" icon={<Upload className="w-4 h-4" />}>
                <p className="text-sm text-gray-400 mb-3">Upload dataset to HuggingFace Hub as a public or private repository</p>
                <button
                  onClick={() => setShowHFModal(true)}
                  className="btn-secondary w-full flex items-center justify-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Upload to HuggingFace Hub
                </button>
              </Section>
            </>
          )}
        </div>
      )}

      {/* Job History */}
      <div className="border-t border-gray-700 pt-6">
        <JobHistory />
      </div>

      {/* HF Upload Modal */}
      {showHFModal && activeJobId && (
        <HFUploadModal
          jobId={activeJobId}
          onClose={() => setShowHFModal(false)}
        />
      )}
    </div>
  )
}


function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="border border-gray-700 rounded-lg p-4 space-y-3">
      <h3 className="text-base font-semibold text-white flex items-center gap-2">
        <span className="text-nvidia-green">{icon}</span>
        {title}
      </h3>
      {children}
    </div>
  )
}

function StatBox({ label, value, color = 'text-white' }: { label: string; value: number; color?: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  )
}

function JobStatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-6 h-6 text-nvidia-green" />
    case 'failed':
      return <XCircle className="w-6 h-6 text-red-500" />
    case 'running':
      return <Loader2 className="w-6 h-6 text-nvidia-green animate-spin" />
    default:
      return <Clock className="w-6 h-6 text-gray-400" />
  }
}

interface DownloadButtonProps {
  icon: React.ReactNode
  label: string
  onClick: () => void
  isLoading: boolean
  description?: string
}

function DownloadButton({ icon, label, onClick, isLoading, description }: DownloadButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="btn-secondary flex flex-col items-center gap-1 py-3 px-4 text-center"
    >
      {icon}
      <span className="text-sm">{label}</span>
      {description && <span className="text-xs text-gray-500">{description}</span>}
    </button>
  )
}

