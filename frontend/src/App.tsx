import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Header } from './components/Header'
import { IndustrySelector } from './components/IndustrySelector'
import { ScenarioSelector } from './components/ScenarioSelector'
import { ConfigOptions } from './components/ConfigOptions'
import { TranscriptPreview } from './components/TranscriptPreview'
import { ExportPanel } from './components/ExportPanel'
import { TranscriptViewer } from './components/TranscriptViewer'
import { useConfigStore } from './stores/configStore'
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react'

const steps = [
    { id: 0, name: 'Industry', description: 'Select your industry' },
    { id: 1, name: 'Scenarios', description: 'Choose call scenarios' },
    { id: 2, name: 'Options', description: 'Configure generation' },
    { id: 3, name: 'Preview', description: 'Review & generate' },
    { id: 4, name: 'Export', description: 'Download results' },
]

function ConfigWizard() {
    const { step, nextStep, prevStep, reset, config } = useConfigStore()

    const canProceed = () => {
        switch (step) {
            case 0: return config.industry !== ''
            case 1: return config.scenarios.length > 0
            case 2: return config.callTypes.length > 0 && config.sentiments.length > 0
            case 3: return true
            case 4: return true
            default: return false
        }
    }

    const renderStep = () => {
        switch (step) {
            case 0: return <IndustrySelector />
            case 1: return <ScenarioSelector />
            case 2: return <ConfigOptions />
            case 3: return <TranscriptPreview />
            case 4: return <ExportPanel />
            default: return <IndustrySelector />
        }
    }

    return (
        <div className="min-h-screen bg-gray-950">
            <Header />

            <main className="max-w-7xl mx-auto px-4 py-8">
                {/* Progress Steps */}
                <div className="mb-8">
                    <div className="flex items-center justify-between max-w-3xl mx-auto">
                        {steps.map((s, idx) => (
                            <div key={s.id} className="flex items-center">
                                <div className="flex flex-col items-center">
                                    <div
                                        className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${step > idx
                                                ? 'bg-nvidia-green text-black'
                                                : step === idx
                                                    ? 'bg-nvidia-green/20 border-2 border-nvidia-green text-nvidia-green'
                                                    : 'bg-gray-800 text-gray-500'
                                            }`}
                                    >
                                        {step > idx ? '✓' : idx + 1}
                                    </div>
                                    <span className={`text-xs mt-2 ${step >= idx ? 'text-white' : 'text-gray-500'}`}>
                                        {s.name}
                                    </span>
                                </div>
                                {idx < steps.length - 1 && (
                                    <div
                                        className={`w-16 md:w-24 h-0.5 mx-2 ${step > idx ? 'bg-nvidia-green' : 'bg-gray-800'
                                            }`}
                                    />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Step Content */}
                <div className="card max-w-4xl mx-auto mb-8">
                    {renderStep()}
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between max-w-4xl mx-auto">
                    <div className="flex gap-2">
                        {step > 0 && (
                            <button onClick={prevStep} className="btn-secondary flex items-center gap-2">
                                <ChevronLeft className="w-4 h-4" />
                                Back
                            </button>
                        )}
                        <button onClick={reset} className="btn-secondary flex items-center gap-2">
                            <RotateCcw className="w-4 h-4" />
                            Reset
                        </button>
                    </div>

                    {step < steps.length - 1 && (
                        <button
                            onClick={nextStep}
                            disabled={!canProceed()}
                            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </main>
        </div>
    )
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ConfigWizard />} />
                <Route path="/transcripts/:jobId" element={<TranscriptViewer />} />
            </Routes>
        </BrowserRouter>
    )
}
