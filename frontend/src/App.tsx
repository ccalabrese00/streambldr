import { Routes, Route } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import EditorPage from './pages/EditorPage'
import { useEffect } from 'react'

function App() {
  const { token, initializeAuth } = useAuthStore()

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={token ? <DashboardPage /> : <LoginPage />} />
        <Route path="/dashboard" element={token ? <DashboardPage /> : <LoginPage />} />
        <Route path="/projects/:projectId" element={token ? <ProjectDetailPage /> : <LoginPage />} />
        <Route path="/projects/:projectId/scenes/:sceneId" element={token ? <EditorPage /> : <LoginPage />} />
      </Routes>
    </div>
  )
}

export default App
