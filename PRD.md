# AI Stream Scene Builder
## Product Requirements Document (PRD)
### Version 5.2 - Production Ready
**Date:** March 26, 2026  
**Product Owner:** Catarina Calabrese

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision](#3-product-vision)
4. [Product Goals](#4-product-goals)
5. [Scope](#5-scope)
6. [User Roles](#6-user-roles)
7. [Core Product Model](#7-core-product-model)
8. [Core Features](#8-core-features)
9. [Functional Requirements](#9-functional-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [User Flows](#11-user-flows)
12. [Edge Cases](#12-edge-cases)
13. [Risks](#13-risks)
14. [Technical Architecture](#14-technical-architecture)
15. [MVP Definition](#15-mvp-definition)
16. [Future Enhancements](#16-future-enhancements)
17. [Database Schema](#17-database-schema)
18. [API Specification](#18-api-specification)
19. [Wireframes](#19-wireframes)
20. [UI Component Specifications](#20-ui-component-specifications)
21. [AI Prompt Specifications](#21-ai-prompt-specifications)

---

## 1. Executive Summary

AI Stream Scene Builder is a web-based design platform that enables streamers to create professional streaming layouts through three flexible workflows:

- **Manual design** (drag-and-drop editor)
- **Template-based design** (themes, overlays, and scene packs)
- **AI-powered generation** (prompt → full scene or scene pack)

The platform simplifies the creation of stream overlays and scenes by combining intuitive design tools with AI assistance, allowing users to quickly produce and customize layouts for use in streaming software such as OBS Studio.

---

## 2. Problem Statement

Streamers face several challenges when creating stream layouts:

- **Lack of design experience** - Many streamers aren't graphic designers
- **Complex configuration in tools like OBS Studio** - Steep learning curve
- **Dependence on expensive pre-made overlay packs** - $50-200 per pack
- **Time-consuming manual setup** - Hours to configure scenes

These issues result in inconsistent branding, inefficient workflows, and reduced production quality.

---

## 3. Product Vision

To become the easiest and fastest way for streamers to design, customize, and manage professional stream scenes without requiring advanced design skills.

---

## 4. Product Goals

### 4.1 Business Goals
- Deliver a scalable SaaS product for creators
- Reduce time-to-create for stream scenes from hours to minutes
- Enable long-term expansion into marketplace and integrations

### 4.2 User Goals

Users want to:

- Quickly generate high-quality stream scenes
- Customize layouts easily
- Maintain consistent branding
- Avoid complex design tools

### 4.3 Success Metrics (KPIs)

| Metric | Target |
|--------|--------|
| Time to first scene created | < 5 minutes |
| Average scenes created per user | > 3 |
| AI usage rate | > 30% of scenes |
| Template usage rate | > 40% of scenes |
| Export success rate | > 95% |
| Weekly active users | Growth 10% week-over-week |

---

## 5. Scope

### 5.1 In Scope (MVP)

- User authentication (email/password, JWT-based)
- Project dashboard (create, view, rename, duplicate, delete)
- Scene editor (drag-and-drop, 1920x1080 canvas)
- Element library (webcam, chat, alert, text, image, panel)
- Template library (themes, overlays, scene packs)
- Theme system (color palette, fonts, global styles)
- AI scene generation (prompt → structured layout)
- Save/load functionality with autosave (30s interval)
- Export (PNG + JSON for OBS Studio)

### 5.2 Out of Scope (MVP)

- Live streaming integration
- Direct API integrations (Twitch, YouTube)
- Real-time alerts/chat widgets
- Payment/subscription system
- Mobile applications
- Template marketplace
- Animation/transition effects
- Audio visualization elements

---

## 6. User Roles

### 6.1 Primary User: Streamer
- Create and manage projects
- Generate scenes (AI/templates/manual)
- Customize layouts via drag-and-drop
- Export scenes for OBS Studio

### 6.2 Platform Admin
- Monitor system usage and analytics
- Manage user accounts
- Handle support issues
- Manage system templates and themes

---

## 7. Core Product Model

### 7.1 Entities

**User**
- id: UUID, primary key
- email: VARCHAR(255), unique
- hashed_password: VARCHAR(255)
- display_name: VARCHAR(100)
- is_active: BOOLEAN
- created_at, updated_at: TIMESTAMP

**Project**
- id: UUID, primary key
- user_id: UUID, foreign key → users
- name: VARCHAR(200)
- description: TEXT, optional
- is_active: BOOLEAN (soft delete)
- created_at, updated_at: TIMESTAMP

**Scene**
- id: UUID, primary key
- project_id: UUID, foreign key → projects
- name: VARCHAR(200)
- scene_type: ENUM (starting_soon, live, brb, ending, custom)
- canvas_width: INTEGER (default 1920)
- canvas_height: INTEGER (default 1080)
- background_color: VARCHAR(7) hex
- theme_id: UUID, foreign key → themes, optional
- layout_data: JSONB (element positions and properties)
- thumbnail_url: VARCHAR(500), optional
- is_active: BOOLEAN
- created_at, updated_at: TIMESTAMP

**Element**
- id: UUID, primary key
- scene_id: UUID, foreign key → scenes
- element_type: ENUM (webcam, chat, alert, text, image, panel)
- name: VARCHAR(200)
- position_x, position_y: INTEGER
- width, height: INTEGER
- z_index: INTEGER (layer order)
- properties: JSONB (type-specific styling)
- is_visible: BOOLEAN
- created_at, updated_at: TIMESTAMP

**Theme**
- id: UUID, primary key
- name: VARCHAR(200)
- is_system: BOOLEAN (built-in vs user-created)
- user_id: UUID, foreign key → users, nullable
- color_primary, color_secondary, color_background, color_surface, color_text, color_text_muted: VARCHAR(7)
- font_heading, font_body: VARCHAR(100)
- properties: JSONB
- created_at, updated_at: TIMESTAMP

**Template**
- id: UUID, primary key
- name: VARCHAR(200)
- description: TEXT
- template_type: ENUM (single_scene, scene_pack)
- category: VARCHAR(100) (gaming, just_chatting, creative, music, irl)
- is_system: BOOLEAN
- user_id: UUID, foreign key → users, nullable
- thumbnail_url: VARCHAR(500)
- preview_data: JSONB
- theme_id: UUID, foreign key → themes
- created_at, updated_at: TIMESTAMP

### 7.2 Relationships

```
users ||--o{ projects : owns
users ||--o{ themes : creates
users ||--o{ templates : creates
users ||--o{ ai_generations : requests

projects ||--o{ scenes : contains
projects }o--|| themes : uses

scenes }o--|| themes : applies
scenes ||--o{ elements : contains

templates ||--o{ template_scenes : includes
templates }o--|| themes : uses
```

---

## 8. Core Features

### 8.1 Authentication

**Requirements**
- Email/password signup with validation
- Login/logout with JWT tokens
- Password reset via email
- Refresh token rotation

**Acceptance Criteria**
- Users can securely access their projects
- Tokens expire after 1 hour (access), 7 days (refresh)
- Password requirements: 8+ chars, 1 uppercase, 1 lowercase, 1 number

### 8.2 Project Dashboard

**Requirements**
- Create new project (blank, from template, or AI-generated)
- View projects in grid layout with thumbnails
- Rename, duplicate, delete projects
- Search projects by name

**Acceptance Criteria**
- Projects persist across sessions
- Users can quickly access existing work
- Dashboard loads in < 3 seconds

### 8.3 Scene Editor (Canva-Style)

**Requirements**
- Fixed 1920x1080 canvas with zoom controls (25% - 200%)
- Drag-and-drop element positioning
- 8-direction resize handles
- Layer ordering with z-index
- Selection with multi-select (Shift+click)
- Properties panel for editing

**Acceptance Criteria**
- Smooth drag interactions (60fps)
- Accurate element positioning (1px precision)
- Edits persist after saving
- Keyboard shortcuts: Delete (remove), Arrows (nudge)

### 8.4 Element Library

**Supported Elements (MVP)**

| Element | Default Size | Key Properties |
|---------|--------------|----------------|
| Webcam | 320x180 | border_radius, border_width, border_color |
| Chat | 400x450 | font_family, font_size, text_color, background_color |
| Alert | 400x150 | animation_type, duration_seconds |
| Text | Variable | content, font_family, font_size, font_weight, text_align |
| Image | Variable | src, object_fit, border_radius |
| Panel | Variable | background_color, border_radius, opacity |

**Acceptance Criteria**
- Users can add/remove elements
- Elements are fully customizable
- Drag from library to canvas

### 8.5 Template Library

**Types**
- Single scenes (one layout)
- Scene packs (Starting Soon, Live, BRB, Ending bundle)

**Categories**
- Gaming
- Just Chatting
- Creative
- Music
- IRL

**Acceptance Criteria**
- Templates are browsable and previewable
- Templates load into editor
- Fully editable after selection

### 8.6 Theme System

**Components**
- Color palette (primary, secondary, background, surface, text, text_muted)
- Font families (heading, body)
- Styling defaults (border radius, spacing)

**Acceptance Criteria**
- Themes apply globally to scenes
- Users can override individual element styles
- Built-in themes available (Minimal, Cyberpunk, Cozy, Professional)

### 8.7 Scene Packs

**Standard Pack**
- Starting Soon (countdown/timer prominent)
- Live (balanced layout)
- BRB (centered message, minimal)
- Ending (thank you, social links)

**Acceptance Criteria**
- Packs create multi-scene projects
- Consistent design across scenes
- Each scene fully customizable

### 8.8 AI Scene Generation

**Description**
Users generate scenes using natural language prompts.

**Inputs**
- Prompt (required, max 500 chars)
- Style hint (optional: minimal, futuristic, cozy, professional, vibrant, retro)
- Canvas size (optional: 1920x1080 default)

**Output Format**
```json
{
  "name": "Scene name",
  "scene_type": "live",
  "background_color": "#1a1a1a",
  "theme": {
    "name": "Theme name",
    "color_primary": "#00f5ff",
    "color_secondary": "#ff006e",
    "color_background": "#0a0a0f",
    "color_surface": "#1a1a24",
    "color_text": "#ffffff",
    "color_text_muted": "#8a8a9a",
    "font_heading": "Orbitron",
    "font_body": "Inter"
  },
  "layout": {
    "version": "1.0",
    "elements": [
      {
        "type": "webcam",
        "x": 50,
        "y": 800,
        "width": 320,
        "height": 180,
        "z_index": 1,
        "properties": {
          "border_radius": 8,
          "border_width": 2,
          "border_color": "#00f5ff"
        }
      }
    ]
  }
}
```

**Acceptance Criteria**
- Generated scene loads in editor
- Fully editable
- Regeneration supported
- Processing time < 10 seconds

### 8.9 Save & Autosave

**Requirements**
- Manual save (Ctrl+S)
- Autosave every 30 seconds when changes detected
- Save status indicator (Saving... / Saved / Unsaved changes)

**Acceptance Criteria**
- No data loss on refresh
- Save confirmation visible
- Concurrent edit detection (last-write-wins)

### 8.10 Export

**Formats**
- **PNG**: Screenshot of canvas at 1x, 2x, or custom scale
- **JSON**: OBS Studio-compatible scene configuration

**PNG Export Options**
- Scale: 0.5x, 1x, 2x, 4x
- Transparent background toggle

**JSON Export Schema (OBS-compatible)**
```json
{
  "streambuldr_version": "1.0",
  "name": "Live",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "background_color": "#1a1a1a"
  },
  "elements": [
    {
      "id": "webcam-1",
      "type": "video_capture",
      "name": "Webcam",
      "pos": {"x": 50, "y": 50},
      "size": {"width": 320, "height": 180},
      "visible": true,
      "streambuldr_meta": {
        "border_radius": 8,
        "border_color": "#ffffff"
      }
    }
  ]
}
```

**Acceptance Criteria**
- Accurate layout export
- Download completes successfully
- PNG matches canvas visual exactly

---

## 9. Functional Requirements

1. **Multi-project support** - Users can create unlimited projects
2. **Layout data storage** - All element positions, sizes, and properties persisted
3. **Asset validation** - Uploaded images validated (format, size, dimensions)
4. **Layout validation** - Prevent off-canvas elements, enforce minimum sizes
5. **Undo/Redo** - Minimum 20-step history in editor
6. **Copy/Paste** - Elements can be copied between scenes
7. **Keyboard shortcuts** - Standard shortcuts (Ctrl+S, Ctrl+Z, Delete, arrows)

---

## 10. Non-Functional Requirements

### 10.1 Performance

| Metric | Requirement |
|--------|-------------|
| Dashboard load | < 3 seconds |
| Editor load | < 5 seconds |
| Drag interaction | 60fps, < 16ms frame time |
| Save operation | < 2 seconds |
| AI generation | < 10 seconds (95th percentile) |

### 10.2 Reliability

- **Availability**: 99.5% uptime (excluding planned maintenance)
- **Autosave**: Must prevent data loss in 99.9% of cases
- **No corrupted layouts**: Validation prevents invalid states

### 10.3 Security

- **Authentication**: JWT with secure rotation
- **Passwords**: bcrypt with salt rounds 12
- **Uploads**: File type validation, size limits (5MB max)
- **HTTPS**: All traffic encrypted
- **CORS**: Restricted to approved origins

### 10.4 Usability

- **Beginner-friendly**: No design experience required
- **Minimal learning curve**: < 10 minutes to first scene
- **Accessibility**: WCAG 2.1 AA compliance
- **Responsive**: Dashboard usable on tablet, Editor requires 1280px+

---

## 11. User Flows

### 11.1 AI Flow
```
User clicks "Generate with AI"
    ↓
Enter prompt + optional style
    ↓
Scene is generated (5-10s)
    ↓
Preview generated layout
    ↓
User edits in studio
    ↓
Save/export
```

### 11.2 Template Flow
```
Select template from library
    ↓
Preview template
    ↓
Apply to new or existing project
    ↓
Edit in studio
    ↓
Save/export
```

### 11.3 Manual Flow
```
Start blank project
    ↓
Add elements from library
    ↓
Drag to position, resize
    ↓
Customize styles
    ↓
Save/export
```

---

## 12. Edge Cases

| Case | Handling |
|------|----------|
| AI generates overlapping elements | Auto-correct with 10px nudge, or flag for user review |
| Invalid prompts (too vague) | Suggest more specific description with examples |
| Upload failures | Retry 3x, then show error with manual retry option |
| Autosave interruption | Queue save, retry on reconnect, show warning |
| Empty export attempt | Show error: "Add at least one element to export" |
| Concurrent edit conflict | Last-write-wins with conflict notification |
| Browser crash during edit | Recover from autosave on reload |
| Large canvas with many elements | Virtual rendering for > 50 elements |

---

## 13. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Drag-and-drop complexity | Medium | High | Use @dnd-kit library, extensive testing |
| AI inconsistency | Medium | Medium | Structured output, validation, retry logic |
| Export mismatches | Low | High | Pixel-perfect rendering with canvas API |
| Scope creep | High | Medium | Strict MVP definition, feature freeze |
| Performance with large scenes | Medium | Medium | Virtualization, lazy loading |
| Browser compatibility | Low | Medium | Test on Chrome, Firefox, Safari, Edge |

---

## 14. Technical Architecture

### 14.1 High-Level Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Tailwind CSS |
| State Management | Zustand (client), TanStack Query (server) |
| Drag & Drop | @dnd-kit/core |
| Canvas Export | html2canvas |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLModel |
| Migrations | Alembic |
| Auth | JWT (python-jose) |
| AI | OpenAI GPT-4 (primary), Claude (fallback) |
| File Storage | AWS S3 (staging: local) |
| Export Processing | Celery + Redis (async jobs) |

### 14.2 API Architecture

- **RESTful API** with JSON payloads
- **OpenAPI/Swagger** documentation auto-generated
- **Versioning**: URL-based (/v1/...)
- **Rate limiting**: Per-user and per-IP
- **Error format**: Standardized JSON with code, message, details

### 14.3 AI Integration Architecture

```
User Request
    ↓
[POST /ai/generate-scene]
    ↓
Validation & Rate Check
    ↓
Queue Job (Celery)
    ↓
GPT-4 API Call
    ↓
JSON Schema Validation
    ↓
Auto-Correction (if needed)
    ↓
Store Result
    ↓
WebSocket/Polling Response
```

---

## 15. MVP Definition

The MVP is complete when a user can:

- [ ] Create an account and log in
- [ ] Create a new project (blank, template, or AI-generated)
- [ ] View and manage projects on dashboard
- [ ] Open scene editor with 1920x1080 canvas
- [ ] Add, move, resize, and style elements
- [ ] Save work manually and via autosave
- [ ] Export scene as PNG and JSON
- [ ] Use at least 5 built-in templates
- [ ] Apply 3 different themes

---

## 16. Future Enhancements

### Phase 2 (Post-MVP)
- [ ] OBS Studio plugin for direct import
- [ ] Platform integrations (Twitch, YouTube Studio)
- [ ] Animation support (CSS animations, transitions)
- [ ] Audio visualizer elements
- [ ] Custom CSS input for advanced users

### Phase 3
- [ ] Template marketplace (buy/sell)
- [ ] Subscription tiers (Free, Pro, Studio)
- [ ] Collaboration (multi-user editing)
- [ ] Version history with branching
- [ ] Mobile companion app

### Phase 4
- [ ] Real-time stream data widgets (alerts, chat, stats)
- [ ] Video background support
- [ ] 3D elements and WebGL effects
- [ ] AI video generation for backgrounds
- [ ] Browser source widget hosting

---

## 17. Database Schema

### 17.1 Complete Table Definitions

See detailed schema in: `docs/database-schema.md`

### 17.2 Key Tables Summary

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| users | User accounts | id, email, hashed_password, display_name |
| projects | Project containers | id, user_id, name, description |
| scenes | Individual layouts | id, project_id, name, layout_data (JSONB) |
| elements | Scene components | id, scene_id, type, x, y, width, height, z_index |
| themes | Visual styles | id, colors (6x hex), fonts (2x) |
| templates | Pre-built layouts | id, type, category, preview_data |
| ai_generations | AI request log | id, user_id, prompt, result, status |

### 17.3 Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_scenes_project_id ON scenes(project_id);
CREATE INDEX idx_elements_scene_id ON elements(scene_id);
CREATE INDEX idx_elements_z_index ON elements(z_index);
CREATE INDEX idx_themes_is_system ON themes(is_system);
CREATE INDEX idx_ai_generations_user_id ON ai_generations(user_id);
```

---

## 18. API Specification

### 18.1 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Authenticate |
| POST | /auth/refresh | Rotate tokens |
| POST | /auth/logout | Revoke token |
| POST | /auth/forgot-password | Request reset |
| POST | /auth/reset-password | Complete reset |

### 18.2 Project Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /projects | List user projects |
| POST | /projects | Create project |
| GET | /projects/{id} | Get project + scenes |
| PUT | /projects/{id} | Update project |
| DELETE | /projects/{id} | Delete project |
| POST | /projects/{id}/duplicate | Clone project |

### 18.3 Scene Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /projects/{id}/scenes | List scenes |
| POST | /projects/{id}/scenes | Create scene |
| GET | /scenes/{id} | Get full scene |
| PUT | /scenes/{id} | Update scene |
| PATCH | /scenes/{id} | Partial update |
| DELETE | /scenes/{id} | Delete scene |
| POST | /scenes/{id}/duplicate | Clone scene |

### 18.4 Element Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /scenes/{id}/elements | List elements |
| POST | /scenes/{id}/elements | Add element |
| PUT | /elements/{id} | Update element |
| DELETE | /elements/{id} | Remove element |
| POST | /scenes/{id}/elements/reorder | Update z-index |

### 18.5 Template & Theme Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /templates | Browse templates |
| GET | /templates/{id} | Get template |
| GET | /themes | List themes |
| GET | /themes/{id} | Get theme |
| POST | /themes | Create custom theme |

### 18.6 AI Generation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ai/generate-scene | Start generation |
| GET | /ai/generations/{id} | Check status/result |

### 18.7 Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /scenes/{id}/export/png | Export as PNG |
| POST | /scenes/{id}/export/json | Export as JSON |

See complete API specs in: `docs/api-specification.md`

---

## 19. Wireframes

### 19.1 Screen Inventory

1. **Auth Screens**: Login, Register, Forgot Password, Reset Password
2. **Dashboard**: Project grid, empty state, search
3. **Editor**: 3-column layout (toolbar, canvas, properties)
4. **Modals**: AI Generation, Template Library, Export, Settings

### 19.2 Login Screen Layout

```
+------------------+--------------------------+
|                  |                          |
|   [Logo]         |     Welcome Back         |
|                  |                          |
|   [Hero Image]   |     Email                |
|                  |     [________________]   |
|                  |                          |
|                  |     Password             |
|                  |     [________________]   |
|                  |     [ ] Remember me      |
|                  |                          |
|                  |     [   Sign In   ]      |
|                  |                          |
|                  |     Forgot password?     |
|                  |     [ Sign up ]          |
+------------------+--------------------------+
```

### 19.3 Dashboard Layout

```
+--------------------------------------------------+
| [Logo]    Dashboard    [Search...]    [Profile ▼] |
+--------------------------------------------------+
|                                                  |
|  My Projects                           [+ New ▼] |
|  ─────────────────────────────────────────────  |
|  +----------------+  +----------------+         |
|  | [Preview]      |  | [Preview]      |         |
|  +----------------+  +----------------+         |
|  Project Name        Another Project            |
|  4 scenes • 2h ago   2 scenes • 1d ago          |
|                                                  |
+--------------------------------------------------+
```

### 19.4 Editor Layout

```
+--------------------------------------------------+
| [←] Project    Scene: [▼]    [Export ▼]  [Save]  |
+--------------------------------------------------+
|  +-----------+  +----------------------------+  +-----------+  |
|  | TOOLBAR   |  |                            |  | PROPERTIES|  |
|  | [Elements]|  |      CANVAS (1920x1080)    |  | [Position] |  |
|  |  +----+   |  |                            |  | [Size]     |  |
|  |  | 🎥 |   |  |    +------------------+    |  | [Style]    |  |
|  |  |Web |   |  |    | [Element]        |    |  |            |  |
|  |  +----+   |  |    +------------------+    |  |            |  |
|  |           |  |                            |  |            |  |
|  | +------+  |  |                            |  |            |  |
|  | |Layers|  |  |                            |  |            |  |
|  +-----------+  +----------------------------+  +-----------+  |
+--------------------------------------------------+
```

See complete wireframes in: `docs/wireframes.md`

---

## 20. UI Component Specifications

### 20.1 Design Tokens

**Colors:**
- Primary: #4f46e5 (indigo-600)
- Success: #22c55e
- Warning: #f59e0b
- Error: #ef4444
- Canvas: #1a1a1a
- Selection: #4f46e5

**Typography:**
- Font: Inter, system-ui, sans-serif
- Base: 16px / 24px line-height
- Scale: xs (12px) → 6xl (60px)

**Spacing:**
- Base unit: 4px
- Scale: 0.5 (2px) → 24 (96px)

### 20.2 Key Components

**Primary Button:**
```tsx
<button className="
  px-4 py-2 bg-indigo-600 hover:bg-indigo-700
  text-white font-medium text-sm rounded-lg
  shadow-sm transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-indigo-500
">
```

**Canvas Element (Selected):**
```tsx
<div className="
  absolute border-2 border-indigo-500 bg-indigo-500/10
">
  {/* 8 resize handles */}
  <div className="absolute -top-1.5 -left-1.5 w-3 h-3 
    bg-white border border-indigo-500 cursor-nw-resize" />
  {/* ... 7 more handles ... */}
</div>
```

See complete component specs in: `docs/ui-component-specs.md`

---

## 21. AI Prompt Specifications

### 21.1 System Prompt

```
You are an expert streaming scene designer. Generate professional 
OBS/streaming layouts based on user descriptions.

RULES:
1. Always return valid JSON matching the SceneLayout schema
2. Ensure all elements within canvas bounds (0 to width/height)
3. Minimize element overlap (10px spacing)
4. Use appropriate defaults per element type
5. Apply requested style through colors, fonts, spacing
6. Use logical positioning (webcam corner, chat side, gameplay center)
7. All colors must be valid hex (#RRGGBB)
8. Font families: "Inter", "Poppins", "Orbitron", "Roboto"

STYLES:
- minimal: Clean, whitespace, monochrome
- futuristic: Neon (#00f5ff, #ff00ff), dark, sharp
- cozy: Warm (#ffaa00), rounded, soft
- professional: Blues (#0066ff), grays, structured
- vibrant: High contrast, bold
- retro: Pixel fonts, scanlines, 90s aesthetic
```

### 21.2 AI Configuration

**Primary Provider:** OpenAI GPT-4-turbo-preview
- Temperature: 0.7
- Max tokens: 2000
- Response format: JSON object
- Timeout: 30s

**Fallback Provider:** Claude 3 Opus

### 21.3 Validation Rules

- Position bounds: `0 <= x <= canvas_width - width`
- Overlap detection: 10px minimum spacing
- Color validation: Regex `^#[0-9A-Fa-f]{6}$`
- Auto-correction: Clamp off-canvas, default missing properties

See complete AI specs in: `docs/ai-prompt-specs.md`

---

## Appendix: Document References

| Document | Path | Contents |
|----------|------|----------|
| Database Schema | `docs/database-schema.md` | Full SQL schema, SQLModel classes |
| API Specification | `docs/api-specification.md` | Complete API reference |
| Wireframes | `docs/wireframes.md` | Screen layouts and interactions |
| UI Components | `docs/ui-component-specs.md` | Design system, Tailwind classes |
| AI Prompts | `docs/ai-prompt-specs.md` | System prompts, validation |

---

## PRD Completeness Checklist

| Component | Status |
|-----------|--------|
| Executive Summary | ✅ |
| Problem Statement | ✅ |
| Product Vision | ✅ |
| Product Goals & KPIs | ✅ |
| Scope (In/Out) | ✅ |
| User Roles | ✅ |
| Product Model (ERD) | ✅ |
| Core Features (8) | ✅ |
| Functional Requirements | ✅ |
| Non-Functional Requirements | ✅ |
| User Flows | ✅ |
| Edge Cases | ✅ |
| Risks & Mitigation | ✅ |
| Technical Architecture | ✅ |
| MVP Definition | ✅ |
| Future Enhancements | ✅ |
| Database Schema | ✅ |
| API Specification | ✅ |
| Wireframes | ✅ |
| UI Component Specs | ✅ |
| AI Prompt Specs | ✅ |

**PRD Status: 95% Production Ready**

The only remaining items for 100% would be:
- Figma/FigJam high-fidelity mockups
- Detailed QA test cases
- Deployment runbooks

---

*End of Document*
