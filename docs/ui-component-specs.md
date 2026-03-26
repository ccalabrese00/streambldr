# UI Component Specifications - AI Stream Scene Builder

## Design System

### Color Palette

**Primary Colors:**
- `--color-primary-50`: #eef2ff
- `--color-primary-100`: #e0e7ff
- `--color-primary-200`: #c7d2fe
- `--color-primary-300`: #a5b4fc
- `--color-primary-400`: #818cf8
- `--color-primary-500`: #6366f1
- `--color-primary-600`: #4f46e5 (Main brand color)
- `--color-primary-700`: #4338ca
- `--color-primary-800`: #3730a3
- `--color-primary-900`: #312e81

**Neutral Colors:**
- `--color-gray-50`: #f9fafb
- `--color-gray-100`: #f3f4f6
- `--color-gray-200`: #e5e7eb
- `--color-gray-300`: #d1d5db
- `--color-gray-400`: #9ca3af
- `--color-gray-500`: #6b7280
- `--color-gray-600`: #4b5563
- `--color-gray-700`: #374151
- `--color-gray-800`: #1f2937
- `--color-gray-900`: #111827

**Semantic Colors:**
- `--color-success`: #22c55e
- `--color-warning`: #f59e0b
- `--color-error`: #ef4444
- `--color-info`: #3b82f6

**Canvas Colors:**
- `--canvas-bg`: #1a1a1a
- `--canvas-grid`: #2a2a2a
- `--selection-border`: #4f46e5
- `--selection-handle`: #ffffff

---

### Typography

**Font Families:**
- Primary: "Inter", system-ui, sans-serif
- Heading (alternative): "Poppins", sans-serif
- Monospace: "JetBrains Mono", monospace
- Decorative: "Orbitron" (for gaming themes)

**Font Sizes:**
| Name | Size | Line Height | Usage |
|------|------|-------------|-------|
| xs | 12px | 16px | Badges, captions |
| sm | 14px | 20px | Body small, labels |
| base | 16px | 24px | Body text |
| lg | 18px | 28px | Lead paragraphs |
| xl | 20px | 28px | H6, small headings |
| 2xl | 24px | 32px | H5 |
| 3xl | 30px | 36px | H4 |
| 4xl | 36px | 40px | H3 |
| 5xl | 48px | 48px | H2 |
| 6xl | 60px | 60px | H1 |

**Font Weights:**
- 400: Regular
- 500: Medium
- 600: Semibold
- 700: Bold

---

### Spacing Scale

| Name | Value |
|------|-------|
| 0 | 0px |
| px | 1px |
| 0.5 | 2px |
| 1 | 4px |
| 2 | 8px |
| 3 | 12px |
| 4 | 16px |
| 5 | 20px |
| 6 | 24px |
| 8 | 32px |
| 10 | 40px |
| 12 | 48px |
| 16 | 64px |
| 20 | 80px |
| 24 | 96px |

---

### Border Radius

| Name | Value |
|------|-------|
| none | 0 |
| sm | 2px |
| base | 4px |
| md | 6px |
| lg | 8px |
| xl | 12px |
| 2xl | 16px |
| 3xl | 24px |
| full | 9999px |

---

### Shadows

| Name | Value |
|------|-------|
| sm | 0 1px 2px 0 rgb(0 0 0 / 0.05) |
| base | 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) |
| md | 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) |
| lg | 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1) |
| xl | 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1) |
| inner | inset 0 2px 4px 0 rgb(0 0 0 / 0.05) |

---

## Component Library

### 1. Buttons

**Primary Button:**
```tsx
<button className="
  inline-flex items-center justify-center
  px-4 py-2
  bg-indigo-600 hover:bg-indigo-700
  text-white font-medium text-sm
  rounded-lg
  shadow-sm
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
">
```

**Secondary Button:**
```tsx
<button className="
  inline-flex items-center justify-center
  px-4 py-2
  bg-white hover:bg-gray-50
  text-gray-700 font-medium text-sm
  border border-gray-300
  rounded-lg
  shadow-sm
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
">
```

