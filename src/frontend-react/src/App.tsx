import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthGuard } from './lib/auth-guard.tsx'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NotesPage from './pages/NotesPage'
import StrategiesPage from './pages/StrategiesPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <AuthGuard>
            <HomePage />
          </AuthGuard>
        }
      />
      <Route
        path="/notes"
        element={
          <AuthGuard>
            <NotesPage />
          </AuthGuard>
        }
      />
      <Route
        path="/strategies"
        element={
          <AuthGuard>
            <StrategiesPage />
          </AuthGuard>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App


