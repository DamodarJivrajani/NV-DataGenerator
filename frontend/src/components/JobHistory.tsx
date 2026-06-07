import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle, Loader2, Download, Eye } from 'lucide-react'
import { api } from '@/services/api'
import type { GenerationJob } from '@/types'

export function JobHistory() {
  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: api.listJobs,
    // Only poll while something is actually in progress; otherwise stop so we
    // don't hammer /jobs forever on an idle, open tab.
    refetchInterval: (query) => {
      const data = query.state.data as GenerationJob[] | undefined
      const active = data?.some((j) => j.status === 'running' || j.status === 'pending')
      return active ? 5000 : false
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  if (!jobs || jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p>No generation jobs yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-white">Recent Jobs</h3>
      <div className="space-y-2">
        {jobs.map((job) => (
          <JobRow key={job.id} job={job} />
        ))}
      </div>
    </div>
  )
}

function JobRow({ job }: { job: GenerationJob }) {
  const handleDownload = async (format: 'json' | 'csv' | 'jsonl') => {
    try {
      const blob = await api.downloadJob(job.id, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `transcripts-${job.id.slice(0, 8)}.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon status={job.status} />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-white font-medium capitalize">
                {job.config.industry}
              </span>
              <span className="text-xs text-gray-500">
                {job.id.slice(0, 8)}
              </span>
            </div>
            <div className="text-xs text-gray-400">
              {job.completedRecords}/{job.totalRecords} records
              {job.status === 'running' && ` • ${Math.round(job.progress)}%`}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {job.status === 'completed' && (
            <div className="flex gap-1">
              <Link
                to={`/transcripts/${job.id}`}
                className="flex items-center gap-1 px-2 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-gray-700 rounded"
                title="View transcripts, KPIs & listen"
              >
                <Eye className="w-4 h-4" />
                View
              </Link>
              <button
                onClick={() => handleDownload('json')}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                title="Download JSON"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          )}
          <span className="text-xs text-gray-500">
            {new Date(job.createdAt).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {job.status === 'running' && (
        <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-nvidia-green transition-all"
            style={{ width: `${job.progress}%` }}
          />
        </div>
      )}

      {job.error && (
        <p className="mt-2 text-xs text-red-400">{job.error}</p>
      )}
    </div>
  )
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-nvidia-green" />
    case 'failed':
      return <XCircle className="w-5 h-5 text-red-500" />
    case 'running':
      return <Loader2 className="w-5 h-5 text-nvidia-green animate-spin" />
    default:
      return <Clock className="w-5 h-5 text-gray-400" />
  }
}