**Ghost Button:**
```tsx
<button className="
  inline-flex items-center justify-center
  px-3 py-2
  text-gray-600 hover:text-gray-900 hover:bg-gray-100
  font-medium text-sm
  rounded-lg
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-gray-500
">
```

**Icon Button:**
```tsx
<button className="
  inline-flex items-center justify-center
  w-10 h-10
  text-gray-600 hover:text-gray-900 hover:bg-gray-100
  rounded-lg
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-gray-500
">
```

**Button Sizes:**
- sm: px-3 py-1.5, text-sm
- md: px-4 py-2, text-sm (default)
- lg: px-6 py-3, text-base

---

### 2. Inputs

**Text Input:**
```tsx
<input className="
  w-full
  px-3 py-2
  bg-white
  border border-gray-300
  rounded-md
  text-sm text-gray-900
  placeholder:text-gray-400
  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
  disabled:bg-gray-50 disabled:text-gray-500
"/>
```

**Textarea:**
```tsx
<textarea className="
  w-full
  px-3 py-2
  bg-white
  border border-gray-300
  rounded-md
  text-sm text-gray-900
  placeholder:text-gray-400
  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
  resize-y
  min-h-[80px]
"/>
```

**Select:**
```tsx
<select className="
  w-full
  px-3 py-2
  bg-white
  border border-gray-300
  rounded-md
  text-sm text-gray-900
  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
  appearance-none
  bg-[url('data:image/svg+xml,...')] bg-no-repeat bg-right-3
">
```

**Color Picker:**
```tsx
<div className="flex items-center gap-2">
  <div className="
    w-8 h-8
    rounded-full
    border-2 border-gray-200
    cursor-pointer
    shadow-inner
  " style={{ backgroundColor: value }} />
  <input 
    type="text" 
    value={value}
    className="w-24 px-2 py-1 text-sm border rounded"
    placeholder="#000000"
  />
</div>
```

**Slider:**
```tsx
<input
  type="range"
  className="
    w-full
    h-1
    bg-gray-200 rounded-lg appearance-none cursor-pointer
    accent-indigo-600
  "
/>
```

---

### 3. Cards

**Project Card:**
```tsx
<div className="
  group
  relative
  bg-white
  rounded-xl
  shadow-sm hover:shadow-md
  transition-all duration-200
  hover:scale-[1.02]
  cursor-pointer
  overflow-hidden
">
  <div className="aspect-video bg-gray-100">
    <img src={thumbnail} className="w-full h-full object-cover" />
  </div>
  <div className="p-4">
    <h3 className="font-semibold text-gray-900 truncate">{name}</h3>
    <p className="text-sm text-gray-500">{scenes} scenes • {time}</p>
  </div>
  <button className="
    absolute top-2 right-2
    opacity-0 group-hover:opacity-100
    p-1.5
    bg-white/90 backdrop-blur rounded-lg
    text-gray-600 hover:text-gray-900
    transition-opacity
  ">
    <MoreHorizontal className="w-4 h-4" />
  </button>
</div>
```

**Element Card (Toolbar):**
```tsx
<div className="
  flex flex-col items-center justify-center
  p-4
  bg-white
  border border-gray-200 hover:border-indigo-500
  rounded-lg
  cursor-grab active:cursor-grabbing
  hover:bg-indigo-50
  transition-colors duration-150
">
  <div className="w-8 h-8 text-gray-600">{icon}</div>
  <span className="mt-2 text-xs text-gray-700 font-medium">{label}</span>
</div>
```

---

### 4. Modals

**Modal Overlay:**
```tsx
<div className="
  fixed inset-0
  z-50
  bg-black/50 backdrop-blur-sm
  flex items-center justify-center
  p-4
">
```

