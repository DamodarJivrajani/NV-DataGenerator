import { useState } from 'react'
import { Sparkles, Settings } from 'lucide-react'
import { SettingsModal } from './SettingsModal'
import { API_URL } from '@/services/api'

// API docs live at the backend origin (strip the /api/v1 path segment).
const DOCS_URL = `${API_URL.replace(/\/api\/v1\/?$/, '')}/docs`

export function Header() {
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <>
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-nvidia-green rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-black" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Contact Center Data Generator</h1>
              <p className="text-xs text-gray-400">Powered by Data Designer</p>
            </div>
          </div>
          <nav className="flex items-center gap-4">
            <button
              onClick={() => setSettingsOpen(true)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-gray-800"
              title="API Settings"
            >
              <Settings className="w-5 h-5" />
              <span className="hidden md:inline">Settings</span>
            </button>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Docs</a>
            <a href={DOCS_URL} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">API</a>
            <a
              href="https://build.nvidia.com/nemo/data-designer"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-sm"
            >
              Data Designer
            </a>
          </nav>
        </div>
      </header>

      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </>
  )
}
