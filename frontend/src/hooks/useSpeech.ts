import { useCallback, useEffect, useRef, useState } from 'react'
import type { ConversationTurn } from '@/types'

/**
 * In-browser text-to-speech for transcript conversations using the Web Speech
 * API (`window.speechSynthesis`). Works with zero backend/setup — no NVIDIA
 * Riva server required — so it is audible on the deployed demo.
 *
 * Agent and customer turns are spoken with distinct voices (and a pitch offset
 * as a fallback) so the conversation is easy to follow. Turns are spoken in
 * sequence; `currentIndex` tracks the active turn for UI highlighting.
 */

const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

// Best-effort gender-leaning voice name hints. Browsers don't expose gender on
// SpeechSynthesisVoice, so we match common voice names and fall back to pitch.
const FEMALE_HINTS = ['female', 'samantha', 'victoria', 'karen', 'moira', 'tessa', 'zira', 'fiona', 'serena']
const MALE_HINTS = ['male', 'daniel', 'alex', 'fred', 'rishi', 'david', 'mark', 'oliver', 'thomas']

function pickVoice(voices: SpeechSynthesisVoice[], hints: string[], fallbackIndex: number): SpeechSynthesisVoice | null {
  const english = voices.filter((v) => v.lang.toLowerCase().startsWith('en'))
  const pool = english.length > 0 ? english : voices
  if (pool.length === 0) return null
  const match = pool.find((v) => hints.some((h) => v.name.toLowerCase().includes(h)))
  return match ?? pool[Math.min(fallbackIndex, pool.length - 1)]
}

export interface UseSpeechResult {
  isSupported: boolean
  isPlaying: boolean
  isPaused: boolean
  currentIndex: number | null
  rate: number
  setRate: (rate: number) => void
  /** Speak a whole conversation in sequence. */
  play: (turns: ConversationTurn[]) => void
  /** Speak a single turn (e.g. the per-turn play button). */
  playTurn: (turn: ConversationTurn, index: number) => void
  pause: () => void
  resume: () => void
  stop: () => void
}

export function useSpeech(): UseSpeechResult {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [currentIndex, setCurrentIndex] = useState<number | null>(null)
  const [rate, setRate] = useState(1)
  const voicesRef = useRef<SpeechSynthesisVoice[]>([])
  const rateRef = useRef(rate)
  rateRef.current = rate

  // Load voices. getVoices() is often empty until the async voiceschanged event.
  useEffect(() => {
    if (!isSupported) return
    const load = () => {
      voicesRef.current = window.speechSynthesis.getVoices()
    }
    load()
    window.speechSynthesis.addEventListener('voiceschanged', load)
    return () => window.speechSynthesis.removeEventListener('voiceschanged', load)
  }, [])

  // Always cancel any in-flight speech when the component using this unmounts,
  // so audio never leaks across page/route changes.
  useEffect(() => {
    return () => {
      if (isSupported) window.speechSynthesis.cancel()
    }
  }, [])

  const buildUtterance = useCallback((turn: ConversationTurn): SpeechSynthesisUtterance => {
    const u = new SpeechSynthesisUtterance(turn.text)
    const voices = voicesRef.current
    if (turn.speaker === 'agent') {
      u.voice = pickVoice(voices, FEMALE_HINTS, 0)
      u.pitch = 1.1
    } else {
      u.voice = pickVoice(voices, MALE_HINTS, 1)
      u.pitch = 0.9
    }
    u.rate = rateRef.current
    return u
  }, [])

  const stop = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    setIsPlaying(false)
    setIsPaused(false)
    setCurrentIndex(null)
  }, [])

  const play = useCallback((turns: ConversationTurn[]) => {
    if (!isSupported) return
    // Speak only non-empty turns, but keep each turn's ORIGINAL index so the UI
    // highlight stays aligned. onend must be attached to the last spoken turn —
    // attaching it to turns[length-1] left isPlaying stuck true forever whenever
    // the final turn had empty text (it was skipped, so its onend never fired).
    const speakable = turns
      .map((turn, idx) => ({ turn, idx }))
      .filter(({ turn }) => turn.text.trim())
    if (speakable.length === 0) return

    window.speechSynthesis.cancel()
    setIsPlaying(true)
    setIsPaused(false)

    speakable.forEach(({ turn, idx }, i) => {
      const u = buildUtterance(turn)
      u.onstart = () => setCurrentIndex(idx)
      if (i === speakable.length - 1) {
        u.onend = () => {
          setIsPlaying(false)
          setIsPaused(false)
          setCurrentIndex(null)
        }
      }
      window.speechSynthesis.speak(u)
    })
  }, [buildUtterance])

  const playTurn = useCallback((turn: ConversationTurn, index: number) => {
    if (!isSupported || !turn.text.trim()) return
    window.speechSynthesis.cancel()
    setIsPlaying(true)
    setIsPaused(false)
    setCurrentIndex(index)
    const u = buildUtterance(turn)
    u.onend = () => {
      setIsPlaying(false)
      setIsPaused(false)
      setCurrentIndex(null)
    }
    window.speechSynthesis.speak(u)
  }, [buildUtterance])

  const pause = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.pause()
    setIsPaused(true)
  }, [])

  const resume = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.resume()
    setIsPaused(false)
  }, [])

  return { isSupported, isPlaying, isPaused, currentIndex, rate, setRate, play, playTurn, pause, resume, stop }
}
