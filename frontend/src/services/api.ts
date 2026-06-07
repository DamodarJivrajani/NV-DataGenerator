import type { GenerationConfig, GenerationJob, Transcript, BiasReport, DatasetStats, CurationResult } from '@/types'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Generate preview (small batch for testing)
  generatePreview: (config: GenerationConfig): Promise<{ transcripts: Transcript[] }> =>
    fetchApi('/generate/preview', {
      method: 'POST',
      body: JSON.stringify(config),
    }),

  // Start batch generation job
  startGeneration: (config: GenerationConfig): Promise<GenerationJob> =>
    fetchApi('/generate/batch', {
      method: 'POST',
      body: JSON.stringify(config),
    }),

  // Get job status
  getJob: (jobId: string): Promise<GenerationJob> =>
    fetchApi(`/jobs/${jobId}`),

  // Get a job's generated transcripts for in-app viewing (text, voice, KPIs)
  getJobResults: (jobId: string): Promise<{ transcripts: Transcript[] }> =>
    fetchApi(`/jobs/${jobId}/results`),

  // List all jobs
  listJobs: (): Promise<GenerationJob[]> =>
    fetchApi('/jobs'),

  // Delete a job
  deleteJob: (jobId: string): Promise<{ message: string }> =>
    fetchApi(`/jobs/${jobId}`, { method: 'DELETE' }),

  // Download generated data
  downloadJob: async (jobId: string, format: 'json' | 'csv' | 'jsonl' | 'sft' | 'sft_instruct' | 'curated' | 'audio' | 'dpo' = 'json'): Promise<Blob> => {
    const response = await fetch(`${API_URL}/jobs/${jobId}/download?format=${format}`)
    if (!response.ok) {
      // Surface the server's reason (e.g. background generation not finished yet)
      // instead of a generic failure, since curated/audio/dpo are produced async.
      const error = await response.json().catch(() => ({ detail: `Download failed (HTTP ${response.status})` }))
      throw new Error(error.detail || `Download failed (HTTP ${response.status})`)
    }
    return response.blob()
  },

  // Score transcripts using LLM quality judge
  scoreJob: (jobId: string): Promise<{ message: string; job_id: string }> =>
    fetchApi(`/jobs/${jobId}/score`, { method: 'POST' }),

  // Get bias & safety report
  getBiasReport: (jobId: string): Promise<BiasReport> =>
    fetchApi(`/jobs/${jobId}/bias-report`),

  // Get dataset statistics
  getJobStatistics: (jobId: string): Promise<DatasetStats> =>
    fetchApi(`/jobs/${jobId}/statistics`),

  // Run NeMo Curator-inspired curation
  curateJob: (
    jobId: string,
    opts: { min_quality_score: number; deduplicate: boolean; filter_pii: boolean }
  ): Promise<CurationResult> =>
    fetchApi(`/jobs/${jobId}/curate`, {
      method: 'POST',
      body: JSON.stringify(opts),
    }),

  // Upload to HuggingFace Hub
  uploadToHF: (
    jobId: string,
    opts: { hf_token: string; repo_name: string; private: boolean; format: string }
  ): Promise<{ repo_url: string; files_uploaded: string[] }> =>
    fetchApi(`/jobs/${jobId}/upload-hf`, {
      method: 'POST',
      body: JSON.stringify(opts),
    }),

  // Generate DPO dataset
  generateDPO: (jobId: string): Promise<{ message: string; job_id: string }> =>
    fetchApi(`/jobs/${jobId}/generate-dpo`, { method: 'POST' }),

  // Generate audio (Riva TTS)
  generateAudio: (jobId: string): Promise<{ message: string; job_id: string; riva_available: boolean }> =>
    fetchApi(`/jobs/${jobId}/generate-audio`, { method: 'POST' }),

  // Health check
  health: (): Promise<{ status: string }> =>
    fetchApi('/health'),
}
