'use client'

import { useState } from 'react'
import { Navbar } from '@/components/navbar'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Bell, Lock, MessageSquare, Zap } from 'lucide-react'

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true)
  const [productAlerts, setProductAlerts] = useState(true)
  const [dataCollection, setDataCollection] = useState(false)
  const [autoSave, setAutoSave] = useState(true)

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1 max-w-2xl mx-auto w-full">
        {/* Header */}
        <section className="border-b border-border bg-card">
          <div className="px-4 md:px-6 py-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">Settings</h1>
            <p className="text-muted-foreground">
              Manage your preferences and account settings
            </p>
          </div>
        </section>

        {/* Settings */}
        <section className="py-8 px-4 md:px-6 space-y-6">
          {/* Notifications */}
          <Card className="p-6 animate-scale-in">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <Bell className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground">
                    Push Notifications
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Receive notifications about new products and recommendations
                  </p>
                </div>
              </div>
              <Switch
                checked={notifications}
                onCheckedChange={setNotifications}
              />
            </div>
          </Card>

          {/* Product Alerts */}
          <Card className="p-6 animate-scale-in" style={{ animationDelay: '50ms' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground">
                    Product Alerts
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Get notified when products you&apos;re interested in go on sale
                  </p>
                </div>
              </div>
              <Switch
                checked={productAlerts}
                onCheckedChange={setProductAlerts}
              />
            </div>
          </Card>

          {/* Auto-Save Chats */}
          <Card className="p-6 animate-scale-in" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <MessageSquare className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground">
                    Auto-Save Chats
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Automatically save your conversations for future reference
                  </p>
                </div>
              </div>
              <Switch
                checked={autoSave}
                onCheckedChange={setAutoSave}
              />
            </div>
          </Card>

          {/* Data Collection */}
          <Card className="p-6 animate-scale-in" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <Lock className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground">
                    Data Collection
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Allow us to use your data to improve recommendations
                  </p>
                </div>
              </div>
              <Switch
                checked={dataCollection}
                onCheckedChange={setDataCollection}
              />
            </div>
          </Card>

          {/* Privacy & Security */}
          <Card className="p-6 border-destructive/30 bg-destructive/5 animate-scale-in" style={{ animationDelay: '200ms' }}>
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Privacy & Security</h3>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  Change Password
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  Download Your Data
                </Button>
                <Button variant="outline" className="w-full justify-start text-destructive">
                  Delete Account
                </Button>
              </div>
            </div>
          </Card>

          {/* Save Button */}
          <div className="flex gap-2 justify-end">
            <Button variant="outline">Cancel</Button>
            <Button>Save Changes</Button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card py-6 mt-8">
        <div className="max-w-2xl mx-auto px-4 md:px-6 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 Shop AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
