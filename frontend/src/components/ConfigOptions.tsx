import { clsx } from 'clsx'
import { Check, Phone, PhoneOutgoing, Minus, Plus } from 'lucide-react'
import { sentiments, callTypes, languages } from '../data/industries'
import { useConfigStore } from '../stores/configStore'
import type { Sentiment, CallType, Language } from '../types'

export function ConfigOptions() {
    const { config, toggleCallType, toggleSentiment, setNumRecords, setTurnRange, setIncludeMetadata, setLanguage } = useConfigStore()

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-white mb-2">Configure Generation</h2>
                <p className="text-gray-400">Fine-tune your synthetic transcript generation settings</p>
            </div>

            {/* Language Selection */}
            <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Output Language</h3>
                <p className="text-sm text-gray-400">Generate all dialogue in the selected language</p>
                <div className="flex flex-wrap gap-2">
                    {languages.map((lang) => {
                        const isSelected = config.language === lang.id
                        return (
                            <button
                                key={lang.id}
                                onClick={() => setLanguage(lang.id as Language)}
                                className={clsx(
                                    'px-3 py-2 rounded-lg border transition-all flex items-center gap-2 text-sm',
                                    isSelected
                                        ? 'bg-nvidia-green/10 border-nvidia-green text-nvidia-green'
                                        : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600'
                                )}
                            >
                                <span>{lang.flag}</span>
                                <span>{lang.name}</span>
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Call Types */}
            <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Call Direction</h3>
                <div className="flex gap-3">
                    {callTypes.map((type) => {
                        const isSelected = config.callTypes.includes(type.id as CallType)
                        return (
                            <button
                                key={type.id}
                                onClick={() => toggleCallType(type.id as CallType)}
                                className={clsx(
                                    'flex items-center gap-3 px-4 py-3 rounded-lg border transition-all',
                                    isSelected
                                        ? 'bg-nvidia-green/10 border-nvidia-green'
                                        : 'bg-gray-800 border-gray-700 hover:border-gray-600'
                                )}
                            >
                                <div
                                    className={clsx(
                                        'w-5 h-5 rounded border-2 flex items-center justify-center',
                                        isSelected ? 'bg-nvidia-green border-nvidia-green' : 'border-gray-600'
                                    )}
                                >
                                    {isSelected && <Check className="w-3 h-3 text-black" />}
                                </div>
                                {type.id === 'inbound' ? (
                                    <Phone className="w-5 h-5 text-gray-400" />
                                ) : (
                                    <PhoneOutgoing className="w-5 h-5 text-gray-400" />
                                )}
                                <div className="text-left">
                                    <div className="text-white font-medium">{type.name}</div>
                                    <div className="text-xs text-gray-400">{type.description}</div>
                                </div>
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Customer Sentiments */}
            <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Customer Sentiments</h3>
                <p className="text-sm text-gray-400">Select the emotional states to include in generated transcripts</p>
                <div className="flex flex-wrap gap-2">
                    {sentiments.map((sentiment) => {
                        const isSelected = config.sentiments.includes(sentiment.id as Sentiment)
                        return (
                            <button
                                key={sentiment.id}
                                onClick={() => toggleSentiment(sentiment.id as Sentiment)}
                                className={clsx(
                                    'px-4 py-2 rounded-full border transition-all flex items-center gap-2',
                                    isSelected
                                        ? 'bg-nvidia-green/10 border-nvidia-green text-nvidia-green'
                                        : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600'
                                )}
                            >
                                <span className={isSelected ? sentiment.color : ''}>{sentiment.name}</span>
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Number of Records */}
            <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Number of Transcripts</h3>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setNumRecords(Math.max(1, config.numRecords - 10))}
                        className="w-10 h-10 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center hover:bg-gray-700 transition-colors"
                    >
                        <Minus className="w-4 h-4" />
                    </button>
                    <input
                        type="number"
                        value={config.numRecords}
                        onChange={(e) => setNumRecords(Math.max(1, Math.min(1000, parseInt(e.target.value) || 1)))}
                        className="input w-32 text-center text-lg font-semibold"
                        min="1"
                        max="1000"
                    />
                    <button
                        onClick={() => setNumRecords(Math.min(1000, config.numRecords + 10))}
                        className="w-10 h-10 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center hover:bg-gray-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                    </button>
                </div>
                <p className="text-sm text-gray-400">
                    Generate up to 1,000 synthetic transcripts. Preview shows first 5.
                </p>
            </div>

            {/* Conversation Turns */}
            <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Conversation Length</h3>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400">Min:</span>
                        <input
                            type="number"
                            value={config.minTurns}
                            onChange={(e) => setTurnRange(Math.max(2, parseInt(e.target.value) || 2), config.maxTurns)}
                            className="input w-20 text-center"
                            min="2"
                            max="20"
                        />
                    </div>
                    <span className="text-gray-500">to</span>
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400">Max:</span>
                        <input
                            type="number"
                            value={config.maxTurns}
                            onChange={(e) => setTurnRange(config.minTurns, Math.max(config.minTurns, parseInt(e.target.value) || 4))}
                            className="input w-20 text-center"
                            min="2"
                            max="50"
                        />
                    </div>
                    <span className="text-gray-400">turns</span>
                </div>
            </div>

            {/* Include Metadata */}
            <div className="flex items-center gap-3">
                <button
                    onClick={() => setIncludeMetadata(!config.includeMetadata)}
                    className={clsx(
                        'w-12 h-6 rounded-full transition-colors relative',
                        config.includeMetadata ? 'bg-nvidia-green' : 'bg-gray-700'
                    )}
                >
                    <div
                        className={clsx(
                            'w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform',
                            config.includeMetadata ? 'translate-x-6' : 'translate-x-0.5'
                        )}
                    />
                </button>
                <div>
                    <span className="text-white font-medium">Include Metadata</span>
                    <p className="text-sm text-gray-400">Add call duration, CSAT scores, resolution status</p>
                </div>
            </div>
        </div>
    )
}
