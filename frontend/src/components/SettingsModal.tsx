import { useState, useEffect, useRef } from 'react'
import { X, Key, CheckCircle, XCircle, Loader2, Eye, EyeOff, Save } from 'lucide-react'
import { clsx } from 'clsx'
import { API_URL } from '@/services/api'

interface SettingsModalProps {
    isOpen: boolean
    onClose: () => void
}

type ApiStatus = 'idle' | 'testing' | 'valid' | 'invalid'

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const [apiKey, setApiKey] = useState('')
    const [showKey, setShowKey] = useState(false)
    const [status, setStatus] = useState<ApiStatus>('idle')
    const [statusMessage, setStatusMessage] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const [saved, setSaved] = useState(false)
    // Cancel any in-flight request when the modal closes/unmounts so we never
    // setState on an unmounted component.
    const abortRef = useRef<AbortController | null>(null)

    useEffect(() => {
        return () => abortRef.current?.abort()
    }, [])

    // Clear the entered key from memory whenever the modal closes. The key is
    // never persisted to localStorage — it is held only by the backend session.
    useEffect(() => {
        if (!isOpen) {
            abortRef.current?.abort()
            setApiKey('')
            setStatus('idle')
            setStatusMessage('')
            setSaved(false)
        }
    }, [isOpen])

    const handleSave = async () => {
        setIsSaving(true)
        abortRef.current?.abort()
        abortRef.current = new AbortController()
        try {
            const response = await fetch(`${API_URL}/settings/api-key`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey }),
                signal: abortRef.current.signal,
            })

            if (response.ok) {
                setSaved(true)
                setTimeout(() => setSaved(false), 2000)
            } else {
                const data = await response.json().catch(() => ({}))
                setStatus('invalid')
                setStatusMessage(data.detail || 'Failed to save API key')
            }
        } catch (error) {
            if ((error as Error).name === 'AbortError') return
            setStatus('invalid')
            setStatusMessage('Failed to connect to backend server')
        } finally {
            setIsSaving(false)
        }
    }

    const handleTest = async () => {
        setStatus('testing')
        setStatusMessage('Testing API connection...')
        abortRef.current?.abort()
        abortRef.current = new AbortController()

        try {
            const response = await fetch(`${API_URL}/settings/test-api`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey }),
                signal: abortRef.current.signal,
            })

            const data = await response.json()

            if (response.ok && data.valid) {
                setStatus('valid')
                setStatusMessage(data.message || 'API key is valid!')
            } else {
                setStatus('invalid')
                setStatusMessage(data.message || 'API key is invalid')
            }
        } catch (error) {
            if ((error as Error).name === 'AbortError') return
            setStatus('invalid')
            setStatusMessage('Failed to connect to backend server')
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-800">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-nvidia-green/20 rounded-lg flex items-center justify-center">
                            <Key className="w-5 h-5 text-nvidia-green" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">API Settings</h2>
                            <p className="text-sm text-gray-400">Configure your NVIDIA API key</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* API Key Input */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">NVIDIA API Key</label>
                        <div className="relative">
                            <input
                                type={showKey ? 'text' : 'password'}
                                value={apiKey}
                                onChange={(e) => {
                                    setApiKey(e.target.value)
                                    setStatus('idle')
                                }}
                                placeholder="nvapi-xxxxxxxxxxxx"
                                className="input w-full pr-20"
                            />
                            <button
                                onClick={() => setShowKey(!showKey)}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded hover:bg-gray-700 transition-colors"
                            >
                                {showKey ? (
                                    <EyeOff className="w-4 h-4 text-gray-400" />
                                ) : (
                                    <Eye className="w-4 h-4 text-gray-400" />
                                )}
                            </button>
                        </div>
                        <p className="text-xs text-gray-500">
                            Get your API key from{' '}
                            <a
                                href="https://build.nvidia.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-nvidia-green hover:underline"
                            >
                                build.nvidia.com
                            </a>
                        </p>
                    </div>

                    {/* Status Message */}
                    {status !== 'idle' && (
                        <div className={clsx(
                            'flex items-center gap-3 p-4 rounded-lg',
                            status === 'testing' && 'bg-blue-900/20 border border-blue-800',
                            status === 'valid' && 'bg-green-900/20 border border-green-800',
                            status === 'invalid' && 'bg-red-900/20 border border-red-800'
                        )}>
                            {status === 'testing' && <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />}
                            {status === 'valid' && <CheckCircle className="w-5 h-5 text-green-400" />}
                            {status === 'invalid' && <XCircle className="w-5 h-5 text-red-400" />}
                            <span className={clsx(
                                'text-sm',
                                status === 'testing' && 'text-blue-300',
                                status === 'valid' && 'text-green-300',
                                status === 'invalid' && 'text-red-300'
                            )}>
                                {statusMessage}
                            </span>
                        </div>
                    )}

                    {/* Saved confirmation */}
                    {saved && (
                        <div className="flex items-center gap-2 text-nvidia-green text-sm">
                            <CheckCircle className="w-4 h-4" />
                            API key saved successfully!
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-gray-800 bg-gray-900/50">
                    <button
                        onClick={handleTest}
                        disabled={!apiKey || status === 'testing'}
                        className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {status === 'testing' ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <CheckCircle className="w-4 h-4" />
                        )}
                        Test Connection
                    </button>

                    <button
                        onClick={handleSave}
                        disabled={!apiKey || isSaving}
                        className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSaving ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Save className="w-4 h-4" />
                        )}
                        Save API Key
                    </button>
                </div>
            </div>
        </div>
    )
}
