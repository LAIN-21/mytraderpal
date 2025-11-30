import { useNavigate } from 'react-router-dom'
import { signOut } from 'aws-amplify/auth'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Target, BarChart3 } from 'lucide-react'

export default function HomePage() {
  const navigate = useNavigate()

  const handleSignOut = async () => {
    try {
      await signOut()
      navigate('/login')
    } catch (error) {
      console.error('Sign out failed:', error)
    }
  }

  return (
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

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 px-6 pt-6">
                <div className="space-y-2 flex-1">
                  <CardTitle className="text-2xl">Trading Journal</CardTitle>
                  <CardDescription className="text-base leading-relaxed">
                    Record your trades, analyze performance, and track your progress
                  </CardDescription>
                </div>
                <FileText className="h-10 w-10 text-muted-foreground ml-4 flex-shrink-0" />
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0 mt-auto">
                <Link to="/notes">
                  <Button className="w-full" size="lg">View Journal</Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="h-full flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 px-6 pt-6">
                <div className="space-y-2 flex-1">
                  <CardTitle className="text-2xl">Strategies</CardTitle>
                  <CardDescription className="text-base leading-relaxed">
                    Create and manage your trading strategies
                  </CardDescription>
                </div>
                <Target className="h-10 w-10 text-muted-foreground ml-4 flex-shrink-0" />
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0 mt-auto">
                <Link to="/strategies">
                  <Button className="w-full" size="lg">View Strategies</Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="h-full flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 px-6 pt-6">
                <div className="space-y-2 flex-1">
                  <CardTitle className="text-2xl">Summary</CardTitle>
                  <CardDescription className="text-base leading-relaxed">
                    View your trading statistics and profit & loss
                  </CardDescription>
                </div>
                <BarChart3 className="h-10 w-10 text-muted-foreground ml-4 flex-shrink-0" />
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0 mt-auto">
                <Link to="/summary">
                  <Button className="w-full" size="lg">View Summary</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}


