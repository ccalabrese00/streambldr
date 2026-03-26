import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Plus, Edit2, Trash2, Copy, Image as ImageIcon } from 'lucide-react'
import { api } from '../utils/api'

interface Scene {
  id: string
  name: string
  scene_type: string
  canvas_width: number
  canvas_height: number
  thumbnail_url: string | null
  updated_at: string
}

interface Project {
  id: string
  name: string
  description: string | null
  scene_count: number
  thumbnail_url: string | null
  created_at: string
  updated_at: string
  scenes: Scene[]
}

const SCENE_TYPE_LABELS: Record<string, string> = {
  starting_soon: 'Starting Soon',
  live: 'Live',
  brb: 'Be Right Back',
  ending: 'Ending',
  custom: 'Custom',
}

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newSceneName, setNewSceneName] = useState('')
  const [newSceneType, setNewSceneType] = useState('live')

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await api.get(`/projects/${projectId}`)
      return response.data as Project
    },
  })

  const createSceneMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/projects/${projectId}/scenes`, {
        name: newSceneName,
        scene_type: newSceneType,
        canvas_width: 1920,
        canvas_height: 1080,
        background_color: '#1a1a1a',
      })
      return response.data
    },
    onSuccess: (data) => {
      setShowCreateModal(false)
      setNewSceneName('')
      setNewSceneType('live')
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      navigate(`/projects/${projectId}/scenes/${data.id}`)
    },
  })

  const duplicateSceneMutation = useMutation({
    mutationFn: async (sceneId: string) => {
      const response = await api.post(`/scenes/${sceneId}/duplicate`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const deleteSceneMutation = useMutation({
    mutationFn: async (sceneId: string) => {
      await api.delete(`/scenes/${sceneId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Project not found</h2>
          <Link to="/dashboard" className="text-indigo-600 hover:text-indigo-500 mt-2 inline-block">
            Back to dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="p-2 hover:bg-gray-100 rounded-lg">
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{project.name}</h1>
                {project.description && (
                  <p className="text-sm text-gray-500">{project.description}</p>
                )}
              </div>
            </div>

            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Scene
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">
            Scenes ({project.scenes?.length || 0})
          </h2>
        </div>

        {project.scenes?.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl shadow-sm">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ImageIcon className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-1">No scenes yet</h3>
            <p className="text-sm text-gray-500 mb-4">Create your first scene to start designing</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Scene
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {project.scenes?.map((scene) => (
              <div
                key={scene.id}
                className="group bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
              >
                <Link to={`/projects/${projectId}/scenes/${scene.id}`}>
                  <div className="aspect-video bg-gray-100 relative">
                    {scene.thumbnail_url ? (
                      <img
                        src={scene.thumbnail_url}
                        alt={scene.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <ImageIcon className="w-12 h-12 text-gray-300" />
                      </div>
                    )}
                    <div className="absolute top-2 left-2 px-2 py-1 bg-black/50 text-white text-xs rounded">
                      {SCENE_TYPE_LABELS[scene.scene_type] || scene.scene_type}
                    </div>
                  </div>
                </Link>
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 truncate">{scene.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {scene.canvas_width}×{scene.canvas_height} • {new Date(scene.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => navigate(`/projects/${projectId}/scenes/${scene.id}`)}
                        className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => duplicateSceneMutation.mutate(scene.id)}
                        className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                        title="Duplicate"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Delete this scene?')) {
                            deleteSceneMutation.mutate(scene.id)
                          }
                        }}
                        className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Scene Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Create New Scene</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Scene Name
                </label>
                <input
                  type="text"
                  value={newSceneName}
                  onChange={(e) => setNewSceneName(e.target.value)}
                  placeholder="e.g., Main Gaming Scene"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Scene Type
                </label>
                <select
                  value={newSceneType}
                  onChange={(e) => setNewSceneType(e.target.value)}
                  className="input-field"
                >
                  <option value="live">Live Stream</option>
                  <option value="starting_soon">Starting Soon</option>
                  <option value="brb">Be Right Back</option>
                  <option value="ending">Stream Ending</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={() => createSceneMutation.mutate()}
                disabled={!newSceneName || createSceneMutation.isPending}
                className="btn-primary flex-1"
              >
                {createSceneMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
