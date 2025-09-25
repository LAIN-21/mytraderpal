'use client'

import { AuthGuard } from '@/lib/auth-guard'
import { signOut } from 'aws-amplify/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  const router = useRouter()

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/login')
    } catch (error) {
      console.error('Sign out failed:', error)
    }
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold">MyTraderPal</h1>
            <Button onClick={handleSignOut} variant="outline">
              Sign Out
            </Button>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Welcome to MyTraderPal</h2>
              <p className="text-muted-foreground text-lg">
                Track your trades and develop winning strategies
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trading Journal</CardTitle>
                  <CardDescription>
                    Record your trades, analyze performance, and track your progress
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/notes">
                    <Button className="w-full">View Journal</Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Strategies</CardTitle>
                  <CardDescription>
                    Create and manage your trading strategies
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/strategies">
                    <Button className="w-full">View Strategies</Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
