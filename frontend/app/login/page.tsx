'use client'

import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { FieldGroup, FieldLabel } from '@/components/ui/field'
import { ShoppingBag } from 'lucide-react'

export default function LoginPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <Card className="w-full max-w-md p-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="h-12 w-12 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
              <ShoppingBag className="h-7 w-7" />
            </div>
          </div>

          <h1 className="text-3xl font-bold text-foreground text-center mb-2">
            Welcome Back
          </h1>
          <p className="text-center text-muted-foreground mb-6">
            Sign in to your Shop AI account
          </p>

          {/* Form */}
          <form className="space-y-4">
            <FieldGroup>
              <FieldLabel htmlFor="email">Email Address</FieldLabel>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </FieldGroup>

            <FieldGroup>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                required
              />
            </FieldGroup>

            <Button type="submit" className="w-full">
              Sign In
            </Button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground">or continue with</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Social Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline">Google</Button>
            <Button variant="outline">GitHub</Button>
          </div>

          {/* Sign Up Link */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="font-semibold text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </Card>
      </main>
    </div>
  )
}
