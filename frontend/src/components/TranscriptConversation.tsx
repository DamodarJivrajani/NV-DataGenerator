import { Volume2 } from 'lucide-react'
import { clsx } from 'clsx'
import type { ConversationTurn } from '@/types'

interface Props {
  conversation: ConversationTurn[]
  /** Index of the turn currently being spoken, for highlighting. */
  activeIndex?: number | null
  /** When provided, renders a per-turn play button. */
  onPlayTurn?: (turn: ConversationTurn, index: number) => void
}

/**
 * Presentational chat-bubble rendering of a conversation, shared by the
 * Transcript Viewer page. Highlights the active (spoken) turn and optionally
 * exposes a per-turn play button.
 */
export function TranscriptConversation({ conversation, activeIndex = null, onPlayTurn }: Props) {
  return (
    <div className="space-y-3">
      {conversation.map((turn, idx) => {
        const isCustomer = turn.speaker === 'customer'
        const isActive = activeIndex === idx
        return (
          <div
            key={idx}
            className={clsx('flex gap-2 items-end', isCustomer ? 'justify-start' : 'justify-end')}
          >
            {onPlayTurn && !isCustomer && (
              <PlayTurnButton onClick={() => onPlayTurn(turn, idx)} />
            )}
            <div
              className={clsx(
                'max-w-[80%] px-4 py-2 rounded-lg text-sm transition-shadow',
                isCustomer ? 'bg-blue-500/20 text-blue-100' : 'bg-nvidia-green/20 text-green-100',
                isActive && 'ring-2 ring-nvidia-green shadow-lg shadow-nvidia-green/20',
              )}
            >
              <span className="text-xs font-medium opacity-70 block mb-1">
                {isCustomer ? 'Customer' : 'Agent'}
              </span>
              {turn.text}
            </div>
            {onPlayTurn && isCustomer && (
              <PlayTurnButton onClick={() => onPlayTurn(turn, idx)} />
            )}
          </div>
        )
      })}
    </div>
  )
}

function PlayTurnButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      title="Listen to this turn"
      className="shrink-0 p-1.5 text-gray-500 hover:text-nvidia-green hover:bg-gray-800 rounded-full transition-colors"
    >
      <Volume2 className="w-4 h-4" />
    </button>
  )
}
