'use client'

import { useState, useRef, useEffect } from 'react'
import { Navbar } from '@/components/navbar'
import { Sidebar, ChatSession } from '@/components/sidebar'
import { ChatMessage } from '@/components/chat-message'
import { ChatInput } from '@/components/chat-input'
import { TypingIndicator } from '@/components/typing-indicator'
import { ProductCard, Product } from '@/components/product-card'
import { cn } from '@/lib/utils'

const CHAT_API_URL = 'http://127.0.0.1:8000/chat'

interface APIHistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

interface APIProduct {
  name?: string
  price?: string | number
  platform?: string
  link?: string
  image?: string
  reason?: string
  score?: number
  tags?: string[]
}

interface APIChatResponse {
  reply?: string
  products?: APIProduct[]
  follow_up_questions?: string[]
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: React.ReactNode
  textContent?: string
  timestamp: Date
}

interface ChatState {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
}

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentChat, setCurrentChat] = useState<ChatState>({
    id: 'default',
    title: 'New Chat',
    messages: [],
    createdAt: new Date(),
  })
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentChat.messages, isLoading])

  const handleNewChat = () => {
    // Save current chat if it has messages
    if (currentChat.messages.length > 0) {
      setSessions((prev) => [
        ...prev,
        {
          id: currentChat.id,
          title: currentChat.title,
          createdAt: currentChat.createdAt,
        },
      ])
    }

    // Create new chat
    const newChat: ChatState = {
      id: `chat-${Date.now()}`,
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
    }
    setCurrentChat(newChat)
  }

  const handleSelectSession = (id: string) => {
    // This would normally load the chat from storage
    // For now, just show a notification
  }

  const handleDeleteSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id))
  }

  const handleSendMessage = async (message: string) => {
    // Add user message
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    }

    setCurrentChat((prev) => ({
      ...prev,
      title:
        prev.messages.length === 0
          ? message.slice(0, 30) + (message.length > 30 ? '...' : '')
          : prev.title,
      messages: [...prev.messages, userMessage],
    }))

    setIsLoading(true)

    try {
      const history: APIHistoryMessage[] = currentChat.messages
        .map((msg) => {
          const messageText =
            typeof msg.content === 'string' ? msg.content : (msg.textContent ?? '')
          return {
            role: msg.role,
            content: messageText,
          }
        })
        .filter((msg) => msg.content.trim().length > 0)

      const response = await fetch(CHAT_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history,
        }),
      })

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data: APIChatResponse = await response.json()
      const products: Product[] = (data.products ?? []).map((product, index) => ({
        id: `${Date.now()}-${index}`,
        name: product.name ?? 'Product',
        price: product.price ?? '',
        image: product.image ?? '',
        platform: product.platform ?? '',
        link: product.link ?? '',
        reason: product.reason ?? '',
        score: product.score,
        tags: product.tags ?? [],
      }))

      const followUps = (data.follow_up_questions ?? []).filter(
        (question) => question.trim().length > 0
      )

      const assistantContent = (
        <div className="space-y-3">
          <p>{data.reply ?? 'Here are some options for you.'}</p>

          {products.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} compact />
              ))}
            </div>
          )}

          {followUps.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-1">
              {followUps.map((question, index) => (
                <button
                  key={`${question}-${index}`}
                  onClick={() => handleSendMessage(question)}
                  className="text-xs px-3 py-1.5 rounded-full border border-primary/40 text-primary hover:bg-primary hover:text-primary-foreground transition-colors font-medium"
                >
                  {question}
                </button>
              ))}
            </div>
          )}
        </div>
      )

      const assistantText = [data.reply ?? '', ...followUps].join('\n').trim()

      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: assistantContent,
        textContent: assistantText,
        timestamp: new Date(),
      }

      setCurrentChat((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }))
    } catch {
      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Something went wrong',
        textContent: 'Something went wrong',
        timestamp: new Date(),
      }

      setCurrentChat((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <Navbar />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - hidden on mobile */}
        <div className="hidden lg:block">
          <Sidebar
            sessions={sessions}
            currentSessionId={currentChat.id}
            onNewChat={handleNewChat}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
          />
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 space-y-2">
            {currentChat.messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="max-w-md">
                  <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
                    Welcome to Shop AI
                  </h1>
                  <p className="text-muted-foreground mb-8">
                    Chat with our AI assistant to discover amazing products tailored to your needs.
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                    <div className="p-3 rounded-lg bg-card border border-border animate-scale-in hover-glow cursor-pointer transition-colors hover:bg-primary/10">
                      Ask about products
                    </div>
                    <div className="p-3 rounded-lg bg-card border border-border animate-scale-in hover-glow cursor-pointer transition-colors hover:bg-primary/10" style={{ animationDelay: '50ms' }}>
                      Get recommendations
                    </div>
                    <div className="p-3 rounded-lg bg-card border border-border animate-scale-in hover-glow cursor-pointer transition-colors hover:bg-primary/10" style={{ animationDelay: '100ms' }}>
                      Find tech gadgets
                    </div>
                    <div className="p-3 rounded-lg bg-card border border-border animate-scale-in hover-glow cursor-pointer transition-colors hover:bg-primary/10" style={{ animationDelay: '150ms' }}>
                      Check reviews
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {currentChat.messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                    timestamp={msg.timestamp}
                  />
                ))}
                {isLoading && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className={cn(
            'border-t border-border bg-background p-4 md:p-6',
            'flex justify-center'
          )}>
            <div className="w-full max-w-2xl">
              <ChatInput onSubmit={handleSendMessage} disabled={isLoading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
