# API Endpoints Specification - AI Stream Scene Builder

Base URL: `https://api.streambuldr.com/v1`

---

## Authentication

All endpoints except `/auth/*` require JWT Bearer token in Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "display_name": "StreamerPro"
}
```

**Validation:**
- `email`: Valid email format, unique
- `password`: 8-100 chars, 1 uppercase, 1 lowercase, 1 number
- `display_name`: 2-100 chars

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "StreamerPro",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors:**
- `400`: Validation error (invalid email, weak password)
- `409`: Email already registered

---

#### POST /auth/login
Authenticate existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "StreamerPro",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401`: Invalid credentials

---

#### POST /auth/refresh
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401`: Invalid or expired refresh token

---

#### POST /auth/logout
Revoke current refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 204:** No content

---

#### POST /auth/forgot-password
Request password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response 202:** Accepted (always returns 202 even if email doesn't exist for security)

---

#### POST /auth/reset-password
Reset password using token from email.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

**Response 200:** Password reset successful

**Errors:**
- `400`: Invalid or expired token
- `400`: Weak password

---

### Projects

#### GET /projects
List all projects for authenticated user.

**Query Parameters:**
- `page`: Integer, default 1
- `limit`: Integer, default 20, max 100
- `sort_by`: String, enum [created_at, updated_at, name], default updated_at
- `sort_order`: String, enum [asc, desc], default desc
- `search`: String, optional (search in name/description)

**Response 200:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Gaming Stream Setup",
      "description": "My main streaming layout",
      "scene_count": 4,
      "thumbnail_url": "https://cdn.streambuldr.com/...",
      "created_at": "2026-03-26T10:00:00Z",
      "updated_at": "2026-03-26T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

---

#### POST /projects
Create a new project.

**Request:**
```json
{
  "name": "Gaming Stream Setup",
  "description": "For my weekly gaming streams",
  "template_id": "550e8400-e29b-41d4-a716-446655440001" // optional
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "Gaming Stream Setup",
  "description": "For my weekly gaming streams",
  "scene_count": 0,
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z",
  "scenes": [] // populated if template_id provided
}
```

---

#### GET /projects/{project_id}
Get project details with scenes.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Gaming Stream Setup",
  "description": "My main streaming layout",
  "scene_count": 4,
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T15:30:00Z",
  "scenes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "Starting Soon",
      "scene_type": "starting_soon",
      "thumbnail_url": "https://cdn.streambuldr.com/...",
      "updated_at": "2026-03-26T15:30:00Z"
    }
  ],
  "theme": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "name": "Cyberpunk Dark",
    "color_primary": "#00f5ff",
    "color_secondary": "#ff006e",
    "color_background": "#0a0a0f"
  }
}
```

**Errors:**
- `404`: Project not found
- `403`: Not authorized (project belongs to different user)

---

#### PUT /projects/{project_id}
Update project details.

**Request:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response 200:** Updated project object

---

#### DELETE /projects/{project_id}
Soft delete a project.

**Response 204:** No content

---

#### POST /projects/{project_id}/duplicate
Duplicate a project with all its scenes.

**Request:**
```json
{
  "name": "Copy of Gaming Stream Setup"
}
```

**Response 201:** New project object

---

### Scenes

#### GET /projects/{project_id}/scenes
List all scenes in a project.

**Response 200:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "Live",
      "scene_type": "live",
      "canvas_width": 1920,
      "canvas_height": 1080,
      "thumbnail_url": "https://cdn.streambuldr.com/...",
      "updated_at": "2026-03-26T15:30:00Z"
    }
  ]
}
```

---

#### POST /projects/{project_id}/scenes
Create a new scene.

**Request:**
```json
{
  "name": "BRB",
  "scene_type": "brb",
  "template_id": "550e8400-e29b-41d4-a716-446655440005" // optional
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "BRB",
  "scene_type": "brb",
  "canvas_width": 1920,
  "canvas_height": 1080,
  "background_color": "#1a1a1a",
  "layout_data": {
    "version": "1.0",
    "elements": []
  },
  "elements": [], // populated if template_id provided
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z"
}
```

---

#### GET /scenes/{scene_id}
Get full scene details with all elements.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Live",
  "scene_type": "live",
  "canvas_width": 1920,
  "canvas_height": 1080,
  "background_color": "#1a1a1a",
  "theme_id": "550e8400-e29b-41d4-a716-446655440004",
  "layout_data": {
    "version": "1.0",
    "elements": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "type": "webcam",
        "x": 50,
        "y": 50,
        "width": 320,
        "height": 180,
        "z_index": 1,
        "properties": {
          "border_radius": 8,
          "border_width": 2,
          "border_color": "#ffffff"
        }
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440008",
        "type": "chat",
        "x": 1400,
        "y": 600,
        "width": 450,
        "height": 400,
        "z_index": 2,
        "properties": {
          "font_family": "Inter",
          "font_size": 14,
          "text_color": "#ffffff",
          "background_color": "#00000080"
        }
      }
    ]
  },
  "elements": [
    // Same as above, individual records
  ],
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T15:30:00Z"
}
```

