'use client'

import { Navbar } from '@/components/navbar'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Trash2, MessageSquare } from 'lucide-react'
import { Empty } from '@/components/ui/empty'

const mockHistory = [
  {
    id: '1',
    title: 'Looking for headphones under 5000',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    messageCount: 3,
  },
  {
    id: '2',
    title: 'Best smartwatch for fitness tracking',
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
    messageCount: 5,
  },
  {
    id: '3',
    title: 'Portable storage solutions',
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    messageCount: 2,
  },
  {
    id: '4',
    title: 'USB adapters and hubs',
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    messageCount: 4,
  },
  {
    id: '5',
    title: 'Wireless charging products',
    timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    messageCount: 1,
  },
]

export default function HistoryPage() {
  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    if (diff < 60 * 60 * 1000) {
      const minutes = Math.floor(diff / (60 * 1000))
      return `${minutes}m ago`
    } else if (diff < 24 * 60 * 60 * 1000) {
      const hours = Math.floor(diff / (60 * 60 * 1000))
      return `${hours}h ago`
    } else {
      const days = Math.floor(diff / (24 * 60 * 60 * 1000))
      return `${days}d ago`
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1 max-w-4xl mx-auto w-full">
        {/* Header */}
        <section className="border-b border-border bg-card">
          <div className="px-4 md:px-6 py-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">Chat History</h1>
            <p className="text-muted-foreground">
              Review your previous conversations and chat topics
            </p>
          </div>
        </section>

        {/* History List */}
        <section className="py-8 px-4 md:px-6">
          {mockHistory.length === 0 ? (
            <Empty
              icon="MessageSquare"
              title="No chat history yet"
              description="Your previous conversations will appear here"
            />
          ) : (
            <div className="space-y-2">
              {mockHistory.map((item, index) => (
                <Card
                  key={item.id}
                  className="p-4 hover:border-primary cursor-pointer transition-all group animate-scale-in"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <MessageSquare className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                          {item.title}
                        </h3>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{formatTime(item.timestamp)}</span>
                        <span>{item.messageCount} messages</span>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card py-6">
        <div className="max-w-4xl mx-auto px-4 md:px-6 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 Shop AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
