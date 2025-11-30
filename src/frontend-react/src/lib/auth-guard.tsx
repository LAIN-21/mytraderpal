import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchAuthSession } from 'aws-amplify/auth'

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const checkAuth = async () => {
      // Check if Cognito is configured
      const userPoolId = import.meta.env.VITE_USER_POOL_ID || ''
      const userPoolClientId = import.meta.env.VITE_USER_POOL_CLIENT_ID || ''
      
      // If auth is not configured, allow access (for development)
      if (!userPoolId || !userPoolClientId) {
        console.warn('Auth not configured - allowing access for development')
        setIsAuthenticated(true)
        setIsLoading(false)
        return
      }
      
      // If Cognito is configured, require authentication
      try {
        const session = await fetchAuthSession()
        if (session.tokens?.idToken) {
          setIsAuthenticated(true)
        } else {
          navigate('/login')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        navigate('/login')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [navigate])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}