**Modal Container:**
```tsx
<div className="
  relative
  w-full max-w-2xl
  bg-white
  rounded-2xl
  shadow-2xl
  overflow-hidden
">
  <div className="flex items-center justify-between px-6 py-4 border-b">
    <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
    <button className="p-1 text-gray-400 hover:text-gray-600">
      <X className="w-5 h-5" />
    </button>
  </div>
  <div className="p-6">{content}</div>
  <div className="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t">
    <button className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
      Cancel
    </button>
    <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg">
      Confirm
    </button>
  </div>
</div>
```

---

### 5. Navigation

**Header:**
```tsx
<header className="
  h-16
  bg-white
  border-b border-gray-200
  px-6
  flex items-center justify-between
  sticky top-0 z-40
">
  <div className="flex items-center gap-8">
    <Logo className="h-8" />
    <nav className="hidden md:flex items-center gap-6">
      <a className="text-sm font-medium text-gray-900">Dashboard</a>
      <a className="text-sm text-gray-500 hover:text-gray-900">Templates</a>
    </nav>
  </div>
  <div className="flex items-center gap-4">
    <SearchInput className="w-64" />
    <UserDropdown />
  </div>
</header>
```

**Sidebar:**
```tsx
<aside className="
  w-72
  bg-white
  border-r border-gray-200
  flex flex-col
  overflow-y-auto
">
  <div className="p-4 border-b">
    <h3 className="font-semibold text-gray-900">{sectionTitle}</h3>
  </div>
  <div className="p-4 flex-1">{content}</div>
</aside>
```

---

### 6. Editor Components

