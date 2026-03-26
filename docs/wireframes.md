# Wireframe Specifications - AI Stream Scene Builder

## Screen Inventory

1. **Auth Screens**: Login, Register, Forgot Password, Reset Password
2. **Dashboard**: Project grid/listing, empty state, project actions
3. **Scene Editor**: Main editor canvas with toolbars and panels
4. **Template Library**: Browse, preview, and select templates
5. **Modals/Dialogs**: AI Generation, Export, Settings, Theme picker

---

## 1. Authentication Screens

### 1.1 Login Screen
**Route:** `/login`

**Layout:**
```
+------------------+--------------------------+
|                  |                          |
|   [Logo]         |     Welcome Back         |
|                  |                          |
|   [Hero Image    |     Email                |
|    or Branding]  |     [________________]   |
|                  |                          |
|                  |     Password             |
|                  |     [________________]   |
|                  |     [ ] Remember me      |
|                  |                          |
|                  |     [   Sign In   ]      |
|                  |                          |
|                  |     Forgot password?     |
|                  |                          |
|                  |     ── or ──             |
|                  |     [ Sign up ]          |
+------------------+--------------------------+
        40%                    60%
```

**Interactions:**
- Email validation on blur
- Password visibility toggle
- Enter key submits form
- "Sign up" link navigates to `/register`
- "Forgot password" opens reset modal

---

### 1.2 Register Screen
**Route:** `/register`

**Layout:** Same split layout as login

**Fields:**
- Display Name (text, 2-100 chars)
- Email (email validation)
- Password (strength indicator required)
- Confirm Password (must match)

**Password Strength Rules:**
- Weak: <8 chars or no complexity
- Medium: 8+ chars, 2 of (upper, lower, number, special)
- Strong: 10+ chars, 3+ of above

---

## 2. Dashboard Screen

**Route:** `/dashboard`

**Layout:**
```
+--------------------------------------------------+
| [Logo]    Dashboard    [Search...]    [Profile ▼] |
+--------------------------------------------------+
|                                                  |
|  My Projects                           [+ New ▼] |
|  ─────────────────────────────────────────────  |
|                                                  |
|  +----------------+  +----------------+         |
|  | [Preview Img]  |  | [Preview Img]  |         |
|  |                |  |                |         |
|  +----------------+  +----------------+         |
|  Project Name        Another Project            |
|  4 scenes • 2h ago   2 scenes • 1d ago          |
|  [⋯]                 [⋯]                        |
|                                                  |
|  +----------------+                             |
|  |    [+]         |                             |
|  |  Create New    |                             |
|  |   Project      |                             |
|  +----------------+                             |
|                                                  |
+--------------------------------------------------+
|  [Home]  [Templates]  [Trash]  [Settings]         |
+--------------------------------------------------+
```

**Components:**

**Header:**
- Logo (left, 32px height)
- Page title "Dashboard"
- Search bar (center, 300px width, placeholder: "Search projects...")
- Profile dropdown (avatar + name, right-aligned)

**Project Card:**
- Thumbnail (16:9 aspect, rounded-lg)
- Project name (font-semibold, truncate)
- Metadata (scenes count • relative time)
- Kebab menu (⋯) with: Rename, Duplicate, Delete
- Hover: subtle shadow, scale(1.02)

**New Project Button:**
- Primary CTA with dropdown
- Options: "Blank Project", "From Template", "Generate with AI"

**Empty State:**
- Centered illustration
- "No projects yet"
- "Create your first scene" CTA button

---

## 3. Scene Editor

**Route:** `/projects/{project_id}/scenes/{scene_id}`

**Layout:**
```
+--------------------------------------------------+
| [←] Project Name    Scene: [Scene Dropdown ▼]  [Export ▼]  [Save] |
+--------------------------------------------------+
|                                                  |
|  +-----------+  +----------------------------+  +-----------+  |
|  |  TOOLBAR  |  |                            |  | PROPERTIES |  |
|  |           |  |                            |  |            |  |
|  | [Elements]|  |      CANVAS (1920x1080)    |  | [Position] |  |
|  |  +----+   |  |                            |  | [Size]     |  |
|  |  | 🎥 |   |  |    +------------------+    |  | [Style]    |  |
|  |  |Web |   |  |    | [Element]        |    |  |            |  |
|  |  +----+   |  |    |                  |    |  |            |  |
|  |           |  |    +------------------+    |  |            |  |
|  | +------+  |  |                            |  |            |  |
|  | |Layers|  |  |    +------------------+     |  |            |  |
|  |  ───────  |  |    | [Element]        |     |  |            |  |
|  |  1. 🎥    |  |    +------------------+     |  |            |  |
|  |  2. 💬    |  |                            |  |            |  |
|  |  3. 📝    |  |                            |  |            |  |
|  +-----------+  +----------------------------+  +-----------+  |
|                                                  |
+--------------------------------------------------+
```

