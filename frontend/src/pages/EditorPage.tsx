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
  Trash2, Copy, Eye, EyeOff, LayoutTemplate, ChevronUp, ChevronDown, Palette, Sparkles, FileJson,
} from 'lucide-react'
import html2canvas from 'html2canvas'
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

interface Template {
  id: string
  name: string
  description: string
  template_type: string
  category: string
  thumbnail_url: string | null
  scene_count: number
  theme: {
    name: string
    color_primary: string
    color_secondary: string
  } | null
}

interface Scene {
  id: string
  name: string
  background_color: string
  canvas_width: number
  canvas_height: number
  theme_id: string | null
  elements: Element[]
  layout_data?: {
    version: string
    elements: Element[]
  }
}

const ELEMENT_TYPES = [
  { type: 'webcam', label: 'Webcam', icon: Monitor },
  { type: 'chat', label: 'Chat', icon: MessageSquare },
  { type: 'alert', label: 'Alert', icon: Bell },
  { type: 'text', label: 'Text', icon: Type },
  { type: 'image', label: 'Image', icon: Image },
  { type: 'panel', label: 'Panel', icon: Square },
]

// Draggable Element Component
function DraggableElement({
  element,
  zoom,
  isSelected,
  onSelect,
  onUpdate,
}: {
  element: Element
  zoom: number
  isSelected: boolean
  onSelect: () => void
  onUpdate: (updates: Partial<Element>) => void
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: element.id,
    disabled: !isSelected,
  })

  const resizeStartRef = useRef({ x: 0, y: 0, width: element.width, height: element.height, posX: element.position_x, posY: element.position_y })

  const style = transform ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` } : undefined

  const handleResizeStart = (e: React.MouseEvent, handle: string) => {
    e.stopPropagation()
    e.preventDefault()
    resizeStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      width: element.width,
      height: element.height,
      posX: element.position_x,
      posY: element.position_y,
    }

    const handleResizeMove = (moveEvent: MouseEvent) => {
      const deltaX = (moveEvent.clientX - resizeStartRef.current.x) / zoom
      const deltaY = (moveEvent.clientY - resizeStartRef.current.y) / zoom

      let newWidth = resizeStartRef.current.width
      let newHeight = resizeStartRef.current.height
      let newX = resizeStartRef.current.posX
      let newY = resizeStartRef.current.posY

      if (handle.includes('e')) newWidth = Math.max(20, resizeStartRef.current.width + deltaX)
      if (handle.includes('w')) {
        newWidth = Math.max(20, resizeStartRef.current.width - deltaX)
        newX = resizeStartRef.current.posX + (resizeStartRef.current.width - newWidth)
      }
      if (handle.includes('s')) newHeight = Math.max(20, resizeStartRef.current.height + deltaY)
      if (handle.includes('n')) {
        newHeight = Math.max(20, resizeStartRef.current.height - deltaY)
        newY = resizeStartRef.current.posY + (resizeStartRef.current.height - newHeight)
      }

      onUpdate({ width: newWidth, height: newHeight, position_x: newX, position_y: newY })
    }

    const handleResizeEnd = () => {
      window.removeEventListener('mousemove', handleResizeMove)
      window.removeEventListener('mouseup', handleResizeEnd)
    }

    window.addEventListener('mousemove', handleResizeMove)
    window.addEventListener('mouseup', handleResizeEnd)
  }

  return (
    <div
      ref={setNodeRef}
      {...(isSelected ? { ...listeners, ...attributes } : {})}
      onClick={(e) => { e.stopPropagation(); onSelect() }}
      className={`absolute ${isDragging ? 'cursor-grabbing' : isSelected ? 'cursor-grab' : 'cursor-pointer'} ${
        isSelected ? 'ring-2 ring-indigo-500' : 'hover:ring-1 hover:ring-gray-400'
      } ${!element.is_visible ? 'opacity-50' : ''}`}
      style={{
        left: element.position_x * zoom,
        top: element.position_y * zoom,
        width: element.width * zoom,
        height: element.height * zoom,
        zIndex: element.z_index,
        ...style,
      }}
    >
      <div className="w-full h-full overflow-hidden">
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
          <div
            className="w-full h-full flex items-center justify-center font-medium"
            style={{
              color: element.properties.text_color || '#ffffff',
              fontSize: (element.properties.font_size || 24) * zoom,
              textAlign: element.properties.text_align || 'center',
            }}
          >
            {element.properties.content || 'Text'}
          </div>
        )}
        {element.element_type === 'panel' && (
          <div
            className="w-full h-full rounded"
            style={{
              backgroundColor: element.properties.background_color || '#2a2a2a',
              borderRadius: (element.properties.border_radius || 0) * zoom,
              opacity: element.properties.opacity ?? 1,
            }}
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

      {isSelected && !isDragging && (
        <>
          <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-indigo-500 cursor-nw-resize" onMouseDown={(e) => handleResizeStart(e, 'nw')} />
          <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-indigo-500 cursor-ne-resize" onMouseDown={(e) => handleResizeStart(e, 'ne')} />
          <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-indigo-500 cursor-sw-resize" onMouseDown={(e) => handleResizeStart(e, 'sw')} />
          <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-indigo-500 cursor-se-resize" onMouseDown={(e) => handleResizeStart(e, 'se')} />
          <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-2 border-indigo-500 cursor-n-resize" onMouseDown={(e) => handleResizeStart(e, 'n')} />
          <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-2 border-indigo-500 cursor-s-resize" onMouseDown={(e) => handleResizeStart(e, 's')} />
          <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-white border-2 border-indigo-500 cursor-w-resize" onMouseDown={(e) => handleResizeStart(e, 'w')} />
          <div className="absolute -right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-white border-2 border-indigo-500 cursor-e-resize" onMouseDown={(e) => handleResizeStart(e, 'e')} />
        </>
      )}
    </div>
  )
}

export default function EditorPage() {
  const { projectId, sceneId } = useParams<{ projectId: string; sceneId: string }>()
  const queryClient = useQueryClient()
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null)
  const [zoom, setZoom] = useState(0.5)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [showAIModal, setShowAIModal] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const canvasRef = useRef<HTMLDivElement>(null)
  const [showThemeModal, setShowThemeModal] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiStyle, setAiStyle] = useState('futuristic')

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

  const { data: themes } = useQuery({
    queryKey: ['themes'],
    queryFn: async () => {
      const response = await api.get('/themes')
      return response.data.data as Theme[]
    },
  })

  const { data: templates } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      const response = await api.get('/templates')
      return response.data.data as Template[]
    },
  })

  const updateElementMutation = useMutation({
    mutationFn: async ({ elementId, updates }: { elementId: string; updates: Partial<Element> }) => {
      await api.put(`/elements/${elementId}`, updates)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const updateSceneMutation = useMutation({
    mutationFn: async (updates: Partial<Scene>) => {
      await api.put(`/scenes/${sceneId}`, updates)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
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
        height: elementType === 'webcam' ? 180 : elementType === 'chat' ? 450 : 150,
        z_index: (scene?.elements.length || 0) + 1,
        properties: elementType === 'text' ? { content: 'New Text', font_size: 24, text_color: '#ffffff' } : {},
        is_visible: true,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const applyTemplateMutation = useMutation({
    mutationFn: async (templateId: string) => {
      const response = await api.post(`/scenes/${sceneId}/apply-template`, { template_id: templateId })
      return response.data
    },
    onSuccess: () => {
      setShowTemplateModal(false)
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const generateAIMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/ai/generate-scene', {
        prompt: aiPrompt,
        style: aiStyle,
        canvas_width: scene?.canvas_width || 1920,
        canvas_height: scene?.canvas_height || 1080,
      })
      return response.data
    },
    onSuccess: (data) => {
      setShowAIModal(false)
      setAiPrompt('')
      // Poll for completion
      pollGeneration(data.id)
    },
  })

  const pollGeneration = async (generationId: string) => {
    const interval = setInterval(async () => {
      const response = await api.get(`/ai/generations/${generationId}`)
      if (response.data.status === 'success') {
        clearInterval(interval)
        // Apply the generated layout
        if (response.data.result) {
          await api.put(`/scenes/${sceneId}`, {
            layout_data: response.data.result.layout,
          })
          queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
        }
      } else if (response.data.status === 'error') {
        clearInterval(interval)
        alert('AI generation failed: ' + response.data.error_message)
      }
    }, 2000)
  }

  const exportPNGMutation = useMutation({
    mutationFn: async () => {
      const canvasEl = canvasRef.current
      if (!canvasEl) throw new Error('Canvas not found')

      const canvas = await html2canvas(canvasEl, {
        scale: 1,
        backgroundColor: null,
        useCORS: true,
        allowTaint: true,
      })

      const link = document.createElement('a')
      link.download = `${scene?.name || 'scene'}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    },
    onSuccess: () => {
      setShowExportModal(false)
    },
    onError: (error) => {
      alert('Failed to export PNG: ' + error.message)
    },
  })

  const exportJSONMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/scenes/${sceneId}/export/json`)
      return response.data
    },
    onSuccess: (data) => {
      window.open(data.download_url, '_blank')
    },
  })

  const deleteElementMutation = useMutation({
    mutationFn: async (elementId: string) => {
      await api.delete(`/elements/${elementId}`)
    },
    onSuccess: () => {
      setSelectedElementId(null)
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const duplicateElementMutation = useMutation({
    mutationFn: async (element: Element) => {
      const response = await api.post(`/scenes/${sceneId}/elements`, {
        element_type: element.element_type,
        name: `${element.name} (Copy)`,
        position_x: element.position_x + 20,
        position_y: element.position_y + 20,
        width: element.width,
        height: element.height,
        z_index: (scene?.elements.length || 0) + 1,
        properties: element.properties,
        is_visible: element.is_visible,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const toggleVisibilityMutation = useMutation({
    mutationFn: async ({ elementId, isVisible }: { elementId: string; isVisible: boolean }) => {
      await api.put(`/elements/${elementId}`, { is_visible: !isVisible })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scene', sceneId] })
    },
  })

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, delta } = event
      if (!delta.x && !delta.y) return

      const elementId = active.id as string
      const element = scene?.elements.find((e) => e.id === elementId)
      if (!element) return

      const newX = Math.max(0, element.position_x + delta.x / zoom)
      const newY = Math.max(0, element.position_y + delta.y / zoom)
      const maxX = (scene?.canvas_width || 1920) - element.width
      const maxY = (scene?.canvas_height || 1080) - element.height

      updateElementMutation.mutate({
        elementId,
        updates: { position_x: Math.min(newX, maxX), position_y: Math.min(newY, maxY) },
      })
    },
    [scene, zoom, updateElementMutation]
  )

  const handleElementUpdate = useCallback(
    (elementId: string, updates: Partial<Element>) => {
      updateElementMutation.mutate({ elementId, updates })
    },
    [updateElementMutation]
  )

  const selectedElement = scene?.elements.find((e) => e.id === selectedElementId) || null
  const currentTheme = themes?.find((t) => t.id === scene?.theme_id)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (!updateSceneMutation.isPending) {
          updateSceneMutation.mutate({ layout_data: { version: '1.0', elements: scene?.elements || [] } })
        }
        return
      }

      // Delete to remove element
      if (e.key === 'Delete' && selectedElementId) {
        deleteElementMutation.mutate(selectedElementId)
      }

      // Escape to deselect
      if (e.key === 'Escape') {
        setSelectedElementId(null)
      }

      // Arrow keys to move selected element
      if (selectedElement && selectedElementId) {
        const step = e.shiftKey ? 10 : 1
        let updates: Partial<Element> = {}

        switch (e.key) {
          case 'ArrowUp':
            updates = { position_y: Math.max(0, selectedElement.position_y - step) }
            break
          case 'ArrowDown':
            updates = { position_y: Math.min((scene?.canvas_height || 1080) - selectedElement.height, selectedElement.position_y + step) }
            break
          case 'ArrowLeft':
            updates = { position_x: Math.max(0, selectedElement.position_x - step) }
            break
          case 'ArrowRight':
            updates = { position_x: Math.min((scene?.canvas_width || 1920) - selectedElement.width, selectedElement.position_x + step) }
            break
        }

        if (updates.position_x !== undefined || updates.position_y !== undefined) {
          e.preventDefault()
          handleElementUpdate(selectedElement.id, updates)
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedElementId, deleteElementMutation, updateSceneMutation, scene?.elements, selectedElement, scene?.canvas_height, scene?.canvas_width, handleElementUpdate])

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
    <DndContext sensors={sensors} onDragEnd={handleDragEnd} modifiers={[restrictToParentElement]}>
      <div className="min-h-screen bg-gray-100 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-14 flex items-center px-4">
          <div className="flex items-center gap-4 flex-1">
            <Link to={`/projects/${projectId}`} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </Link>
            <span className="text-sm text-gray-500">Project</span>
            <span className="text-gray-300">/</span>
            <span className="font-medium text-gray-900">{scene.name}</span>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={() => setShowThemeModal(true)} className="btn-secondary">
              <Palette className="w-4 h-4 mr-2" />
              {currentTheme?.name || 'Theme'}
            </button>
            <button onClick={() => setShowTemplateModal(true)} className="btn-secondary">
              <LayoutTemplate className="w-4 h-4 mr-2" />
              Templates
            </button>
            <button onClick={() => setShowAIModal(true)} className="btn-secondary">
              <Sparkles className="w-4 h-4 mr-2" />
              AI
            </button>
            <button onClick={() => setShowExportModal(true)} className="btn-secondary">
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
            <button
              onClick={() => updateSceneMutation.mutate({ layout_data: { version: '1.0', elements: scene.elements } })}
              className="btn-primary"
              disabled={updateSceneMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              {updateSceneMutation.isPending ? 'Saving...' : 'Save'}
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
                onClick={() => addElementMutation.mutate(type)}
                disabled={addElementMutation.isPending}
                className="w-12 h-12 flex flex-col items-center justify-center rounded-lg hover:bg-indigo-50 hover:text-indigo-600 text-gray-600 transition-colors disabled:opacity-50"
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
              ref={canvasRef}
              className="relative shadow-2xl"
              style={{
                width: scene.canvas_width * zoom,
                height: scene.canvas_height * zoom,
                backgroundColor: currentTheme?.color_background || scene.background_color,
                backgroundImage: `linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px)`,
                backgroundSize: `${20 * zoom}px ${20 * zoom}px`,
              }}
              onClick={() => setSelectedElementId(null)}
            >
              {scene.elements.map((element) => (
                <DraggableElement
                  key={element.id}
                  element={element}
                  zoom={zoom}
                  isSelected={selectedElementId === element.id}
                  onSelect={() => setSelectedElementId(element.id)}
                  onUpdate={(updates) => handleElementUpdate(element.id, updates)}
                />
              ))}
            </div>

            <div className="absolute bottom-4 right-80 bg-white rounded-lg shadow-lg p-2 flex items-center gap-2">
              <button onClick={() => setZoom(Math.max(0.25, zoom - 0.25))} className="p-1 hover:bg-gray-100 rounded">-</button>
              <span className="text-sm w-12 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom(Math.min(2, zoom + 0.25))} className="p-1 hover:bg-gray-100 rounded">+</button>
            </div>
          </div>

          {/* Right sidebar - Properties & Layers */}
          <aside className="w-80 bg-white border-l border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-medium text-gray-900">Properties</h3>
            </div>

            {selectedElement ? (
              <div className="p-4 space-y-4 overflow-y-auto flex-1">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Name</label>
                  <input
                    type="text"
                    value={selectedElement.name}
                    onChange={(e) => handleElementUpdate(selectedElement.id, { name: e.target.value })}
                    className="input-field mt-1"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">X</label>
                    <input
                      type="number"
                      value={selectedElement.position_x}
                      onChange={(e) => handleElementUpdate(selectedElement.id, { position_x: parseInt(e.target.value) || 0 })}
                      className="input-field mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Y</label>
                    <input
                      type="number"
                      value={selectedElement.position_y}
                      onChange={(e) => handleElementUpdate(selectedElement.id, { position_y: parseInt(e.target.value) || 0 })}
                      className="input-field mt-1"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Width</label>
                    <input
                      type="number"
                      value={selectedElement.width}
                      onChange={(e) => handleElementUpdate(selectedElement.id, { width: parseInt(e.target.value) || 20 })}
                      className="input-field mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Height</label>
                    <input
                      type="number"
                      value={selectedElement.height}
                      onChange={(e) => handleElementUpdate(selectedElement.id, { height: parseInt(e.target.value) || 20 })}
                      className="input-field mt-1"
                    />
                  </div>
                </div>

                {/* Text Element Styling */}
                {selectedElement.element_type === 'text' && (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Content</label>
                      <textarea
                        value={selectedElement.properties.content || ''}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, content: e.target.value }
                        })}
                        className="input-field mt-1 h-20 resize-none"
                        rows={2}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase">Font Size</label>
                        <input
                          type="number"
                          value={selectedElement.properties.font_size || 24}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, font_size: parseInt(e.target.value) || 24 }
                          })}
                          className="input-field mt-1"
                          min={8}
                          max={120}
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase">Text Color</label>
                        <div className="flex items-center gap-2 mt-1">
                          <input
                            type="color"
                            value={selectedElement.properties.text_color || '#ffffff'}
                            onChange={(e) => handleElementUpdate(selectedElement.id, { 
                              properties: { ...selectedElement.properties, text_color: e.target.value }
                            })}
                            className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                          />
                          <input
                            type="text"
                            value={selectedElement.properties.text_color || '#ffffff'}
                            onChange={(e) => handleElementUpdate(selectedElement.id, { 
                              properties: { ...selectedElement.properties, text_color: e.target.value }
                            })}
                            className="input-field flex-1 text-sm"
                            placeholder="#ffffff"
                          />
                        </div>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Text Align</label>
                      <div className="flex gap-1 mt-1">
                        {['left', 'center', 'right'].map((align) => (
                          <button
                            key={align}
                            onClick={() => handleElementUpdate(selectedElement.id, { 
                              properties: { ...selectedElement.properties, text_align: align }
                            })}
                            className={`flex-1 py-2 rounded-lg text-sm capitalize ${
                              selectedElement.properties.text_align === align 
                                ? 'bg-indigo-600 text-white' 
                                : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                          >
                            {align}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Font Weight</label>
                      <select
                        value={selectedElement.properties.font_weight || 'normal'}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, font_weight: e.target.value }
                        })}
                        className="input-field mt-1"
                      >
                        <option value="normal">Normal</option>
                        <option value="bold">Bold</option>
                        <option value="lighter">Light</option>
                      </select>
                    </div>
                  </>
                )}

                {/* Panel Element Styling */}
                {selectedElement.element_type === 'panel' && (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Background Color</label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="color"
                          value={selectedElement.properties.background_color || '#2a2a2a'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, background_color: e.target.value }
                          })}
                          className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                        />
                        <input
                          type="text"
                          value={selectedElement.properties.background_color || '#2a2a2a'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, background_color: e.target.value }
                          })}
                          className="input-field flex-1 text-sm"
                          placeholder="#2a2a2a"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Border Radius</label>
                      <input
                        type="range"
                        value={selectedElement.properties.border_radius || 0}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, border_radius: parseInt(e.target.value) }
                        })}
                        className="w-full mt-2"
                        min={0}
                        max={50}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {selectedElement.properties.border_radius || 0}px
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Opacity</label>
                      <input
                        type="range"
                        value={Math.round((selectedElement.properties.opacity ?? 1) * 100)}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, opacity: parseInt(e.target.value) / 100 }
                        })}
                        className="w-full mt-2"
                        min={0}
                        max={100}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {Math.round((selectedElement.properties.opacity ?? 1) * 100)}%
                      </div>
                    </div>
                  </>
                )}

                {/* Webcam Element Styling */}
                {selectedElement.element_type === 'webcam' && (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Border Color</label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="color"
                          value={selectedElement.properties.border_color || '#6366f1'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, border_color: e.target.value }
                          })}
                          className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                        />
                        <input
                          type="text"
                          value={selectedElement.properties.border_color || '#6366f1'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, border_color: e.target.value }
                          })}
                          className="input-field flex-1 text-sm"
                          placeholder="#6366f1"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Border Width</label>
                      <input
                        type="range"
                        value={selectedElement.properties.border_width || 2}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, border_width: parseInt(e.target.value) }
                        })}
                        className="w-full mt-2"
                        min={0}
                        max={20}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {selectedElement.properties.border_width || 2}px
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Border Radius</label>
                      <input
                        type="range"
                        value={selectedElement.properties.border_radius || 8}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, border_radius: parseInt(e.target.value) }
                        })}
                        className="w-full mt-2"
                        min={0}
                        max={50}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {selectedElement.properties.border_radius || 8}px
                      </div>
                    </div>
                  </>
                )}

                {/* Chat Element Styling */}
                {selectedElement.element_type === 'chat' && (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Background Color</label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="color"
                          value={selectedElement.properties.background_color || '#1a1a1a'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, background_color: e.target.value }
                          })}
                          className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                        />
                        <input
                          type="text"
                          value={selectedElement.properties.background_color || '#1a1a1a'}
                          onChange={(e) => handleElementUpdate(selectedElement.id, { 
                            properties: { ...selectedElement.properties, background_color: e.target.value }
                          })}
                          className="input-field flex-1 text-sm"
                          placeholder="#1a1a1a"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Font Size</label>
                      <input
                        type="number"
                        value={selectedElement.properties.font_size || 14}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, font_size: parseInt(e.target.value) || 14 }
                        })}
                        className="input-field mt-1"
                        min={8}
                        max={32}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Border Radius</label>
                      <input
                        type="range"
                        value={selectedElement.properties.border_radius || 8}
                        onChange={(e) => handleElementUpdate(selectedElement.id, { 
                          properties: { ...selectedElement.properties, border_radius: parseInt(e.target.value) }
                        })}
                        className="w-full mt-2"
                        min={0}
                        max={50}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {selectedElement.properties.border_radius || 8}px
                      </div>
                    </div>
                  </>
                )}

                <div className="border-t pt-4 mt-4">
                  <label className="text-xs font-medium text-gray-500 uppercase mb-2 block">Layer Order</label>
                  <div className="flex gap-2">
                    <button onClick={() => handleElementUpdate(selectedElement.id, { z_index: selectedElement.z_index + 1 })} className="btn-secondary flex-1">
                      <ChevronUp className="w-4 h-4 mr-1 inline" />
                      Forward
                    </button>
                    <button onClick={() => handleElementUpdate(selectedElement.id, { z_index: Math.max(0, selectedElement.z_index - 1) })} className="btn-secondary flex-1">
                      <ChevronDown className="w-4 h-4 mr-1 inline" />
                      Back
                    </button>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => toggleVisibilityMutation.mutate({ elementId: selectedElement.id, isVisible: selectedElement.is_visible })}
                    className="btn-secondary flex-1"
                  >
                    {selectedElement.is_visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  </button>
                  <button onClick={() => duplicateElementMutation.mutate(selectedElement)} className="btn-secondary flex-1">
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteElementMutation.mutate(selectedElement.id)}
                    className="btn-secondary flex-1 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-500">
                <Settings className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Select an element to edit its properties</p>
              </div>
            )}

            <div className="flex-1 border-t border-gray-200 flex flex-col min-h-0">
              <div className="p-3 border-b border-gray-200 flex items-center gap-2">
                <Layers className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">Layers</span>
              </div>
              <div className="p-2 space-y-1 overflow-y-auto flex-1">
                {[...scene.elements].sort((a, b) => b.z_index - a.z_index).map((element) => (
                  <button
                    key={element.id}
                    onClick={() => setSelectedElementId(element.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 ${
                      selectedElementId === element.id ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100 text-gray-700'
                    } ${!element.is_visible ? 'opacity-50' : ''}`}
                  >
                    {(() => {
                      const Icon = ELEMENT_TYPES.find((t) => t.type === element.element_type)?.icon
                      return Icon ? <Icon className="w-4 h-4" /> : null
                    })()}
                    <span className="flex-1 truncate">{element.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* Theme Modal */}
      {showThemeModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Select Theme</h2>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {themes?.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => { updateSceneMutation.mutate({ theme_id: theme.id }); setShowThemeModal(false) }}
                  className={`w-full p-3 rounded-lg border text-left flex items-center gap-3 ${
                    scene.theme_id === theme.id ? 'border-indigo-500 bg-indigo-50' : 'hover:border-gray-300'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full border" style={{ backgroundColor: theme.color_primary }} />
                  <div>
                    <div className="font-medium">{theme.name}</div>
                    <div className="text-xs text-gray-500 flex gap-1">
                      <span style={{ color: theme.color_primary }}>Primary</span>
                      <span>•</span>
                      <span style={{ color: theme.color_secondary }}>Secondary</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <button onClick={() => setShowThemeModal(false)} className="btn-secondary w-full mt-4">Close</button>
          </div>
        </div>
      )}

      {/* Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-auto">
            <h2 className="text-xl font-bold mb-4">Apply Template</h2>
            <div className="grid grid-cols-2 gap-3">
              {templates?.map((template) => (
                <button
                  key={template.id}
                  onClick={() => applyTemplateMutation.mutate(template.id)}
                  disabled={applyTemplateMutation.isPending}
                  className="p-4 border rounded-lg hover:border-indigo-500 text-left transition-colors disabled:opacity-50"
                >
                  <div className="flex items-center gap-2 mb-2">
                    {template.theme && (
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: template.theme.color_primary }} />
                    )}
                    <span className="font-medium">{template.name}</span>
                  </div>
                  <p className="text-sm text-gray-500">{template.description}</p>
                  <div className="text-xs text-gray-400 mt-2 capitalize">{template.category}</div>
                </button>
              ))}
            </div>
            <button onClick={() => setShowTemplateModal(false)} className="btn-secondary w-full mt-4">Cancel</button>
          </div>
        </div>
      )}

      {/* AI Generation Modal */}
      {showAIModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
            <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-indigo-600" />
              AI Scene Generator
            </h2>
            <p className="text-gray-600 mb-4">Describe your ideal stream layout and AI will generate it.</p>
            <textarea
              className="input-field w-full h-24 mb-4"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="e.g., Create a futuristic gaming setup with neon blue accents, webcam bottom right, chat on the left side..."
            />
            <div className="flex gap-2 mb-4">
              {['minimal', 'futuristic', 'cozy', 'professional', 'vibrant', 'retro'].map((style) => (
                <button
                  key={style}
                  onClick={() => setAiStyle(style)}
                  className={`px-3 py-1.5 rounded-lg text-sm capitalize ${
                    aiStyle === style ? 'bg-indigo-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowAIModal(false)} className="btn-secondary flex-1">Cancel</button>
              <button
                onClick={() => generateAIMutation.mutate()}
                disabled={!aiPrompt || generateAIMutation.isPending}
                className="btn-primary flex-1"
              >
                {generateAIMutation.isPending ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Export Scene</h2>
            <div className="space-y-3">
              <button
                onClick={() => exportPNGMutation.mutate()}
                disabled={exportPNGMutation.isPending}
                className="w-full p-4 border rounded-lg hover:border-indigo-500 text-left flex items-center gap-3 disabled:opacity-50"
              >
                <Image className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="font-medium">Export as PNG</div>
                  <div className="text-sm text-gray-500">High quality image for preview</div>
                </div>
              </button>
              <button
                onClick={() => exportJSONMutation.mutate()}
                disabled={exportJSONMutation.isPending}
                className="w-full p-4 border rounded-lg hover:border-indigo-500 text-left flex items-center gap-3 disabled:opacity-50"
              >
                <FileJson className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="font-medium">Export as JSON</div>
                  <div className="text-sm text-gray-500">For OBS Studio import</div>
                </div>
              </button>
            </div>
            <button onClick={() => setShowExportModal(false)} className="btn-secondary w-full mt-4">Close</button>
          </div>
        </div>
      )}
    </DndContext>
  )
}
