import { ResourcesConfig } from 'aws-amplify'

const userPoolId = import.meta.env.VITE_USER_POOL_ID || ''
const userPoolClientId = import.meta.env.VITE_USER_POOL_CLIENT_ID || ''

// Only configure Amplify if credentials are provided
// This allows the app to run without auth for development/testing
const config: ResourcesConfig = userPoolId && userPoolClientId ? {
  Auth: {
    Cognito: {
      userPoolId,
      userPoolClientId,
      loginWith: {
        email: true,
        username: true,
      },
    },
  },
} : {}

// Warn in development if auth is not configured
if (import.meta.env.DEV && (!userPoolId || !userPoolClientId)) {
  console.warn('⚠️  Cognito UserPool not configured. Authentication features will not work.')
  console.warn('   Create a .env file with VITE_USER_POOL_ID and VITE_USER_POOL_CLIENT_ID')
  console.warn('   Or set DEV_MODE=true in backend to bypass authentication')
}

export { config }
