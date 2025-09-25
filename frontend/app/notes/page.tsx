'use client'

import { useState, useEffect } from 'react'
import { AuthGuard } from '@/lib/auth-guard'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { ArrowLeft, Plus, Edit, Trash2 } from 'lucide-react'

const noteSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  text: z.string().min(1, 'Text is required'),
  direction: z.string().optional(),
  session: z.string().optional(),
  risk: z.number().optional(),
  win_amount: z.number().optional(),
  tags: z.array(z.string()).optional(),
  strategyId: z.string().optional(),
})

type NoteFormData = z.infer<typeof noteSchema>

interface Note {
  noteId: string
  userId: string
  date: string
  text: string
  direction?: string
  session?: string
  risk?: number
  win_amount?: number
  tags?: string[]
  strategyId?: string
  createdAt: string
  updatedAt: string
}

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingNote, setEditingNote] = useState<Note | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<NoteFormData>({
    resolver: zodResolver(noteSchema),
  })

  useEffect(() => {
    loadNotes()
  }, [])

  const loadNotes = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getNotes()
      console.log('Notes response:', response)
      setNotes(response.notes || [])
    } catch (error) {
      console.error('Failed to load notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: NoteFormData) => {
    try {
      console.log('Saving note with data:', data)
      if (editingNote) {
        console.log('Updating existing note:', editingNote.noteId)
        await apiClient.updateNote(editingNote.noteId, data)
        console.log('Note updated successfully')
      } else {
        console.log('Creating new note')
        const result = await apiClient.createNote(data)
        console.log('Note created successfully:', result)
      }
      
      reset()
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
      text: note.text,
      direction: note.direction || '',
      session: note.session || '',
      risk: note.risk,
      win_amount: note.win_amount,
      tags: note.tags || [],
      strategyId: note.strategyId || '',
    })
    setShowForm(true)
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
    setShowForm(false)
    setEditingNote(null)
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4 flex items-center gap-4">
            <Link href="/">
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
                      <Input
                        id="direction"
                        placeholder="e.g., Long, Short"
                        {...register('direction')}
                      />
                    </div>
                    <div>
                      <Label htmlFor="session">Session</Label>
                      <Input
                        id="session"
                        placeholder="e.g., London, New York"
                        {...register('session')}
                      />
                    </div>
                    <div>
                      <Label htmlFor="risk">Risk Amount</Label>
                      <Input
                        id="risk"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        {...register('risk', { valueAsNumber: true })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="win_amount">Win Amount</Label>
                      <Input
                        id="win_amount"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        {...register('win_amount', { valueAsNumber: true })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="strategyId">Strategy ID</Label>
                      <Input
                        id="strategyId"
                        placeholder="Optional strategy reference"
                        {...register('strategyId')}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="text">Note Text *</Label>
                    <Textarea
                      id="text"
                      placeholder="Describe your trade, market observations, or lessons learned..."
                      rows={4}
                      {...register('text')}
                      className={errors.text ? 'border-destructive' : ''}
                    />
                    {errors.text && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.text.message}
                      </p>
                    )}
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

          <div className="space-y-4">
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
              notes.map((note) => (
                <Card key={note.noteId}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{note.date}</CardTitle>
                        {note.direction && (
                          <CardDescription>
                            Direction: {note.direction}
                            {note.session && ` • Session: ${note.session}`}
                          </CardDescription>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(note)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(note.noteId)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{note.text}</p>
                    {(note.risk || note.win_amount) && (
                      <div className="mt-4 flex gap-4 text-sm text-muted-foreground">
                        {note.risk && <span>Risk: ${note.risk}</span>}
                        {note.win_amount && <span>Win: ${note.win_amount}</span>}
                      </div>
                    )}
                    {note.tags && note.tags.length > 0 && (
                      <div className="mt-2 flex gap-1 flex-wrap">
                        {note.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-secondary text-secondary-foreground rounded text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