**Dimensions:**
- Left sidebar: 280px fixed
- Right sidebar: 320px fixed
- Canvas: Center, 1920x1080 (scaled to fit viewport)
- Min canvas zoom: 25%, Max: 200%

### 3.1 Left Sidebar - Elements Panel

**Tabs:**
- Elements (default)
- Layers

**Elements Tab:**
```
Elements
────────
[Search elements...]

Basic
┌──────────┐ ┌──────────┐
│   🎥     │ │   💬     │
│ Webcam   │ │  Chat    │
└──────────┘ └──────────┘
┌──────────┐ ┌──────────┐
│   🔔     │ │   📝     │
│  Alert   │ │  Text    │
└──────────┘ └──────────┘

Media
┌──────────┐ ┌──────────┐
│   🖼️     │ │   ⬜     │
│  Image   │ │  Panel   │
└──────────┘ └──────────┘
```

- 2-column grid of element types
- Click to add to canvas (center position)
- Drag to canvas for direct placement

**Layers Tab:**
- Reverse-ordered list (top layer at top)
- Drag to reorder (updates z-index)
- Eye icon to toggle visibility
- Lock icon to prevent editing
- Click to select element on canvas

### 3.2 Center - Canvas

**Canvas Container:**
- Gray checkerboard pattern for transparency
- Centered in available space
- Zoom controls (bottom-right of canvas):
  - [-] [50%] [+] buttons
  - Fit to screen button
  - Reset zoom button