---

#### PUT /scenes/{scene_id}
Update scene (full update with elements).

**Request:**
```json
{
  "name": "Updated Scene Name",
  "background_color": "#2a2a2a",
  "layout_data": {
    "version": "1.0",
    "elements": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "type": "webcam",
        "x": 100,
        "y": 100,
        "width": 400,
        "height": 225,
        "z_index": 1,
        "properties": {
          "border_radius": 12,
          "border_width": 3,
          "border_color": "#00f5ff"
        }
      }
    ]
  }
}
```

**Response 200:** Updated scene object

**Validation:**
- All elements must have valid positions within canvas bounds
- z_index values must be unique per scene
- Element types must be supported

---

#### PATCH /scenes/{scene_id}
Partial update (name, background_color, theme_id only).

**Request:**
```json
{
  "name": "Quick Rename",
  "background_color": "#000000"
}
```

---

#### DELETE /scenes/{scene_id}
Delete a scene.

**Response 204:** No content

---

#### POST /scenes/{scene_id}/duplicate
Duplicate a scene.

**Response 201:** New scene object

---

### Elements

#### GET /scenes/{scene_id}/elements
List all elements in a scene (ordered by z_index).

**Response 200:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440007",
      "scene_id": "550e8400-e29b-41d4-a716-446655440006",
      "element_type": "webcam",
      "name": "Webcam",
      "position_x": 50,
      "position_y": 50,
      "width": 320,
      "height": 180,
      "z_index": 1,
      "properties": {...},
      "is_visible": true,
      "updated_at": "2026-03-26T15:30:00Z"
    }
  ]
}
```

---

#### POST /scenes/{scene_id}/elements
Add a new element to scene.

**Request:**
```json
{
  "element_type": "text",
  "name": "Stream Title",
  "position_x": 960,
  "position_y": 100,
  "width": 400,
  "height": 60,
  "z_index": 3,
  "properties": {
    "content": "My Awesome Stream",
    "font_family": "Inter",
    "font_size": 32,
    "font_weight": "bold",
    "text_color": "#ffffff",
    "text_align": "center"
  }
}
```

**Response 201:** Created element object

**Validation:**
- Element must be fully within canvas bounds
- z_index must not conflict (auto-adjust if needed)
- Valid element_type from enum

---

#### PUT /elements/{element_id}
Update an element.

**Request:** Same as POST but all fields optional.

**Response 200:** Updated element

---

#### DELETE /elements/{element_id}
Remove an element.

**Response 204:** No content

---

#### POST /scenes/{scene_id}/elements/reorder
Update z-index ordering for multiple elements.

**Request:**
```json
{
  "orders": [
    {"element_id": "550e8400-e29b-41d4-a716-446655440007", "z_index": 3},
    {"element_id": "550e8400-e29b-41d4-a716-446655440008", "z_index": 1}
  ]
}
```

**Response 200:** Updated elements

---

### Templates

#### GET /templates
Browse available templates.

**Query Parameters:**
- `type`: Enum [single_scene, scene_pack, all], default all
- `category`: Enum [gaming, just_chatting, creative, music, irl]
- `search`: String (search in name/description)
- `page`: Integer, default 1
- `limit`: Integer, default 20

**Response 200:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Cyberpunk Gaming",
      "description": "Futuristic neon theme for gaming streams",
      "template_type": "scene_pack",
      "category": "gaming",
      "is_system": true,
      "thumbnail_url": "https://cdn.streambuldr.com/...",
      "theme": {
        "name": "Cyberpunk Neon",
        "color_primary": "#00f5ff",
        "color_secondary": "#ff006e"
      },
      "scene_count": 4
    }
  ],
  "pagination": {...}
}
```

---

#### GET /templates/{template_id}
Get template details.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Cyberpunk Gaming",
  "template_type": "scene_pack",
  "category": "gaming",
  "is_system": true,
  "thumbnail_url": "https://cdn.streambuldr.com/...",
  "preview_data": {
    "scenes": [
      {
        "name": "Starting Soon",
        "scene_type": "starting_soon",
        "layout_data": {...}
      }
    ]
  },
  "scenes": [
    // Individual scene records for packs
  ]
}
```

---

### Themes

#### GET /themes
List available themes.

**Query Parameters:**
- `is_system`: Boolean (filter system vs user themes)
- `page`: Integer, default 1
- `limit`: Integer, default 50

**Response 200:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Cyberpunk Dark",
      "is_system": true,
      "color_primary": "#00f5ff",
      "color_secondary": "#ff006e",
      "color_background": "#0a0a0f",
      "color_surface": "#1a1a24",
      "color_text": "#ffffff",
      "color_text_muted": "#8a8a9a",
      "font_heading": "Orbitron",
      "font_body": "Inter"
    }
  ]
}
```

