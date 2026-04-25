'use client'

import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Send } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ChatInputProps {
  onSubmit: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSubmit, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      onSubmit(value)
      setValue('')
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <textarea
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ask me about products..."
        className={cn(
          'flex-1 min-h-[44px] max-h-[120px] px-4 py-2 rounded-lg border border-border bg-input text-foreground placeholder-muted-foreground resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200',
          'font-sans text-sm'
        )}
      />
      <Button
        type="submit"
        disabled={disabled || !value.trim()}
        className="h-[44px] w-[44px] p-0 flex items-center justify-center flex-shrink-0"
      >
        <Send className="h-4 w-4" />
      </Button>
    </form>
  )
}
