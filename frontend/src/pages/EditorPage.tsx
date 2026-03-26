import { useState, useCallback, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  DndContext,
  useDraggable,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import { restrictToParentElement } from '@dnd-kit/modifiers'
import {
  ArrowLeft, Save, Download, Settings, Layers, Square, Type, Image, Monitor, MessageSquare, Bell,
  Trash2, Copy, Eye, EyeOff, Wand2, LayoutTemplate, ChevronUp, ChevronDown, Palette,
} from 'lucide-react'
import { api } from '../utils/api'

interface Element {
  id: string
  element_type: string
  name: string
  position_x: number
  position_y: number
  width: number
  height: number
  z_index: number
  properties: Record<string, any>
  is_visible: boolean
}

interface Theme {
  id: string
  name: string
  color_primary: string
  color_secondary: string
  color_background: string
  color_surface: string
  color_text: string
  color_text_muted: string
  font_heading: string
  font_body: string
}

interface Scene {
  id: string
  name: string
  background_color: string
  canvas_width: number
  canvas_height: number
  theme_id: string | null
  elements: Element[]
}

const ELEMENT_TYPES = [
  { type: 'webcam', label: 'Webcam', icon: Monitor },
  { type: 'chat', label: 'Chat', icon: MessageSquare },
  { type: 'alert', label: 'Alert', icon: Bell },
  { type: 'text', label: 'Text', icon: Type },
  { type: 'image', label: 'Image', icon: Image },
  { type: 'panel', label: 'Panel', icon: Square },
]

export default function EditorPage() {
  const { projectId, sceneId } = useParams<{ projectId: string; sceneId: string }>()
  const queryClient = useQueryClient()
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null)
  const [zoom, setZoom] = useState(0.5)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [showAIModal, setShowAIModal] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [showThemeModal, setShowThemeModal] = useState(false)

  const sensors = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 10 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 250, tolerance: 5 } })
  )

  const { data: scene, isLoading } = useQuery({
    queryKey: ['scene', sceneId],
    queryFn: async () => {
      const response = await api.get(`/scenes/${sceneId}`)
      return response.data as Scene
    },
  })

  const saveMutation = useMutation({
    mutationFn: async (data: Partial<Scene>) => {
      await api.put(`/scenes/${sceneId}`, data)
    },
  })

  const addElementMutation = useMutation({
    mutationFn: async (elementType: string) => {
      const response = await api.post(`/scenes/${sceneId}/elements`, {
        element_type: elementType,
        name: elementType.charAt(0).toUpperCase() + elementType.slice(1),
        position_x: 100,
        position_y: 100,
        width: elementType === 'webcam' ? 320 : elementType === 'chat' ? 400 : 200,
        height: elementType === 'webcam' ? 180 : elementType === 'chat' ? 450 : 100,
        z_index: (scene?.elements.length || 0) + 1,
        properties: {},
        is_visible: true,
      })
      return response.data
    },
    onSuccess: () => {
      // Refetch scene
      window.location.reload()
    },
  })

  const handleAddElement = (elementType: string) => {
    addElementMutation.mutate(elementType)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!scene) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Scene not found</h2>
          <Link to="/dashboard" className="text-indigo-600 hover:text-indigo-500 mt-2 inline-block">
            Back to dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 h-14 flex items-center px-4">
        <div className="flex items-center gap-4 flex-1">
          <Link to="/dashboard" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <span className="text-sm text-gray-500">Project</span>
          <span className="text-gray-300">/</span>
          <span className="font-medium text-gray-900">{scene.name}</span>
        </div>

        <div className="flex items-center gap-2">
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button
            onClick={() => saveMutation.mutate(scene)}
            className="btn-primary"
            disabled={saveMutation.isPending}
          >
            <Save className="w-4 h-4 mr-2" />
            {saveMutation.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Tools */}
        <aside className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 gap-2">
          {ELEMENT_TYPES.map(({ type, label, icon: Icon }) => (
            <button
              key={type}
              onClick={() => handleAddElement(type)}
              className="w-12 h-12 flex flex-col items-center justify-center rounded-lg hover:bg-indigo-50 hover:text-indigo-600 text-gray-600 transition-colors"
              title={label}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5">{label}</span>
            </button>
          ))}
        </aside>

        {/* Center - Canvas */}
        <div className="flex-1 flex items-center justify-center p-8 overflow-auto">
          <div
            className="relative shadow-2xl"
            style={{
              width: scene.canvas_width * zoom,
              height: scene.canvas_height * zoom,
              backgroundColor: scene.background_color,
              backgroundImage: `
                linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px)
              `,
              backgroundSize: `${20 * zoom}px ${20 * zoom}px`,
            }}
          >
            {scene.elements.map((element) => (
              <div
                key={element.id}
                onClick={() => setSelectedElement(element)}
                className={`absolute cursor-pointer transition-all ${
                  selectedElement?.id === element.id
                    ? 'ring-2 ring-indigo-500'
                    : 'hover:ring-1 hover:ring-gray-400'
                }`}
                style={{
                  left: element.position_x * zoom,
                  top: element.position_y * zoom,
                  width: element.width * zoom,
                  height: element.height * zoom,
                  zIndex: element.z_index,
                }}
              >
                {element.element_type === 'webcam' && (
                  <div className="w-full h-full bg-gray-800 rounded flex items-center justify-center">
                    <Monitor className="w-8 h-8 text-gray-500" />
                  </div>
                )}
                {element.element_type === 'chat' && (
                  <div className="w-full h-full bg-black/50 rounded p-2">
                    <div className="text-white/60 text-xs">Chat placeholder</div>
                  </div>
                )}
                {element.element_type === 'text' && (
                  <div className="w-full h-full flex items-center justify-center text-white font-medium">
                    {element.properties.content || 'Text'}
                  </div>
                )}
                {element.element_type === 'panel' && (
                  <div
                    className="w-full h-full rounded"
                    style={{ backgroundColor: element.properties.background_color || '#2a2a2a' }}
                  />
                )}
                {element.element_type === 'alert' && (
                  <div className="w-full h-full bg-yellow-500/20 rounded flex items-center justify-center">
                    <Bell className="w-6 h-6 text-yellow-500" />
                  </div>
                )}
                {element.element_type === 'image' && (
                  <div className="w-full h-full bg-gray-700 rounded flex items-center justify-center">
                    <Image className="w-8 h-8 text-gray-500" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Zoom controls */}
          <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-2 flex items-center gap-2">
            <button
              onClick={() => setZoom(Math.max(0.25, zoom - 0.25))}
              className="p-1 hover:bg-gray-100 rounded"
            >
              -
            </button>
            <span className="text-sm w-12 text-center">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(Math.min(2, zoom + 0.25))}
              className="p-1 hover:bg-gray-100 rounded"
            >
              +
            </button>
          </div>
        </div>

        {/* Right sidebar - Properties */}
        <aside className="w-80 bg-white border-l border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-medium text-gray-900">Properties</h3>
          </div>

          {selectedElement ? (
            <div className="p-4 space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Name</label>
                <input
                  type="text"
                  value={selectedElement.name}
                  className="input-field mt-1"
                  readOnly
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">X</label>
                  <input
                    type="number"
                    value={selectedElement.position_x}
                    className="input-field mt-1"
                    readOnly
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Y</label>
                  <input
                    type="number"
                    value={selectedElement.position_y}
                    className="input-field mt-1"
                    readOnly
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Width</label>
                  <input
                    type="number"
                    value={selectedElement.width}
                    className="input-field mt-1"
                    readOnly
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Height</label>
                  <input
                    type="number"
                    value={selectedElement.height}
                    className="input-field mt-1"
                    readOnly
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Z-Index</label>
                <input
                  type="number"
                  value={selectedElement.z_index}
                  className="input-field mt-1"
                  readOnly
                />
              </div>
            </div>
          ) : (
            <div className="p-4 text-center text-gray-500">
              <Settings className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Select an element to edit its properties</p>
            </div>
          )}

          {/* Layers */}
          <div className="flex-1 border-t border-gray-200">
            <div className="p-3 border-b border-gray-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium">Layers</span>
            </div>
            <div className="p-2 space-y-1">
              {scene.elements.map((element) => (
                <button
                  key={element.id}
                  onClick={() => setSelectedElement(element)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 ${
                    selectedElement?.id === element.id
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  {ELEMENT_TYPES.find((t) => t.type === element.element_type)?.icon && (
                    <div className="w-4 h-4">
                      {(() => {
                        const Icon = ELEMENT_TYPES.find((t) => t.type === element.element_type)?.icon
                        return Icon ? <Icon className="w-4 h-4" /> : null
                      })()}
                    </div>
                  )}
                  <span className="flex-1 truncate">{element.name}</span>
                  <span className="text-xs text-gray-400">{element.z_index}</span>
                </button>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