---

#### GET /themes/{theme_id}
Get theme details.

**Response 200:** Full theme object with all properties.

---

#### POST /themes
Create custom theme.

**Request:**
```json
{
  "name": "My Custom Theme",
  "color_primary": "#ff5500",
  "color_secondary": "#0055ff",
  "color_background": "#1a1a1a",
  "color_surface": "#2a2a2a",
  "color_text": "#ffffff",
  "color_text_muted": "#888888",
  "font_heading": "Poppins",
  "font_body": "Inter"
}
```

**Response 201:** Created theme object

---

### AI Generation

#### POST /ai/generate-scene
Generate a scene layout using AI.

**Request:**
```json
{
  "prompt": "Create a cozy gaming setup with a warm amber color scheme, webcam in bottom left, chat on the right side, and a large area for gameplay",
  "style": "cozy", // optional: minimal, futuristic, cozy, professional, vibrant
  "canvas_width": 1920, // optional, default 1920
  "canvas_height": 1080 // optional, default 1080
}
```

**Response 202:** Accepted (async processing)
```json
{
  "generation_id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "pending",
  "estimated_seconds": 10
}
```

---

#### GET /ai/generations/{generation_id}
Check generation status and retrieve result.

**Response 200 (pending):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "pending",
  "prompt": "Create a cozy gaming setup...",
  "style": "cozy",
  "created_at": "2026-03-26T10:00:00Z"
}
```

**Response 200 (completed):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "success",
  "prompt": "Create a cozy gaming setup...",
  "style": "cozy",
  "result": {
    "name": "Cozy Gaming Setup",
    "scene_type": "live",
    "background_color": "#2d2418",
    "theme": {
      "name": "Amber Warmth",
      "color_primary": "#ff9500",
      "color_secondary": "#ffcc00",
      "color_background": "#2d2418"
    },
    "layout": {
      "version": "1.0",
      "elements": [
        {
          "type": "webcam",
          "x": 50,
          "y": 750,
          "width": 320,
          "height": 200,
          "z_index": 1,
          "properties": {
            "border_radius": 16,
            "border_width": 3,
            "border_color": "#ff9500"
          }
        },
        {
          "type": "chat",
          "x": 1450,
          "y": 600,
          "width": 420,
          "height": 400,
          "z_index": 2,
          "properties": {
            "font_family": "Inter",
            "font_size": 14,
            "text_color": "#ffffff",
            "background_color": "#1a150f80",
            "border_radius": 8
          }
        }
      ]
    }
  },
  "processing_time_ms": 3250,
  "created_at": "2026-03-26T10:00:00Z",
  "completed_at": "2026-03-26T10:00:03Z"
}
```

**Response 200 (error):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "error",
  "prompt": "Create a cozy gaming setup...",
  "error_message": "Unable to parse AI response into valid layout",
  "created_at": "2026-03-26T10:00:00Z"
}
```

---

### Export

#### POST /scenes/{scene_id}/export/png
Export scene as PNG image.

**Request:**
```json
{
  "scale": 1, // 0.5, 1, 2 (for higher resolution)
  "transparent_background": false // if true, exports with transparent bg
}
```

**Response 200:**
```json
{
  "download_url": "https://cdn.streambuldr.com/exports/550e8400-e29b-41d4-a716-446655440006.png?token=...",
  "expires_at": "2026-03-26T11:00:00Z",
  "width": 1920,
  "height": 1080
}
```

**Errors:**
- `400`: Invalid scale value
- `422`: Empty scene (no elements to export)

---

#### POST /scenes/{scene_id}/export/json
Export scene as JSON for OBS import.

**Response 200:**
```json
{
  "download_url": "https://cdn.streambuldr.com/exports/550e8400-e29b-41d4-a716-446655440006.json?token=...",
  "expires_at": "2026-03-26T11:00:00Z",
  "format": "obs-studio",
  "version": "1.0"
}
```

**JSON Export Schema (OBS-compatible):**
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
      "crop": null,
      "visible": true,
      "locked": false,
      "bounds": {
        "type": "none"
      },
      "streambuldr_meta": {
        "border_radius": 8,
        "border_width": 2,
        "border_color": "#ffffff"
      }
    }
  ],
  "sources": [],
  "transitions": []
}
```

---

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields failed validation",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Codes:**
- `VALIDATION_ERROR`: Field validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing token
- `AUTHORIZATION_ERROR`: Permission denied
- `NOT_FOUND`: Resource doesn't exist
- `CONFLICT`: Resource already exists (duplicate email, etc.)
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| All auth endpoints | 10 requests/minute per IP |
| AI generation | 10 requests/hour per user |
| All other endpoints | 100 requests/minute per user |

---

## Version History

- v1.0 (2026-03-26): Initial API specification for MVP
