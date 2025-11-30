import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, TrendingUp, TrendingDown, DollarSign, FileText, Target } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Note {
  noteId: string
  userId: string
  date: string
  text?: string
  direction?: string
  session?: string
  risk?: number
  win_amount?: number
  tags?: string[]
  strategyId?: string
  hit_miss?: string
  createdAt: string
  updatedAt: string
}

interface Strategy {
  strategyId: string
  userId: string
  name: string
  market: string
  timeframe: string
  createdAt: string
  updatedAt: string
}

export default function SummaryPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [notesResponse, strategiesResponse] = await Promise.all([
        apiClient.getNotes(1000) as Promise<{ notes?: Note[] }>,
        apiClient.getStrategies(1000) as Promise<{ strategies?: Strategy[] }>,
      ])
      setNotes(notesResponse.notes || [])
      setStrategies(strategiesResponse.strategies || [])
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate PnL: sum of wins where hit + sum of losses where miss
  const calculatePnL = () => {
    let totalPnL = 0

    notes.forEach((note) => {
      if (note.hit_miss === 'Hit' && note.win_amount) {
        // Add win amount for hits
        totalPnL += note.win_amount
      } else if (note.hit_miss === 'Miss' && note.risk) {
        // Subtract risk amount for misses (losses)
        totalPnL -= note.risk
      }
    })

    return totalPnL
  }

  // Calculate average win
  const calculateAverageWin = () => {
    const hits = notes.filter(n => n.hit_miss === 'Hit' && n.win_amount)
    if (hits.length === 0) return 0
    const totalWins = hits.reduce((sum, n) => sum + (n.win_amount || 0), 0)
    return totalWins / hits.length
  }

  // Calculate average loss
  const calculateAverageLoss = () => {
    const misses = notes.filter(n => n.hit_miss === 'Miss' && n.risk)
    if (misses.length === 0) return 0
    const totalLosses = misses.reduce((sum, n) => sum + (n.risk || 0), 0)
    return totalLosses / misses.length
  }

  const totalTrades = notes.length
  const totalStrategies = strategies.length
  const pnl = calculatePnL()
  const isPositive = pnl >= 0
  const averageWin = calculateAverageWin()
  const averageLoss = calculateAverageLoss()
  const totalWins = notes.filter(n => n.hit_miss === 'Hit' && n.win_amount).reduce((sum, n) => sum + (n.win_amount || 0), 0)
  const totalLosses = notes.filter(n => n.hit_miss === 'Miss' && n.risk).reduce((sum, n) => sum + (n.risk || 0), 0)
  const winCount = notes.filter(n => n.hit_miss === 'Hit' && n.win_amount).length
  const lossCount = notes.filter(n => n.hit_miss === 'Miss' && n.risk).length

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Loading summary...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Summary</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            {/* Total Trades */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalTrades}</div>
                <p className="text-xs text-muted-foreground">
                  Trading notes recorded
                </p>
              </CardContent>
            </Card>

            {/* Total Strategies */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Strategies</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalStrategies}</div>
                <p className="text-xs text-muted-foreground">
                  Strategies created
                </p>
              </CardContent>
            </Card>

            {/* PnL */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Profit & Loss</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold flex items-center gap-2 ${
                  isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {isPositive ? (
                    <TrendingUp className="h-5 w-5" />
                  ) : (
                    <TrendingDown className="h-5 w-5" />
                  )}
                  ${pnl.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {isPositive ? 'Net profit' : 'Net loss'}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Average Win */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Win</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  ${averageWin.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {winCount > 0 ? `From ${winCount} winning trade${winCount !== 1 ? 's' : ''}` : 'No winning trades yet'}
                </p>
              </CardContent>
            </Card>

            {/* Average Loss */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Loss</CardTitle>
                <TrendingDown className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  ${averageLoss.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {lossCount > 0 ? `From ${lossCount} losing trade${lossCount !== 1 ? 's' : ''}` : 'No losing trades yet'}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* PnL Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>PnL Breakdown</CardTitle>
              <CardDescription>
                Calculation: Wins (Hits) - Losses (Misses)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Wins (Hits):</span>
                  <span className="text-sm font-semibold text-green-600">
                    ${totalWins.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Losses (Misses):</span>
                  <span className="text-sm font-semibold text-red-600">
                    -${totalLosses.toFixed(2)}
                  </span>
                </div>
                <div className="border-t pt-4 flex justify-between items-center">
                  <span className="text-base font-semibold">Net PnL:</span>
                  <span className={`text-lg font-bold ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${pnl.toFixed(2)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

