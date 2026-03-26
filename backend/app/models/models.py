"""Database models for the application."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """User account model."""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    email: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    display_name: str = Field(sa_column=Column(String(100), nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="user")
    themes: List["Theme"] = Relationship(back_populates="user")
    templates: List["Template"] = Relationship(back_populates="user")


class Project(SQLModel, table=True):
    """Project container for scenes."""
    __tablename__ = "projects"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    user_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("users.id"), nullable=False, index=True))
    name: str = Field(sa_column=Column(String(200), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="projects")
    scenes: List["Scene"] = Relationship(back_populates="project")


class Scene(SQLModel, table=True):
    """Individual scene/layout."""
    __tablename__ = "scenes"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    project_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("projects.id"), nullable=False, index=True))
    name: str = Field(sa_column=Column(String(200), nullable=False))
    scene_type: str = Field(sa_column=Column(String(50), nullable=False))  # starting_soon, live, brb, ending, custom
    canvas_width: int = Field(default=1920, sa_column=Column(Integer, default=1920))
    canvas_height: int = Field(default=1080, sa_column=Column(Integer, default=1080))
    background_color: str = Field(default="#1a1a1a", sa_column=Column(String(7), default="#1a1a1a"))
    theme_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID, ForeignKey("themes.id")))
    layout_data: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    thumbnail_url: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    project: Optional[Project] = Relationship(back_populates="scenes")
    elements: List["Element"] = Relationship(back_populates="scene")
    theme: Optional["Theme"] = Relationship()


class Element(SQLModel, table=True):
    """Scene element model."""
    __tablename__ = "elements"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    scene_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("scenes.id"), nullable=False, index=True))
    element_type: str = Field(sa_column=Column(String(50), nullable=False))  # webcam, chat, alert, text, image, panel
    name: str = Field(sa_column=Column(String(200), nullable=False))
    position_x: int = Field(sa_column=Column(Integer, nullable=False))
    position_y: int = Field(sa_column=Column(Integer, nullable=False))
    width: int = Field(sa_column=Column(Integer, nullable=False))
    height: int = Field(sa_column=Column(Integer, nullable=False))
    z_index: int = Field(default=0, sa_column=Column(Integer, default=0, index=True))
    properties: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    is_visible: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    scene: Optional[Scene] = Relationship(back_populates="elements")


class Theme(SQLModel, table=True):
    """Theme/styling model."""
    __tablename__ = "themes"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    name: str = Field(sa_column=Column(String(200), nullable=False))
    is_system: bool = Field(default=False, sa_column=Column(Boolean, default=False, index=True))
    user_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID, ForeignKey("users.id"), index=True))
    color_primary: str = Field(sa_column=Column(String(7), nullable=False))
    color_secondary: str = Field(sa_column=Column(String(7), nullable=False))
    color_background: str = Field(sa_column=Column(String(7), nullable=False))
    color_surface: str = Field(sa_column=Column(String(7), nullable=False))
    color_text: str = Field(sa_column=Column(String(7), nullable=False))
    color_text_muted: str = Field(sa_column=Column(String(7), nullable=False))
    font_heading: str = Field(default="Inter", sa_column=Column(String(100), default="Inter"))
    font_body: str = Field(default="Inter", sa_column=Column(String(100), default="Inter"))
    properties: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="themes")


class Template(SQLModel, table=True):
    """Template model for pre-built scenes."""
    __tablename__ = "templates"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    name: str = Field(sa_column=Column(String(200), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    template_type: str = Field(sa_column=Column(String(50), nullable=False))  # single_scene, scene_pack
    category: str = Field(sa_column=Column(String(100), nullable=False))
    is_system: bool = Field(default=False, sa_column=Column(Boolean, default=False, index=True))
    user_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID, ForeignKey("users.id")))
    thumbnail_url: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    preview_data: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    theme_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID, ForeignKey("themes.id")))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="templates")
    theme: Optional[Theme] = Relationship()
    scenes: List["TemplateScene"] = Relationship(back_populates="template")


class TemplateScene(SQLModel, table=True):
    """Individual scenes within a template pack."""
    __tablename__ = "template_scenes"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    template_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("templates.id"), nullable=False, index=True))
    scene_type: str = Field(sa_column=Column(String(50), nullable=False))
    name: str = Field(sa_column=Column(String(200), nullable=False))
    layout_data: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    display_order: int = Field(default=0, sa_column=Column(Integer, default=0))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    
    # Relationships
    template: Optional[Template] = Relationship(back_populates="scenes")


class RefreshToken(SQLModel, table=True):
    """Refresh token storage."""
    __tablename__ = "refresh_tokens"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    user_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("users.id"), nullable=False, index=True))
    token_hash: str = Field(sa_column=Column(String(255), unique=True, nullable=False, index=True))
    expires_at: datetime = Field(sa_column=Column(DateTime, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    revoked_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))


class AIGeneration(SQLModel, table=True):
    """AI generation request log."""
    __tablename__ = "ai_generations"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PGUUID, primary_key=True))
    user_id: UUID = Field(sa_column=Column(PGUUID, ForeignKey("users.id"), nullable=False, index=True))
    prompt: str = Field(sa_column=Column(Text, nullable=False))
    style_hint: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    generated_layout: dict = Field(default_factory=dict, sa_column=Column(JSON, default={}))
    status: str = Field(sa_column=Column(String(50), nullable=False))  # pending, success, error
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    processing_time_ms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
