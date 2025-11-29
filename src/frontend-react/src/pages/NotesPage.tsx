import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Plus, Edit, Trash2 } from 'lucide-react'

const noteSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  text: z.string().optional(),
  direction: z.string().optional(),
  session: z.string().optional(),
  risk: z.string().optional(),
  win_amount: z.string().optional(),
  tags: z.array(z.string()).optional(),
  strategyId: z.string().optional(),
  hit_miss: z.string().optional(),
})

type NoteFormData = z.infer<typeof noteSchema>

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

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingNote, setEditingNote] = useState<Note | null>(null)
  const [direction, setDirection] = useState<string>('')
  const [session, setSession] = useState<string>('')
  const [strategyId, setStrategyId] = useState<string>('')
  const [hitMiss, setHitMiss] = useState<string>('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<NoteFormData>({
    resolver: zodResolver(noteSchema),
  })

  const strategyMap = useMemo(() => {
    const map = new Map<string, Strategy>()
    strategies.forEach(strategy => {
      map.set(strategy.strategyId, strategy)
    })
    return map
  }, [strategies])

  useEffect(() => {
    loadNotes()
    loadStrategies()
  }, [])

  const loadNotes = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getNotes() as { notes?: Note[] }
      setNotes(response.notes || [])
    } catch (error) {
      console.error('Failed to load notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStrategies = async () => {
    try {
      const response = await apiClient.getStrategies() as { strategies?: Strategy[] }
      setStrategies(response.strategies || [])
    } catch (error) {
      console.error('Failed to load strategies:', error)
    }
  }

  const onSubmit = async (data: NoteFormData) => {
    try {
      const noteData = {
        ...data,
        risk: data.risk && data.risk !== '' ? parseFloat(data.risk) : undefined,
        win_amount: data.win_amount && data.win_amount !== '' ? parseFloat(data.win_amount) : undefined,
      }
      
      if (direction && direction !== '') {
        noteData.direction = direction
      }
      if (session && session !== '') {
        noteData.session = session
      }
      if (strategyId && strategyId !== '') {
        noteData.strategyId = strategyId
      }
      if (hitMiss && hitMiss !== '') {
        noteData.hit_miss = hitMiss
      }
      
      if (editingNote) {
        await apiClient.updateNote(editingNote.noteId, noteData)
      } else {
        await apiClient.createNote(noteData)
      }
      
      reset()
      setDirection('')
      setSession('')
      setStrategyId('')
      setHitMiss('')
      setShowForm(false)
      setEditingNote(null)
      loadNotes()
    } catch (error) {
      console.error('Failed to save note:', error)
      alert('Failed to save note: ' + (error as Error).message)
    }
  }

  const handleEdit = (note: Note) => {
    setEditingNote(note)
    reset({
      date: note.date,
      text: note.text || '',
      risk: note.risk?.toString() || '',
      win_amount: note.win_amount?.toString() || '',
      tags: note.tags || [],
    })
    setDirection(note.direction || '')
    setSession(note.session || '')
    setStrategyId(note.strategyId || '')
    setHitMiss(note.hit_miss || '')
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDelete = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) return
    
    try {
      await apiClient.deleteNote(noteId)
      loadNotes()
    } catch (error) {
      console.error('Failed to delete note:', error)
    }
  }

  const handleCancel = () => {
    reset()
    setDirection('')
    setSession('')
    setStrategyId('')
    setHitMiss('')
    setShowForm(false)
    setEditingNote(null)
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
          <h1 className="text-2xl font-bold">Trading Journal</h1>
          <Button onClick={() => setShowForm(true)} className="ml-auto">
            <Plus className="h-4 w-4 mr-2" />
            Add Note
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {showForm && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>{editingNote ? 'Edit Note' : 'Add New Note'}</CardTitle>
              <CardDescription>
                Record your trading thoughts and observations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Date *</Label>
                    <Input
                      id="date"
                      type="date"
                      {...register('date')}
                      className={errors.date ? 'border-destructive' : ''}
                    />
                    {errors.date && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.date.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="direction">Direction</Label>
                    <Select value={direction} onValueChange={setDirection}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select direction" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Long">Long</SelectItem>
                        <SelectItem value="Short">Short</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="session">Session</Label>
                    <Select value={session} onValueChange={setSession}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select session" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Asia">Asia</SelectItem>
                        <SelectItem value="London">London</SelectItem>
                        <SelectItem value="New York">New York</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="hitMiss">Hit/Miss</Label>
                    <Select value={hitMiss} onValueChange={setHitMiss}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select result" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Hit">Hit</SelectItem>
                        <SelectItem value="Miss">Miss</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="risk">Risk Amount</Label>
                    <Input
                      id="risk"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      {...register('risk')}
                    />
                  </div>
                  <div>
                    <Label htmlFor="win_amount">Win Amount</Label>
                    <Input
                      id="win_amount"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      {...register('win_amount')}
                    />
                  </div>
                  <div>
                    <Label htmlFor="strategyId">Strategy</Label>
                    {strategies.length > 0 ? (
                      <Select value={strategyId} onValueChange={setStrategyId}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select strategy (optional)" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">No strategy</SelectItem>
                          {strategies.map((strategy) => (
                            <SelectItem key={strategy.strategyId} value={strategy.strategyId}>
                              {strategy.name} ({strategy.market} - {strategy.timeframe})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          No strategies found. Create your first strategy to start tracking your trading approach.
                        </p>
                        <Link to="/strategies">
                          <Button type="button" variant="outline" size="sm">
                            Create Strategy
                          </Button>
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="text">Note Text</Label>
                  <Textarea
                    id="text"
                    placeholder="Describe your trade, market observations, or lessons learned..."
                    rows={4}
                    {...register('text')}
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Saving...' : editingNote ? 'Update Note' : 'Save Note'}
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
              <p className="mt-2 text-muted-foreground">Loading notes...</p>
            </div>
          ) : notes.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-muted-foreground">No notes yet. Create your first trading note!</p>
              </CardContent>
            </Card>
          ) : (
            notes.map((note) => {
              const strategy = note.strategyId ? strategyMap.get(note.strategyId) : undefined
              const strategyName = strategy ? strategy.name : note.strategyId
              
              return (
                <Card key={note.noteId} className="mb-3">
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-base">{note.date}</h3>
                          <div className="flex gap-2 text-xs">
                            {note.direction && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                {note.direction}
                              </span>
                            )}
                            {note.session && (
                              <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                                {note.session}
                              </span>
                            )}
                            {note.hit_miss && (
                              <span className={`px-2 py-1 rounded ${
                                note.hit_miss === 'Hit' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {note.hit_miss}
                              </span>
                            )}
                            {note.strategyId && (
                              <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                                {strategyName}
                              </span>
                            )}
                          </div>
                        </div>
                        {note.text && (
                          <p className="text-sm text-gray-700 mb-2 whitespace-pre-wrap">
                            {note.text}
                          </p>
                        )}
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {(note.risk || note.win_amount) && (
                            <div className="flex gap-3">
                              {note.risk && <span>Risk: ${note.risk}</span>}
                              {note.win_amount && <span>Win: ${note.win_amount}</span>}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(note)}
                          className="h-7 w-7 p-0"
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(note.noteId)}
                          className="h-7 w-7 p-0"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })
          )}
        </div>
      </main>
    </div>
  )
}

