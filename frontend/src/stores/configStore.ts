import { create } from 'zustand'
import type { GenerationConfig, Sentiment, CallType, Language } from '@/types'

interface ConfigState {
  config: GenerationConfig
  step: number
  setIndustry: (industry: string) => void
  toggleScenario: (scenario: string) => void
  toggleCallType: (callType: CallType) => void
  toggleSentiment: (sentiment: Sentiment) => void
  setNumRecords: (num: number) => void
  setTurnRange: (min: number, max: number) => void
  setIncludeMetadata: (include: boolean) => void
  setLanguage: (language: Language) => void
  setStep: (step: number) => void
  nextStep: () => void
  prevStep: () => void
  reset: () => void
}

const defaultConfig: GenerationConfig = {
  industry: '',
  scenarios: [],
  callTypes: ['inbound'],
  sentiments: ['neutral', 'frustrated', 'satisfied'],
  numRecords: 10,
  minTurns: 4,
  maxTurns: 12,
  includeMetadata: true,
  language: 'english',
}

export const useConfigStore = create<ConfigState>((set) => ({
  config: defaultConfig,
  step: 0,

  setIndustry: (industry) =>
    set((state) => ({
      config: { ...state.config, industry, scenarios: [] },
    })),

  toggleScenario: (scenario) =>
    set((state) => ({
      config: {
        ...state.config,
        scenarios: state.config.scenarios.includes(scenario)
          ? state.config.scenarios.filter((s) => s !== scenario)
          : [...state.config.scenarios, scenario],
      },
    })),

  toggleCallType: (callType) =>
    set((state) => ({
      config: {
        ...state.config,
        callTypes: state.config.callTypes.includes(callType)
          ? state.config.callTypes.filter((c) => c !== callType)
          : [...state.config.callTypes, callType],
      },
    })),

  toggleSentiment: (sentiment) =>
    set((state) => ({
      config: {
        ...state.config,
        sentiments: state.config.sentiments.includes(sentiment)
          ? state.config.sentiments.filter((s) => s !== sentiment)
          : [...state.config.sentiments, sentiment],
      },
    })),

  setNumRecords: (numRecords) =>
    set((state) => ({
      config: { ...state.config, numRecords },
    })),

  setTurnRange: (minTurns, maxTurns) =>
    set((state) => ({
      config: { ...state.config, minTurns, maxTurns },
    })),

  setIncludeMetadata: (includeMetadata) =>
    set((state) => ({
      config: { ...state.config, includeMetadata },
    })),

  setLanguage: (language) =>
    set((state) => ({
      config: { ...state.config, language },
    })),

  setStep: (step) => set({ step: Math.min(4, Math.max(0, step)) }),
  // 5 wizard steps (0..4); clamp so we never render the fall-through default.
  nextStep: () => set((state) => ({ step: Math.min(4, state.step + 1) })),
  prevStep: () => set((state) => ({ step: Math.max(0, state.step - 1) })),
  reset: () => set({ config: defaultConfig, step: 0 }),
}))
