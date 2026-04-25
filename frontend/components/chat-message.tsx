'use client'

import { cn } from '@/lib/utils'

export interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: React.ReactNode
  timestamp?: Date
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={cn(
        'flex gap-3 mb-4 animate-slide-in-from-bottom',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-muted-foreground'
        )}
      >
        {isUser ? 'You' : 'AI'}
      </div>

      {/* Message Bubble */}
      <div
        className={cn(
          'max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg',
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-none'
            : 'bg-card text-card-foreground border border-border rounded-bl-none'
        )}
      >
        <div className="text-sm leading-relaxed">{content}</div>
        {timestamp && (
          <div
            className={cn(
              'text-xs mt-1 opacity-70',
              isUser ? 'text-primary-foreground' : 'text-muted-foreground'
            )}
          >
            {timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        )}
      </div>
    </div>
  )
}
