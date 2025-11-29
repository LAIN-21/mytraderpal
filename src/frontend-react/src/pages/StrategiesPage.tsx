import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Plus, Edit, Trash2 } from 'lucide-react'

const strategySchema = z.object({
  name: z.string().min(1, 'Name is required'),
  market: z.string().min(1, 'Market is required'),
  timeframe: z.string().min(1, 'Timeframe is required'),
  dsl: z.record(z.any()).optional(),
})

type StrategyFormData = z.infer<typeof strategySchema>

interface Strategy {
  strategyId: string
  userId: string
  name: string
  market: string
  timeframe: string
  dsl?: Record<string, any>
  createdAt: string
  updatedAt: string
}

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null)
  const [dslText, setDslText] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<StrategyFormData>({
    resolver: zodResolver(strategySchema),
  })

  useEffect(() => {
    loadStrategies()
  }, [])

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getStrategies() as { strategies?: Strategy[] }
      setStrategies(response.strategies || [])
    } catch (error) {
      console.error('Failed to load strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: StrategyFormData) => {
    try {
      const dsl = dslText ? { description: dslText } : {}
      const strategyData = { ...data, dsl }
      
      if (editingStrategy) {
        await apiClient.updateStrategy(editingStrategy.strategyId, strategyData)
      } else {
        await apiClient.createStrategy(strategyData)
      }
      
      reset()
      setDslText('')
      setShowForm(false)
      setEditingStrategy(null)
      loadStrategies()
    } catch (error) {
      console.error('Failed to save strategy:', error)
      alert('Failed to save strategy: ' + (error as Error).message)
    }
  }

  const handleEdit = (strategy: Strategy) => {
    setEditingStrategy(strategy)
    reset({
      name: strategy.name,
      market: strategy.market,
      timeframe: strategy.timeframe,
    })
    setDslText(strategy.dsl ? JSON.stringify(strategy.dsl, null, 2) : '')
    setShowForm(true)
  }

  const handleDelete = async (strategyId: string) => {
    if (!confirm('Are you sure you want to delete this strategy?')) return
    
    try {
      await apiClient.deleteStrategy(strategyId)
      loadStrategies()
    } catch (error) {
      console.error('Failed to delete strategy:', error)
    }
  }

  const handleCancel = () => {
    reset()
    setDslText('')
    setShowForm(false)
    setEditingStrategy(null)
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
          <h1 className="text-2xl font-bold">Trading Strategies</h1>
          <Button onClick={() => setShowForm(true)} className="ml-auto">
            <Plus className="h-4 w-4 mr-2" />
            Add Strategy
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {showForm && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>{editingStrategy ? 'Edit Strategy' : 'Add New Strategy'}</CardTitle>
              <CardDescription>
                Define your trading strategy parameters and rules
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="name">Strategy Name *</Label>
                    <Input
                      id="name"
                      placeholder="e.g., EMA Crossover"
                      {...register('name')}
                      className={errors.name ? 'border-destructive' : ''}
                    />
                    {errors.name && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.name.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="market">Market *</Label>
                    <Input
                      id="market"
                      placeholder="e.g., forex, stocks, crypto"
                      {...register('market')}
                      className={errors.market ? 'border-destructive' : ''}
                    />
                    {errors.market && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.market.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="timeframe">Timeframe *</Label>
                    <Input
                      id="timeframe"
                      placeholder="e.g., 1h, 4h, 1d"
                      {...register('timeframe')}
                      className={errors.timeframe ? 'border-destructive' : ''}
                    />
                    {errors.timeframe && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.timeframe.message}
                      </p>
                    )}
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="dsl">Strategy Description (Optional)</Label>
                  <Textarea
                    id="dsl"
                    placeholder="Describe your strategy rules, entry/exit conditions, risk management, etc."
                    rows={4}
                    value={dslText}
                    onChange={(e) => setDslText(e.target.value)}
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Optional: Describe your strategy rules and conditions.
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Saving...' : editingStrategy ? 'Update Strategy' : 'Save Strategy'}
                  </Button>
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <div className="space-y-2">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-2 text-muted-foreground">Loading strategies...</p>
            </div>
          ) : strategies.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-muted-foreground">No strategies yet. Create your first trading strategy!</p>
              </CardContent>
            </Card>
          ) : (
            strategies.map((strategy) => (
              <Card key={strategy.strategyId} className="mb-2">
                <CardContent className="pt-4">
                  <div className="flex justify-between items-center">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-semibold text-base">{strategy.name}</h3>
                        <div className="flex gap-2 text-xs">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {strategy.market}
                          </span>
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                            {strategy.timeframe}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(strategy)}
                        className="h-7 w-7 p-0"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(strategy.strategyId)}
                        className="h-7 w-7 p-0"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  )
}

