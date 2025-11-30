import { fetchAuthSession } from 'aws-amplify/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Check if Cognito is configured
const isCognitoConfigured = (): boolean => {
  const userPoolId = import.meta.env.VITE_USER_POOL_ID || ''
  const userPoolClientId = import.meta.env.VITE_USER_POOL_CLIENT_ID || ''
  return !!(userPoolId && userPoolClientId)
}

export class ApiClient {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    // If Cognito is not configured, use DEV_MODE header
    if (!isCognitoConfigured()) {
      headers['X-MTP-Dev-User'] = 'dev-user'
      return headers
    }

    // Otherwise, try to get Cognito token
    try {
      const session = await fetchAuthSession()
      const token = session.tokens?.idToken?.toString()
      
      if (!token) {
        throw new Error('No authentication token available')
      }
      
      headers['Authorization'] = `Bearer ${token}`
      return headers
    } catch (error) {
      // If auth fails and we're in development, fall back to dev mode
      if (import.meta.env.DEV) {
        console.warn('Cognito auth failed, falling back to DEV_MODE')
        headers['X-MTP-Dev-User'] = 'dev-user'
        return headers
      }
      throw new Error('Authentication required')
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}/v1${endpoint}`
    const headers = await this.getAuthHeaders()
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    })

    if (response.status === 401) {
      // Redirect to login on auth failure
      window.location.href = '/login'
      throw new Error('Authentication required')
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`)
    }

    return await response.json()
  }

  // Notes API
  async createNote(data: {
    date: string
    text?: string
    direction?: string
    session?: string
    risk?: number | string
    win_amount?: number | string
    tags?: string[]
    strategyId?: string
    hit_miss?: string
  }) {
    return this.request('/notes', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getNotes(limit = 20, lastKey?: string) {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (lastKey) params.append('lastKey', lastKey)
    
    return this.request(`/notes?${params}`)
  }

  async getNote(noteId: string) {
    return this.request(`/notes/${noteId}`)
  }

  async updateNote(noteId: string, data: Partial<{
    date: string
    text: string
    direction: string
    session: string
    risk: number | string
    win_amount: number | string
    tags: string[]
    strategyId: string
    hit_miss: string
  }>) {
    return this.request(`/notes/${noteId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteNote(noteId: string) {
    return this.request(`/notes/${noteId}`, {
      method: 'DELETE',
    })
  }

  // Strategies API
  async createStrategy(data: {
    name: string
    market: string
    timeframe: string
    dsl?: Record<string, any>
  }) {
    return this.request('/strategies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getStrategies(limit = 20, lastKey?: string) {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (lastKey) params.append('lastKey', lastKey)
    
    return this.request(`/strategies?${params}`)
  }

  async getStrategy(strategyId: string) {
    return this.request(`/strategies/${strategyId}`)
  }

  async updateStrategy(strategyId: string, data: Partial<{
    name: string
    market: string
    timeframe: string
    dsl: Record<string, any>
  }>) {
    return this.request(`/strategies/${strategyId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteStrategy(strategyId: string) {
    return this.request(`/strategies/${strategyId}`, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient()
