export type Language =
  | 'english'
  | 'spanish'
  | 'french'
  | 'german'
  | 'portuguese'
  | 'italian'
  | 'japanese'
  | 'mandarin'
  | 'hindi'
  | 'arabic'
  | 'korean'
  | 'dutch'
  | 'russian'

export interface QualityScores {
  coherence: number
  diversity: number
  factualConsistency: number
  overall: number
}

export interface BiasReport {
  genderBiasScore: number
  sentimentDistribution: Record<string, number>
  demographicDiversityScore: number
  safetyFlags: string[]
  overallFairnessGrade: string
  totalAnalyzed: number
}

export interface DatasetStats {
  sentimentDistribution: Record<string, number>
  turnLengthHistogram: Array<{ range: string; count: number }>
  industryBreakdown: Record<string, number>
  scenarioBreakdown: Record<string, number>
  languageDistribution: Record<string, number>
  resolutionStatusDistribution: Record<string, number>
  csatDistribution: Record<string, number>
  qualityScoreDistribution: Record<string, number>
  avgDurationSeconds: number
  totalTranscripts: number
}

export interface CurationResult {
  originalCount: number
  deduplicatedCount: number
  piiRemovedCount: number
  qualityFilteredCount: number
  finalCount: number
}

export interface Industry {
  id: string
  name: string
  description: string
  icon: string
  scenarios: Scenario[]
}

export interface Scenario {
  id: string
  name: string
  description: string
}

export interface CustomerProfile {
  name: string
  age: number
  sentiment: Sentiment
  issueComplexity: 'low' | 'medium' | 'high'
}

export interface AgentProfile {
  name: string
  department: string
  experienceLevel: 'junior' | 'mid' | 'senior'
}

export type Sentiment = 'frustrated' | 'neutral' | 'satisfied' | 'angry' | 'confused'
export type CallType = 'inbound' | 'outbound'

export interface ConversationTurn {
  speaker: 'agent' | 'customer'
  text: string
  timestamp?: string
}

export interface TranscriptMetadata {
  durationSeconds: number
  resolutionStatus: 'resolved' | 'escalated' | 'pending' | 'unresolved'
  csatScore: number | null
  callReasonPrimary: string
  callReasonSecondary?: string
  escalated: boolean
}

export interface Transcript {
  id: string
  industry: string
  scenario: string
  language?: Language
  callType: CallType
  customer: CustomerProfile
  agent: AgentProfile
  conversation: ConversationTurn[]
  metadata: TranscriptMetadata
  qualityScores?: QualityScores
  createdAt: string
}

export interface GenerationConfig {
  industry: string
  scenarios: string[]
  callTypes: CallType[]
  sentiments: Sentiment[]
  numRecords: number
  minTurns: number
  maxTurns: number
  includeMetadata: boolean
  language: Language
}

export interface GenerationJob {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  config: GenerationConfig
  progress: number
  totalRecords: number
  completedRecords: number
  createdAt: string
  completedAt?: string
  error?: string
}
