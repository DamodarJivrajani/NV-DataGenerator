import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { X, Upload, Loader2, ExternalLink, Lock, Globe } from 'lucide-react'
import { api } from '@/services/api'

interface Props {
  jobId: string
  onClose: () => void
}

export function HFUploadModal({ jobId, onClose }: Props) {
  const [hfToken, setHfToken] = useState('')
  const [repoName, setRepoName] = useState('nv-contact-center-transcripts')
  const [isPrivate, setIsPrivate] = useState(true)
  const [format, setFormat] = useState('json')
  const [repoUrl, setRepoUrl] = useState<string | null>(null)

  const uploadMutation = useMutation({
    mutationFn: () =>
      api.uploadToHF(jobId, {
        hf_token: hfToken,
        repo_name: repoName,
        private: isPrivate,
        format,
      }),
    onSuccess: (data) => setRepoUrl(data.repo_url),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-md mx-4 p-6 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-nvidia-green" />
            Publish to HuggingFace Hub
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {repoUrl ? (
          /* Success state */
          <div className="space-y-4">
            <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 text-center">
              <div className="text-green-400 font-semibold mb-2">✓ Dataset Published!</div>
              <a
                href={repoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-nvidia-green hover:underline flex items-center justify-center gap-1"
              >
                {repoUrl}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <button onClick={onClose} className="btn-secondary w-full">Close</button>
          </div>
        ) : (
          /* Form */
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">HuggingFace Token</label>
              <input
                type="password"
                value={hfToken}
                onChange={(e) => setHfToken(e.target.value)}
                placeholder="hf_..."
                className="input w-full font-mono text-sm"
              />
              <p className="text-xs text-gray-500">
                Token is used only for this upload and never stored.{' '}
                <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-nvidia-green hover:underline">
                  Get a token ↗
                </a>
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Repository Name</label>
              <input
                type="text"
                value={repoName}
                onChange={(e) => setRepoName(e.target.value)}
                placeholder="my-dataset-name"
                className="input w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="input w-full"
              >
                <option value="json">JSON</option>
                <option value="jsonl">JSONL</option>
                <option value="sft">SFT (prompt/response)</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsPrivate(!isPrivate)}
                className={`w-12 h-6 rounded-full transition-colors relative ${isPrivate ? 'bg-nvidia-green' : 'bg-gray-700'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${isPrivate ? 'translate-x-6' : 'translate-x-0.5'}`} />
              </button>
              <div className="flex items-center gap-2 text-sm text-white">
                {isPrivate ? <Lock className="w-4 h-4 text-gray-400" /> : <Globe className="w-4 h-4 text-nvidia-green" />}
                {isPrivate ? 'Private repository' : 'Public repository'}
              </div>
            </div>

            {uploadMutation.isError && (
              <p className="text-red-400 text-sm">{(uploadMutation.error as Error).message}</p>
            )}

            <div className="flex gap-3 pt-2">
              <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
              <button
                onClick={() => uploadMutation.mutate()}
                disabled={!hfToken || !repoName || uploadMutation.isPending}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {uploadMutation.isPending ? (
                  <><Loader2 className="w-4 h-4 animate-spin" />Uploading...</>
                ) : (
                  <><Upload className="w-4 h-4" />Publish</>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
