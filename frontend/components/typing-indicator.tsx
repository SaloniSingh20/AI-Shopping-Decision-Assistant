'use client'

export function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-4 animate-slide-in-from-bottom">
      {/* Avatar */}
      <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 bg-muted text-muted-foreground text-sm font-semibold">
        AI
      </div>

      {/* Typing Bubble */}
      <div className="bg-card text-card-foreground border border-border rounded-lg rounded-bl-none px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Thinking...</span>
          <div className="flex gap-1">
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  )
}