**Canvas Background:**
- Solid color (default: #1a1a1a)
- Or: Transparent with checkerboard

**Element Selection:**
- Click to select (blue border, 8 resize handles)
- Shift+click for multi-select
- Drag to move
- Arrow keys for nudge (1px), Shift+arrow (10px)
- Delete key removes selected

**Resize Handles:**
- 8 handles: 4 corners, 4 edges
- Corner: free resize (maintains aspect ratio with Shift)
- Edge: resize single dimension
- Min size: 20x20px

**Context Menu (Right-click on element):**
- Cut / Copy / Paste
- Duplicate
- Delete
- Arrange → Send to Back / Bring to Front
- Align → Left / Center / Right / Top / Middle / Bottom

### 3.3 Right Sidebar - Properties Panel

**Header:**
- Element name (editable)
- Element type icon
- Visibility toggle
- Lock toggle

**Position Section:**
```
Position
X: [_____] px    Y: [_____] px
```

**Size Section:**
```
Size
W: [_____] px    H: [_____] px
[ ] Lock aspect ratio
```

**Style Section (varies by element type):**

**Webcam:**
- Border radius: [0-50] slider
- Border width: [0-10] number
- Border color: [color picker]
- Background: [color picker]

**Text:**
- Content: [textarea]
- Font: [dropdown]
- Size: [8-128] number
- Weight: [dropdown: normal, bold, etc.]
- Color: [color picker]
- Align: [left|center|right buttons]
- Transform: [none|uppercase|lowercase]

**All Elements:**
- Opacity: [0-100] slider
- Rotation: [-360 to 360] number

**Layers Section:**
- z-index: [number]
- Send to Back / Bring to Front buttons

---

## 4. Template Library Modal

**Trigger:** "New Project → From Template" or "Templates" nav item

**Modal Layout:**
```
+--------------------------------------------------+
| Choose a Template                           [✕]  |
+--------------------------------------------------+
| [All ▼] [Gaming ▼] [Search templates...]         |
+--------------------------------------------------+
|                                                  |
|  Scene Packs              Single Scenes          |
|  ══════════════════════════════════════════════  |
|                                                  |
|  +------------------+  +------------------+      |
|  | [Preview]        |  | [Preview]        |      |
|  |                  |  |                  |      |
|  +------------------+  +------------------+      |
|  Cyberpunk Gaming      Minimal Dark              |
|  4 scenes              Just Chatting layout      |
|  [Use Pack]            [Use Scene]               |
|                                                  |
|  +------------------+                            |
|  | [Preview]        |                            |
|  |                  |                            |
|  +------------------+                            |
|  Cozy Stream                                       |
|  4 scenes                                          |
|  [Use Pack]                                        |
|                                                  |
+--------------------------------------------------+
```

**Filters:**
- Type: All, Scene Packs, Single Scenes
- Category: Gaming, Just Chatting, Creative, Music, IRL
- Search: text input

**Template Card:**
- Preview image (16:9)
- Template name
- Description (2 lines max)
- Metadata (scene count or type)
- CTA button

**Preview Modal:**
- Larger preview image
- Full description
- Scene list (for packs)
- Theme preview
- "Use Template" / "Cancel" buttons

---

## 5. AI Generation Modal

**Trigger:** "New Project → Generate with AI" or "AI Generate" button

**Modal Layout:**
```
+--------------------------------------------------+
| Generate Scene with AI                      [✕]  |
+--------------------------------------------------+
|                                                  |
|  Describe your ideal stream layout:              |
|                                                  |
|  +--------------------------------------------+  |
|  | "Create a futuristic gaming setup with     |  |
|  |  neon accents, webcam bottom right, chat   |  |
|  |  top left, and a central gameplay area"    |  |
|  +--------------------------------------------+  |
|  [0/500 characters]                              |
|                                                  |
|  Style (optional):                               |
|  [Futuristic ▼]                                  |
|  Options: Minimal, Futuristic, Cozy,               |
|           Professional, Vibrant, Retro         |
|                                                  |
|  Canvas Size: [1920x1080 ▼]                    |
|  Options: 1920x1080, 1280x720, Custom             |
|                                                  |
|  [      Generate Scene      ]                    |
|                                                  |
+--------------------------------------------------+
```

**Loading State:**
```
+--------------------------------------------------+
|                                                  |
|           ⏳ Generating...                       |
|                                                  |
|     Creating your custom layout                  |
|     This takes about 5-10 seconds                |
|                                                  |
|           [Cancel]                               |
|                                                  |
+--------------------------------------------------+
```

**Result Preview:**
- Generated scene preview (rendered)
- "Looks great!" / "Try again" buttons
- "Edit in Studio" to open in editor

---

## 6. Export Modal

**Trigger:** "Export" button in editor

**Modal Layout:**
```
+--------------------------------------------------+
| Export Scene                              [✕]    |
+--------------------------------------------------+
|                                                  |
|  Export as:                                      |
|                                                  |
|  [📷 PNG Image]    [📄 JSON]                     |
|                                                  |
|  ─────────────────────────────────────────────  |
|                                                  |
|  PNG Options:                                    |
|  Scale: [1x ▼] (0.5x, 1x, 2x, 4x)               |
|  [ ] Transparent background                      |
|                                                  |
|  [        Download PNG        ]                  |
|                                                  |
|  ─────────────────────────────────────────────  |
|                                                  |
|  Use in OBS Studio:                             |
|  1. Download JSON file                          |
|  2. In OBS: Scene → Import → Select JSON         |
|                                                  |
+--------------------------------------------------+
```

---

## 7. Component Specifications

### 7.1 Buttons

**Primary Button:**
- Background: `bg-indigo-600`
- Hover: `bg-indigo-700`
- Text: white, font-medium
- Padding: px-4 py-2
- Border-radius: rounded-lg
- Shadow: shadow-sm

**Secondary Button:**
- Background: white
- Border: border-gray-300
- Text: gray-700
- Hover: bg-gray-50

**Icon Button:**
- Size: 40x40px
- Border-radius: rounded-lg
- Hover: bg-gray-100

### 7.2 Cards

**Project Card:**
- Background: white
- Border-radius: rounded-xl
- Shadow: shadow-sm
- Hover: shadow-md, scale(1.02)
- Transition: all 200ms ease

**Element Card (toolbar):**
- Size: 120x100px
- Border: 1px solid gray-200
- Border-radius: rounded-lg
- Hover: border-indigo-500, bg-indigo-50

### 7.3 Inputs

**Text Input:**
- Border: border-gray-300
- Border-radius: rounded-md
- Focus: ring-2 ring-indigo-500 border-indigo-500
- Padding: px-3 py-2

**Color Picker:**
- Trigger: colored circle (24px) + hex input
- Popover: color spectrum + hex input

**Slider:**
- Track height: 4px
- Thumb: 16px circle
- Active: indigo-600

---

## 8. Responsive Behavior

**Desktop (1280px+):**
- Full 3-column layout
- Both sidebars visible

**Tablet (768px - 1279px):**
- Collapse right sidebar to tab/drawer
- Canvas zoom adjusts

**Mobile (< 768px):**
- Not supported for editor
- Show message: "Studio requires desktop"
- Dashboard remains functional

---

## Version History

- v1.0 (2026-03-26): Initial wireframe specifications
