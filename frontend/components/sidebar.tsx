'use client'

import { useState } from 'react'
import { Plus, Trash2, ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export interface ChatSession {
  id: string
  title: string
  createdAt: Date
}

export interface SidebarProps {
  sessions: ChatSession[]
  currentSessionId?: string
  onNewChat?: () => void
  onSelectSession?: (id: string) => void
  onDeleteSession?: (id: string) => void
}

export function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
}: SidebarProps) {
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['today'])

  const groupSessionsByDate = (sessions: ChatSession[]) => {
    const groups: Record<string, ChatSession[]> = {
      today: [],
      yesterday: [],
      week: [],
      older: [],
    }

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const weekAgo = new Date(today)
    weekAgo.setDate(weekAgo.getDate() - 7)

    sessions.forEach((session) => {
      const sessionDate = new Date(
        session.createdAt.getFullYear(),
        session.createdAt.getMonth(),
        session.createdAt.getDate()
      )

      if (sessionDate.getTime() === today.getTime()) {
        groups.today.push(session)
      } else if (sessionDate.getTime() === yesterday.getTime()) {
        groups.yesterday.push(session)
      } else if (sessionDate.getTime() > weekAgo.getTime()) {
        groups.week.push(session)
      } else {
        groups.older.push(session)
      }
    })

    return groups
  }

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) =>
      prev.includes(group)
        ? prev.filter((g) => g !== group)
        : [...prev, group]
    )
  }

  const groupedSessions = groupSessionsByDate(sessions)

  return (
    <aside className="w-64 h-screen bg-sidebar border-r border-sidebar-border flex flex-col overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <Button
          onClick={onNewChat}
          className="w-full justify-center gap-2"
          variant="default"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto">
        {Object.entries(groupedSessions).map(([group, groupSessions]) => (
          groupSessions.length > 0 && (
            <div key={group} className="mb-2">
              <button
                onClick={() => toggleGroup(group)}
                className="w-full px-4 py-2 flex items-center justify-between text-xs font-semibold text-sidebar-muted-foreground hover:bg-sidebar-accent transition-colors"
              >
                <span className="capitalize">
                  {group === 'today'
                    ? 'Today'
                    : group === 'yesterday'
                      ? 'Yesterday'
                      : group === 'week'
                        ? 'This Week'
                        : 'Older'}
                </span>
                <ChevronDown
                  className={cn(
                    'h-3 w-3 transition-transform',
                    expandedGroups.includes(group) ? '' : '-rotate-90'
                  )}
                />
              </button>

              {expandedGroups.includes(group) && (
                <div className="px-2 py-1 space-y-1">
                  {groupSessions.map((session) => (
                    <div
                      key={session.id}
                      className="group flex items-center gap-2 p-2 rounded-lg hover:bg-sidebar-accent transition-colors cursor-pointer"
                      onClick={() => onSelectSession?.(session.id)}
                    >
                      <button
                        className={cn(
                          'flex-1 text-left px-2 py-1 text-sm rounded transition-colors',
                          currentSessionId === session.id
                            ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                            : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                        )}
                      >
                        <span className="truncate block">{session.title}</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDeleteSession?.(session.id)
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 text-sidebar-muted-foreground hover:text-sidebar-foreground transition-all"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        ))}
      </div>
    </aside>
  )
}
