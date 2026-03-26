"""Projects API endpoints."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.api.v1.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, Project, Scene, Element, Template, Theme
from app.models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    PaginationParams,
    PaginatedResponse
)

router = APIRouter()


@router.get("/projects", response_model=PaginatedResponse)
def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all projects for current user."""
    # Build query
    query = select(Project).where(
        Project.user_id == current_user.id,
        Project.is_active == True
    )
    
    if search:
        query = query.where(
            Project.name.ilike(f"%{search}%") | 
            Project.description.ilike(f"%{search}%")
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()
    
    # Apply pagination
    query = query.order_by(Project.updated_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    projects = db.execute(query).scalars().all()
    
    # Format response
    project_responses = []
    for project in projects:
        scene_count = db.execute(
            select(func.count()).where(
                Scene.project_id == project.id,
                Scene.is_active == True
            )
        ).scalar()
        
        project_responses.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "scene_count": scene_count,
            "thumbnail_url": project.scenes[0].thumbnail_url if project.scenes else None,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        })
    
    return {
        "data": project_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/projects", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new project."""
    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # If template_id provided, copy scenes from template
    if project_data.template_id:
        template = db.get(Template, project_data.template_id)
        if template and template.is_system:
            # Copy scenes from template
            for template_scene in template.scenes:
                scene = Scene(
                    project_id=project.id,
                    name=template_scene.name,
                    scene_type=template_scene.scene_type,
                    layout_data=template_scene.layout_data,
                    background_color="#1a1a1a"
                )
                db.add(scene)
    
    db.commit()
    
    # Get scenes for response
    scenes = db.execute(
        select(Scene).where(
            Scene.project_id == project.id,
            Scene.is_active == True
        )
    ).scalars().all()
    
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "scene_count": len(scenes),
        "thumbnail_url": scenes[0].thumbnail_url if scenes else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "scenes": [
            {
                "id": s.id,
                "name": s.name,
                "scene_type": s.scene_type,
                "canvas_width": s.canvas_width,
                "canvas_height": s.canvas_height,
                "thumbnail_url": s.thumbnail_url,
                "updated_at": s.updated_at
            } for s in scenes
        ],
        "theme": None
    }


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get project details with scenes."""
    project = db.get(Project, project_id)
    
    if not project or project.user_id != current_user.id or not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    scenes = db.execute(
        select(Scene).where(
            Scene.project_id == project.id,
            Scene.is_active == True
        )
    ).scalars().all()
    
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "scene_count": len(scenes),
        "thumbnail_url": scenes[0].thumbnail_url if scenes else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "scenes": [
            {
                "id": s.id,
                "name": s.name,
                "scene_type": s.scene_type,
                "canvas_width": s.canvas_width,
                "canvas_height": s.canvas_height,
                "thumbnail_url": s.thumbnail_url,
                "updated_at": s.updated_at
            } for s in scenes
        ],
        "theme": None
    }


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update project details."""
    project = db.get(Project, project_id)
    
    if not project or project.user_id != current_user.id or not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
    scene_count = db.execute(
        select(func.count()).where(
            Scene.project_id == project.id,
            Scene.is_active == True
        )
    ).scalar()
    
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "scene_count": scene_count,
        "thumbnail_url": project.scenes[0].thumbnail_url if project.scenes else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete a project."""
    project = db.get(Project, project_id)
    
    if not project or project.user_id != current_user.id or not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.is_active = False
    project.updated_at = datetime.utcnow()
    
    # Also soft delete all scenes
    scenes = db.execute(
        select(Scene).where(Scene.project_id == project.id)
    ).scalars().all()
    
    for scene in scenes:
        scene.is_active = False
        scene.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/projects/{project_id}/duplicate", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def duplicate_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a project with all its scenes."""
    original = db.get(Project, project_id)
    
    if not original or original.user_id != current_user.id or not original.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Create new project
    new_project = Project(
        user_id=current_user.id,
        name=f"Copy of {original.name}",
        description=original.description
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Copy scenes
    original_scenes = db.execute(
        select(Scene).where(
            Scene.project_id == original.id,
            Scene.is_active == True
        )
    ).scalars().all()
    
    for scene in original_scenes:
        new_scene = Scene(
            project_id=new_project.id,
            name=scene.name,
            scene_type=scene.scene_type,
            canvas_width=scene.canvas_width,
            canvas_height=scene.canvas_height,
            background_color=scene.background_color,
            theme_id=scene.theme_id,
            layout_data=scene.layout_data
        )
        db.add(new_scene)
        db.commit()
        db.refresh(new_scene)
        
        # Copy elements
        elements = db.execute(
            select(Element).where(Element.scene_id == scene.id)
        ).scalars().all()
        
        for element in elements:
            new_element = Element(
                scene_id=new_scene.id,
                element_type=element.element_type,
                name=element.name,
                position_x=element.position_x,
                position_y=element.position_y,
                width=element.width,
                height=element.height,
                z_index=element.z_index,
                properties=element.properties,
                is_visible=element.is_visible
            )
            db.add(new_element)
    
    db.commit()
    
    # Get scenes for response
    scenes = db.execute(
        select(Scene).where(
            Scene.project_id == new_project.id,
            Scene.is_active == True
        )
    ).scalars().all()
    
    return {
        "id": new_project.id,
        "user_id": new_project.user_id,
        "name": new_project.name,
        "description": new_project.description,
        "scene_count": len(scenes),
        "thumbnail_url": scenes[0].thumbnail_url if scenes else None,
        "created_at": new_project.created_at,
        "updated_at": new_project.updated_at,
        "scenes": [
            {
                "id": s.id,
                "name": s.name,
                "scene_type": s.scene_type,
                "canvas_width": s.canvas_width,
                "canvas_height": s.canvas_height,
                "thumbnail_url": s.thumbnail_url,
                "updated_at": s.updated_at
            } for s in scenes
        ],
        "theme": None
    }
