"""Templates API endpoints."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.api.v1.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, Template, TemplateScene
from app.models.schemas import (
    TemplateResponse,
    TemplateDetailResponse,
    PaginatedResponse
)

router = APIRouter()


@router.get("/templates", response_model=PaginatedResponse)
def list_templates(
    template_type: Optional[str] = Query(None, pattern=r'^(single_scene|scene_pack)$'),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Browse available templates."""
    # Build query
    query = select(Template).where(Template.is_system == True)
    
    if template_type:
        query = query.where(Template.template_type == template_type)
    
    if category:
        query = query.where(Template.category.ilike(f"%{category}%"))
    
    if search:
        query = query.where(
            Template.name.ilike(f"%{search}%") |
            Template.description.ilike(f"%{search}%")
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()
    
    # Apply pagination
    query = query.order_by(Template.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    templates = db.execute(query).scalars().all()
    
    # Format response
    template_responses = []
    for template in templates:
        scene_count = len(template.scenes) if template.template_type == "scene_pack" else 1
        
        template_responses.append({
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "template_type": template.template_type,
            "category": template.category,
            "is_system": template.is_system,
            "thumbnail_url": template.thumbnail_url,
            "scene_count": scene_count,
            "theme": {
                "name": template.theme.name if template.theme else None,
                "color_primary": template.theme.color_primary if template.theme else None,
                "color_secondary": template.theme.color_secondary if template.theme else None
            } if template.theme else None
        })
    
    return {
        "data": template_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Get template details."""
    template = db.get(Template, template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    scenes_data = []
    for scene in template.scenes:
        scenes_data.append({
            "id": scene.id,
            "name": scene.name,
            "scene_type": scene.scene_type,
            "layout_data": scene.layout_data
        })
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "template_type": template.template_type,
        "category": template.category,
        "is_system": template.is_system,
        "thumbnail_url": template.thumbnail_url,
        "preview_data": template.preview_data,
        "scene_count": len(scenes_data),
        "theme": {
            "id": template.theme.id if template.theme else None,
            "name": template.theme.name if template.theme else None,
            "color_primary": template.theme.color_primary if template.theme else None,
            "color_secondary": template.theme.color_secondary if template.theme else None,
            "color_background": template.theme.color_background if template.theme else None
        } if template.theme else None,
        "scenes": scenes_data
    }