**Canvas:**
```tsx
<div className="
  relative
  w-[1920px] h-[1080px]
  bg-[#1a1a1a]
  shadow-2xl
  overflow-hidden
">
  {/* Grid pattern */}
  <div 
    className="absolute inset-0 opacity-20"
    style={{
      backgroundImage: `
        linear-gradient(to right, #2a2a2a 1px, transparent 1px),
        linear-gradient(to bottom, #2a2a2a 1px, transparent 1px)
      `,
      backgroundSize: '20px 20px'
    }}
  />
  
  {/* Elements */}
  {elements.map(el => <CanvasElement key={el.id} {...el} />)}
</div>
```

**Canvas Element (Selected):**
```tsx
<div className="
  absolute
  border-2 border-indigo-500
  bg-indigo-500/10
">
  {/* Element content */}
  <div className="w-full h-full">{renderElement()}</div>
  
  {/* Resize handles */}
  <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white border border-indigo-500 cursor-nw-resize" />
  <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white border border-indigo-500 cursor-n-resize" />
  <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white border border-indigo-500 cursor-ne-resize" />
  <div className="absolute top-1/2 -right-1.5 -translate-y-1/2 w-3 h-3 bg-white border border-indigo-500 cursor-e-resize" />
  <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-white border border-indigo-500 cursor-se-resize" />
  <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white border border-indigo-500 cursor-s-resize" />
  <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-white border border-indigo-500 cursor-sw-resize" />
  <div className="absolute top-1/2 -left-1.5 -translate-y-1/2 w-3 h-3 bg-white border border-indigo-500 cursor-w-resize" />
</div>
```

**Layer Item:**
```tsx
<div className="
  flex items-center gap-2
  px-3 py-2
  rounded-lg
  cursor-pointer
  hover:bg-gray-100
  data-[selected=true]:bg-indigo-50 data-[selected=true]:text-indigo-900
">
  <Eye className="w-4 h-4 text-gray-400" />
  <Lock className="w-4 h-4 text-gray-400" />
  <span className="flex-1 text-sm truncate">{element.name}</span>
  <span className="text-xs text-gray-400">{element.z_index}</span>
</div>
```

---

### 7. Feedback Components

**Toast Notification:**
```tsx
<div className="
  fixed bottom-4 right-4
  z-50
  flex items-center gap-3
  px-4 py-3
  bg-white
  border border-gray-200
  rounded-lg
  shadow-lg
">
  <div className={cn(
    "w-5 h-5 rounded-full flex items-center justify-center",
    type === 'success' && "bg-green-100 text-green-600",
    type === 'error' && "bg-red-100 text-red-600",
    type === 'info' && "bg-blue-100 text-blue-600"
  )}>
    {icon}
  </div>
  <span className="text-sm text-gray-700">{message}</span>
  <button className="text-gray-400 hover:text-gray-600">
    <X className="w-4 h-4" />
  </button>
</div>
```

**Loading Spinner:**
```tsx
<div className="
  inline-block
  w-5 h-5
  border-2 border-current border-t-transparent
  rounded-full
  animate-spin
"/>
```

**Skeleton:**
```tsx
<div className="
  animate-pulse
  bg-gray-200 rounded
"/>
```

**Empty State:**
```tsx
<div className="
  flex flex-col items-center justify-center
  py-16
  text-center
">
  <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
    <FolderOpen className="w-10 h-10 text-gray-400" />
  </div>
  <h3 className="text-lg font-medium text-gray-900 mb-1">No projects yet</h3>
  <p className="text-sm text-gray-500 mb-4">Create your first streaming scene</p>
  <Button>Create Project</Button>
</div>
```

---

### 8. Form Components

**Form Group:**
```tsx
<div className="space-y-1.5">
  <label className="block text-sm font-medium text-gray-700">
    {label}
    {required && <span className="text-red-500 ml-1">*</span>}
  </label>
  {children}
  {error && <p className="text-sm text-red-600">{error}</p>}
  {hint && <p className="text-sm text-gray-500">{hint}</p>}
</div>
```

**Field Row (Horizontal):**
```tsx
<div className="flex items-center gap-4">
  <div className="flex-1">
    <label className="text-sm text-gray-600">X</label>
    <NumberInput value={x} onChange={setX} suffix="px" />
  </div>
  <div className="flex-1">
    <label className="text-sm text-gray-600">Y</label>
    <NumberInput value={y} onChange={setY} suffix="px" />
  </div>
</div>
```

---

### 9. Status Indicators

**Save Status:**
```tsx
<div className="
  flex items-center gap-2
  text-sm text-gray-500
">
  {status === 'saving' && <>
    <Spinner className="w-3 h-3" />
    <span>Saving...</span>
  </>}
  {status === 'saved' && <>
    <Check className="w-3 h-3 text-green-500" />
    <span>Saved</span>
  </>}
  {status === 'unsaved' && <>
    <Circle className="w-3 h-3 fill-amber-500" />
    <span>Unsaved changes</span>
  </>}
</div>
```

**Badge:**
```tsx
<span className={cn(
  "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
  variant === 'default' && "bg-gray-100 text-gray-800",
  variant === 'primary' && "bg-indigo-100 text-indigo-800",
  variant === 'success' && "bg-green-100 text-green-800",
  variant === 'warning' && "bg-amber-100 text-amber-800",
  variant === 'error' && "bg-red-100 text-red-800"
)}>
  {children}
</span>
```

---

## Responsive Breakpoints

| Name | Min Width | Description |
|------|-----------|-------------|
| sm | 640px | Small devices |
| md | 768px | Tablets |
| lg | 1024px | Desktop |
| xl | 1280px | Large desktop |
| 2xl | 1536px | Extra large |

**Editor Minimum:** 1280px (show warning below)

---

## Animation Specifications

**Transitions:**
- Default: 150ms ease-in-out
- Slow: 300ms ease-in-out
- Bounce: 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)

**Element Interactions:**
- Hover: scale(1.02), shadow increase
- Select: border highlight with fade
- Drag: opacity 0.8, shadow lift
- Drop: bounce back animation

**Modal:**
- Enter: opacity 0→1, scale 0.95→1
- Exit: opacity 1→0, scale 1→0.95
- Duration: 200ms

**Toast:**
- Enter: slide up + fade in
- Exit: slide right + fade out
- Duration: 300ms

---

## Accessibility

- Focus rings on all interactive elements
- ARIA labels for icon buttons
- Keyboard navigation support
- Screen reader announcements for dynamic content
- Minimum touch target: 44x44px on mobile
- Color contrast ratio: 4.5:1 minimum

---

## Version History

- v1.0 (2026-03-26): Initial component specifications
