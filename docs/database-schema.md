# Database Schema - AI Stream Scene Builder

## Overview
PostgreSQL database using SQLModel ORM. All tables use UUID primary keys with automatic generation.

---

## Tables

### 1. users
Stores user accounts and authentication data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| display_name | VARCHAR(100) | NOT NULL | User's display name |
| is_active | BOOLEAN | DEFAULT true | Account status |
| created_at | TIMESTAMP | DEFAULT now() | Account creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_users_email` on `email` (for login lookups)

---

### 2. projects
Container for multiple scenes belonging to a user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique project identifier |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Owner of project |
| name | VARCHAR(200) | NOT NULL | Project name |
| description | TEXT | NULL | Project description |
| is_active | BOOLEAN | DEFAULT true | Soft delete flag |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_projects_user_id` on `user_id` (for user's project listing)
- `idx_projects_created_at` on `created_at DESC` (for sorting)

---

### 3. scenes
Individual stream layouts within a project.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique scene identifier |
| project_id | UUID | FOREIGN KEY → projects(id), NOT NULL | Parent project |
| name | VARCHAR(200) | NOT NULL | Scene name (e.g., "Live", "BRB") |
| scene_type | VARCHAR(50) | NOT NULL | Type: starting_soon, live, brb, ending, custom |
| canvas_width | INTEGER | DEFAULT 1920 | Canvas width in pixels |
| canvas_height | INTEGER | DEFAULT 1080 | Canvas height in pixels |
| background_color | VARCHAR(7) | DEFAULT '#1a1a1a' | Hex background color |
| theme_id | UUID | FOREIGN KEY → themes(id), NULL | Applied theme |
| layout_data | JSONB | NOT NULL | Serialized element positions |
| thumbnail_url | VARCHAR(500) | NULL | Preview image URL |
| is_active | BOOLEAN | DEFAULT true | Soft delete flag |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_scenes_project_id` on `project_id` (for project scene listing)
- `idx_scenes_scene_type` on `scene_type` (for filtering by type)

**layout_data JSON Schema:**
```json
{
  "version": "1.0",
  "elements": [
    {
      "id": "uuid-string",
      "type": "webcam|chat|alert|text|image|panel",
      "x": 100,
      "y": 200,
      "width": 300,
      "height": 200,
      "z_index": 1,
      "properties": { /* element-specific data */ }
    }
  ]
}
```

---

### 4. elements
Individual overlay components (stored as JSONB in scenes, but can be extracted for querying).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique element identifier |
| scene_id | UUID | FOREIGN KEY → scenes(id), NOT NULL | Parent scene |
| element_type | VARCHAR(50) | NOT NULL | Type: webcam, chat, alert, text, image, panel |
| name | VARCHAR(200) | NOT NULL | Element name/label |
| position_x | INTEGER | NOT NULL | X coordinate on canvas |
| position_y | INTEGER | NOT NULL | Y coordinate on canvas |
| width | INTEGER | NOT NULL | Width in pixels |
| height | INTEGER | NOT NULL | Height in pixels |
| z_index | INTEGER | DEFAULT 0 | Layer order (higher = on top) |
| properties | JSONB | DEFAULT '{}' | Element-specific properties |
| is_visible | BOOLEAN | DEFAULT true | Visibility toggle |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_elements_scene_id` on `scene_id` (for scene element loading)
- `idx_elements_z_index` on `z_index` (for layer ordering)

**properties JSON by type:**

**webcam:**
```json
{
  "border_radius": 8,
  "border_width": 2,
  "border_color": "#ffffff",
  "background_color": "#000000",
  "aspect_ratio": "16:9"
}
```

**chat:**
```json
{
  "font_family": "Inter",
  "font_size": 14,
  "text_color": "#ffffff",
  "background_color": "#00000080",
  "border_radius": 4,
  "max_messages": 10
}
```

**alert:**
```json
{
  "animation_type": "slide_in|fade_in|bounce",
  "duration_seconds": 5,
  "sound_enabled": false,
  "font_family": "Inter",
  "font_size": 24,
  "text_color": "#ffffff"
}
```

**text:**
```json
{
  "content": "Stream Title Here",
  "font_family": "Inter",
  "font_size": 32,
  "font_weight": "bold",
  "text_color": "#ffffff",
  "text_align": "left|center|right",
  "text_transform": "none|uppercase|lowercase"
}
```

**image:**
```json
{
  "src": "https://...",
  "alt": "Logo",
  "object_fit": "contain|cover|fill",
  "border_radius": 0
}
```

**panel:**
```json
{
  "background_color": "#2a2a2a",
  "border_radius": 8,
  "border_width": 0,
  "border_color": "#3a3a3a",
  "opacity": 1.0
}
```

---

### 5. themes
Visual styling systems that can be applied to projects or scenes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique theme identifier |
| name | VARCHAR(200) | NOT NULL | Theme name |
| is_system | BOOLEAN | DEFAULT false | True for built-in themes |
| user_id | UUID | FOREIGN KEY → users(id), NULL | Creator (null for system themes) |
| color_primary | VARCHAR(7) | NOT NULL | Primary brand color |
| color_secondary | VARCHAR(7) | NOT NULL | Secondary accent color |
| color_background | VARCHAR(7) | NOT NULL | Default background |
| color_surface | VARCHAR(7) | NOT NULL | Panel/card backgrounds |
| color_text | VARCHAR(7) | NOT NULL | Primary text color |
| color_text_muted | VARCHAR(7) | NOT NULL | Secondary/muted text |
| font_heading | VARCHAR(100) | DEFAULT 'Inter' | Heading font family |
| font_body | VARCHAR(100) | DEFAULT 'Inter' | Body text font family |
| properties | JSONB | DEFAULT '{}' | Additional theme properties |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_themes_user_id` on `user_id` (for user's custom themes)
- `idx_themes_is_system` on `is_system` (for filtering system themes)

---

### 6. templates
Pre-built scene layouts and scene packs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique template identifier |
| name | VARCHAR(200) | NOT NULL | Template name |
| description | TEXT | NULL | Template description |
| template_type | VARCHAR(50) | NOT NULL | Type: single_scene, scene_pack |
| category | VARCHAR(100) | NOT NULL | Category: gaming, just_chatting, creative, etc. |
| is_system | BOOLEAN | DEFAULT false | True for built-in templates |
| user_id | UUID | FOREIGN KEY → users(id), NULL | Creator (null for system templates) |
| thumbnail_url | VARCHAR(500) | NULL | Preview image URL |
| preview_data | JSONB | NOT NULL | Serialized scene data for preview |
| theme_id | UUID | FOREIGN KEY → themes(id), NULL | Associated theme |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update time |

**Indexes:**
- `idx_templates_type` on `template_type` (for filtering by type)
- `idx_templates_category` on `category` (for category browsing)
- `idx_templates_is_system` on `is_system` (for filtering system templates)

---

### 7. template_scenes (for scene packs)
Individual scenes within a template pack.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| template_id | UUID | FOREIGN KEY → templates(id), NOT NULL | Parent template |
| scene_type | VARCHAR(50) | NOT NULL | starting_soon, live, brb, ending |
| name | VARCHAR(200) | NOT NULL | Scene name |
| layout_data | JSONB | NOT NULL | Serialized element data |
| display_order | INTEGER | DEFAULT 0 | Order within pack |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |

**Indexes:**
- `idx_template_scenes_template_id` on `template_id` (for loading pack scenes)
- `idx_template_scenes_order` on `display_order` (for ordering)

---

### 8. refresh_tokens
JWT refresh token storage for authentication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Token owner |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | Hashed refresh token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| revoked_at | TIMESTAMP | NULL | Revocation time (if revoked) |

**Indexes:**
- `idx_refresh_tokens_user_id` on `user_id` (for user's tokens)
- `idx_refresh_tokens_hash` on `token_hash` (for token lookup)

---

### 9. ai_generations
Log of AI scene generation requests for analytics and improvement.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Requesting user |
| prompt | TEXT | NOT NULL | User's input prompt |
| style_hint | VARCHAR(100) | NULL | Optional style preference |
| generated_layout | JSONB | NOT NULL | AI output layout |
| status | VARCHAR(50) | NOT NULL | pending, success, error |
| error_message | TEXT | NULL | Error details if failed |
| processing_time_ms | INTEGER | NULL | Generation duration |
| created_at | TIMESTAMP | DEFAULT now() | Request time |

**Indexes:**
- `idx_ai_generations_user_id` on `user_id` (for user's generation history)
- `idx_ai_generations_status` on `status` (for filtering)
- `idx_ai_generations_created_at` on `created_at DESC` (for history listing)

---

## Relationships

```
users ||--o{ projects : owns
users ||--o{ themes : creates
users ||--o{ templates : creates
users ||--o{ ai_generations : requests
users ||--o{ refresh_tokens : has

projects ||--o{ scenes : contains
projects }o--|| themes : uses

scenes }o--|| themes : applies
scenes ||--o{ elements : contains

templates ||--o{ template_scenes : includes
templates }o--|| themes : uses
```

---

## Migration Notes

1. Enable UUID extension: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
2. Enable pgcrypto for gen_random_uuid(): `CREATE EXTENSION IF NOT EXISTS "pgcrypto";`
3. Set up updated_at triggers for all tables
4. Create GIN indexes on JSONB columns for efficient querying

---

## SQLModel Classes (Python Reference)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    display_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    projects: List["Project"] = Relationship(back_populates="user")
    themes: List["Theme"] = Relationship(back_populates="user")

class Project(SQLModel, table=True):
    __tablename__ = "projects"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=200)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="projects")
    scenes: List["Scene"] = Relationship(back_populates="project")

class Scene(SQLModel, table=True):
    __tablename__ = "scenes"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    name: str = Field(max_length=200)
    scene_type: str = Field(max_length=50)
    canvas_width: int = Field(default=1920)
    canvas_height: int = Field(default=1080)
    background_color: str = Field(default="#1a1a1a", max_length=7)
    theme_id: Optional[uuid.UUID] = Field(foreign_key="themes.id")
    layout_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    project: Optional[Project] = Relationship(back_populates="scenes")
    elements: List["Element"] = Relationship(back_populates="scene")

class Element(SQLModel, table=True):
    __tablename__ = "elements"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    scene_id: uuid.UUID = Field(foreign_key="scenes.id", index=True)
    element_type: str = Field(max_length=50)
    name: str = Field(max_length=200)
    position_x: int
    position_y: int
    width: int
    height: int
    z_index: int = Field(default=0, index=True)
    properties: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_visible: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    scene: Optional[Scene] = Relationship(back_populates="elements")

class Theme(SQLModel, table=True):
    __tablename__ = "themes"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=200)
    is_system: bool = Field(default=False, index=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", index=True)
    color_primary: str = Field(max_length=7)
    color_secondary: str = Field(max_length=7)
    color_background: str = Field(max_length=7)
    color_surface: str = Field(max_length=7)
    color_text: str = Field(max_length=7)
    color_text_muted: str = Field(max_length=7)
    font_heading: str = Field(default="Inter", max_length=100)
    font_body: str = Field(default="Inter", max_length=100)
    properties: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="themes")
```

---

## Version History

- v1.0 (2026-03-26): Initial schema for MVP
