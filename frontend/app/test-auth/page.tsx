'use client'

import { useEffect } from 'react'

export default function TestAuthPage() {
  useEffect(() => {
    console.log('Test page loaded')
    
    // Test basic Amplify import
    try {
      console.log('Testing Amplify import...')
      import('aws-amplify').then(({ Amplify }) => {
        console.log('Amplify imported successfully')
        
        // Test auth import
        import('aws-amplify/auth').then(({ fetchAuthSession }) => {
          console.log('Auth imported successfully')
          
          // Test the actual function
          fetchAuthSession().then((session) => {
            console.log('Auth session test successful:', session)
          }).catch((error) => {
            console.log('Auth session test failed:', error)
          })
        }).catch((error) => {
          console.log('Auth import failed:', error)
        })
      }).catch((error) => {
        console.log('Amplify import failed:', error)
      })
    } catch (error) {
      console.log('Import test failed:', error)
    }
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Auth Test Page</h1>
      <p>Check the browser console and terminal for debug logs.</p>
    </div>
  )
}
