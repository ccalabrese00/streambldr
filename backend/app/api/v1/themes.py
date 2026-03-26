"""Themes API endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.api.v1.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, Theme
from app.models.schemas import (
    ThemeCreate,
    ThemeResponse,
    PaginatedResponse
)

router = APIRouter()


@router.get("/themes", response_model=PaginatedResponse)
def list_themes(
    is_system: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List available themes."""
    # Build query
    query = select(Theme)
    
    if is_system is not None:
        query = query.where(Theme.is_system == is_system)
    
    # Get system themes + user's custom themes
    if is_system is None:
        query = query.where(
            (Theme.is_system == True) | (Theme.user_id == current_user.id)
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()
    
    # Apply pagination
    query = query.order_by(Theme.is_system.desc(), Theme.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    themes = db.execute(query).scalars().all()
    
    return {
        "data": themes,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
def get_theme(
    theme_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get theme details."""
    theme = db.get(Theme, theme_id)
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    # Check access - must be system theme or owned by user
    if not theme.is_system and theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this theme"
        )
    
    return theme


@router.post("/themes", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
def create_theme(
    theme_data: ThemeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create custom theme."""
    theme = Theme(
        name=theme_data.name,
        is_system=False,
        user_id=current_user.id,
        color_primary=theme_data.color_primary,
        color_secondary=theme_data.color_secondary,
        color_background=theme_data.color_background,
        color_surface=theme_data.color_surface,
        color_text=theme_data.color_text,
        color_text_muted=theme_data.color_text_muted,
        font_heading=theme_data.font_heading,
        font_body=theme_data.font_body
    )
    
    db.add(theme)
    db.commit()
    db.refresh(theme)
    
    return theme


@router.put("/themes/{theme_id}", response_model=ThemeResponse)
def update_theme(
    theme_id: UUID,
    theme_data: ThemeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update custom theme."""
    theme = db.get(Theme, theme_id)
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    if theme.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system themes"
        )
    
    if theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this theme"
        )
    
    # Update fields
    theme.name = theme_data.name
    theme.color_primary = theme_data.color_primary
    theme.color_secondary = theme_data.color_secondary
    theme.color_background = theme_data.color_background
    theme.color_surface = theme_data.color_surface
    theme.color_text = theme_data.color_text
    theme.color_text_muted = theme_data.color_text_muted
    theme.font_heading = theme_data.font_heading
    theme.font_body = theme_data.font_body
    theme.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(theme)
    
    return theme


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theme(
    theme_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete custom theme."""
    theme = db.get(Theme, theme_id)
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    if theme.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system themes"
        )
    
    if theme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this theme"
        )
    
    db.delete(theme)
    db.commit()
    
    return None
