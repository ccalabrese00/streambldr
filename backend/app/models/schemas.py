"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Theme schemas
class ThemeBase(BaseModel):
    name: str = Field(..., max_length=200)
    color_primary: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    color_secondary: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    color_background: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    color_surface: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    color_text: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    color_text_muted: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    font_heading: str = Field(default="Inter", max_length=100)
    font_body: str = Field(default="Inter", max_length=100)


class ThemeCreate(ThemeBase):
    pass


class ThemeResponse(ThemeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_system: bool
    user_id: Optional[UUID]
    created_at: datetime


# Element schemas
class ElementProperties(BaseModel):
    # Webcam
    border_radius: Optional[int] = Field(None, ge=0, le=50)
    border_width: Optional[int] = Field(None, ge=0, le=10)
    border_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    background_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    aspect_ratio: Optional[str] = None
    
    # Chat
    font_family: Optional[str] = None
    font_size: Optional[int] = Field(None, ge=8, le=72)
    text_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    max_messages: Optional[int] = Field(None, ge=1, le=100)
    
    # Alert
    animation_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    sound_enabled: Optional[bool] = None
    
    # Text
    content: Optional[str] = None
    font_weight: Optional[str] = None
    text_align: Optional[str] = None
    text_transform: Optional[str] = None
    
    # Image
    src: Optional[str] = None
    alt: Optional[str] = None
    object_fit: Optional[str] = None
    
    # Panel
    opacity: Optional[float] = Field(None, ge=0.0, le=1.0)


class ElementBase(BaseModel):
    element_type: str = Field(..., pattern=r'^(webcam|chat|alert|text|image|panel)$')
    name: str = Field(..., max_length=200)
    position_x: int = Field(..., ge=0)
    position_y: int = Field(..., ge=0)
    width: int = Field(..., ge=20, le=3840)
    height: int = Field(..., ge=20, le=2160)
    z_index: int = Field(default=0, ge=0)
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_visible: bool = True


class ElementCreate(ElementBase):
    pass


class ElementUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=20, le=3840)
    height: Optional[int] = Field(None, ge=20, le=2160)
    z_index: Optional[int] = Field(None, ge=0)
    properties: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None


class ElementResponse(ElementBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    scene_id: UUID
    created_at: datetime
    updated_at: datetime


class ElementReorderRequest(BaseModel):
    orders: List[Dict[str, Any]]


# Scene schemas
class LayoutData(BaseModel):
    version: str = "1.0"
    elements: List[Dict[str, Any]] = Field(default_factory=list)


class SceneBase(BaseModel):
    name: str = Field(..., max_length=200)
    scene_type: str = Field(..., pattern=r'^(starting_soon|live|brb|ending|custom)$')
    canvas_width: int = Field(default=1920, ge=640, le=3840)
    canvas_height: int = Field(default=1080, ge=360, le=2160)
    background_color: str = Field(default="#1a1a1a", pattern=r'^#[0-9A-Fa-f]{6}$')
    theme_id: Optional[UUID] = None


class SceneCreate(SceneBase):
    template_id: Optional[UUID] = None
    layout_data: Optional[LayoutData] = None


class SceneUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    background_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    theme_id: Optional[UUID] = None
    layout_data: Optional[LayoutData] = None


class SceneResponse(SceneBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    layout_data: Dict[str, Any]
    thumbnail_url: Optional[str]
    elements: List[ElementResponse] = []
    created_at: datetime
    updated_at: datetime


class SceneListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    scene_type: str
    canvas_width: int
    canvas_height: int
    thumbnail_url: Optional[str]
    updated_at: datetime


# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    template_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    scene_count: int = 0
    thumbnail_url: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    scenes: List[SceneListResponse] = []
    theme: Optional[ThemeResponse] = None


# Template schemas
class TemplateBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    template_type: str = Field(..., pattern=r'^(single_scene|scene_pack)$')
    category: str = Field(..., max_length=100)


class TemplateResponse(TemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_system: bool
    thumbnail_url: Optional[str]
    theme: Optional[ThemeResponse] = None
    scene_count: int = 0


class TemplateDetailResponse(TemplateResponse):
    preview_data: Dict[str, Any] = {}
    scenes: List[Dict[str, Any]] = []


# AI Generation schemas
class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500)
    style: Optional[str] = Field(None, pattern=r'^(minimal|futuristic|cozy|professional|vibrant|retro)$')
    canvas_width: int = Field(default=1920, ge=640, le=3840)
    canvas_height: int = Field(default=1080, ge=360, le=2160)


class AIGenerationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: str
    prompt: str
    style_hint: Optional[str]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]


# Export schemas
class PNGExportRequest(BaseModel):
    scale: float = Field(default=1.0, ge=0.5, le=4.0)
    transparent_background: bool = False


class PNGExportResponse(BaseModel):
    download_url: str
    expires_at: datetime
    width: int
    height: int


class JSONExportResponse(BaseModel):
    download_url: str
    expires_at: datetime
    format: str = "obs-studio"
    version: str = "1.0"


# Pagination
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: Dict[str, Any]


# Error response
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
