"""Scenes API endpoints."""
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.v1.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, Project, Scene, Element, Template
from app.models.schemas import (
    SceneCreate,
    SceneUpdate,
    SceneResponse,
    SceneListResponse
)

router = APIRouter()


def check_project_access(project_id: UUID, user_id: UUID, db: Session) -> Project:
    """Verify user has access to project."""
    project = db.get(Project, project_id)
    
    if not project or project.user_id != user_id or not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.get("/projects/{project_id}/scenes", response_model=List[SceneListResponse])
def list_scenes(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all scenes in a project."""
    check_project_access(project_id, current_user.id, db)
    
    scenes = db.execute(
        select(Scene).where(
            Scene.project_id == project_id,
            Scene.is_active == True
        ).order_by(Scene.created_at)
    ).scalars().all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "scene_type": s.scene_type,
            "canvas_width": s.canvas_width,
            "canvas_height": s.canvas_height,
            "thumbnail_url": s.thumbnail_url,
            "updated_at": s.updated_at
        } for s in scenes
    ]


@router.post("/projects/{project_id}/scenes", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
def create_scene(
    project_id: UUID,
    scene_data: SceneCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new scene."""
    check_project_access(project_id, current_user.id, db)
    
    # Create scene
    scene = Scene(
        project_id=project_id,
        name=scene_data.name,
        scene_type=scene_data.scene_type,
        canvas_width=scene_data.canvas_width,
        canvas_height=scene_data.canvas_height,
        background_color=scene_data.background_color,
        theme_id=scene_data.theme_id,
        layout_data=scene_data.layout_data.dict() if scene_data.layout_data else {"version": "1.0", "elements": []}
    )
    db.add(scene)
    db.commit()
    db.refresh(scene)
    
    # If template provided, copy elements
    if scene_data.template_id:
        template = db.get(Template, scene_data.template_id)
        if template and template.is_system:
            # Find matching scene in template
            for template_scene in template.scenes:
                if template_scene.scene_type == scene_data.scene_type:
                    scene.layout_data = template_scene.layout_data
                    
                    # Create elements from layout data
                    for el_data in template_scene.layout_data.get("elements", []):
                        element = Element(
                            scene_id=scene.id,
                            element_type=el_data.get("type", "panel"),
                            name=el_data.get("name", "Element"),
                            position_x=el_data.get("x", 0),
                            position_y=el_data.get("y", 0),
                            width=el_data.get("width", 100),
                            height=el_data.get("height", 100),
                            z_index=el_data.get("z_index", 0),
                            properties=el_data.get("properties", {}),
                            is_visible=True
                        )
                        db.add(element)
                    break
    
    db.commit()
    db.refresh(scene)
    
    # Get elements for response
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    return {
        "id": scene.id,
        "project_id": scene.project_id,
        "name": scene.name,
        "scene_type": scene.scene_type,
        "canvas_width": scene.canvas_width,
        "canvas_height": scene.canvas_height,
        "background_color": scene.background_color,
        "theme_id": scene.theme_id,
        "layout_data": scene.layout_data,
        "thumbnail_url": scene.thumbnail_url,
        "elements": elements,
        "created_at": scene.created_at,
        "updated_at": scene.updated_at
    }


@router.get("/scenes/{scene_id}", response_model=SceneResponse)
def get_scene(
    scene_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get full scene details with elements."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check project ownership
    check_project_access(scene.project_id, current_user.id, db)
    
    # Get elements
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    return {
        "id": scene.id,
        "project_id": scene.project_id,
        "name": scene.name,
        "scene_type": scene.scene_type,
        "canvas_width": scene.canvas_width,
        "canvas_height": scene.canvas_height,
        "background_color": scene.background_color,
        "theme_id": scene.theme_id,
        "layout_data": scene.layout_data,
        "thumbnail_url": scene.thumbnail_url,
        "elements": elements,
        "created_at": scene.created_at,
        "updated_at": scene.updated_at
    }


@router.put("/scenes/{scene_id}", response_model=SceneResponse)
def update_scene(
    scene_id: UUID,
    scene_data: SceneUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update scene (full update with elements)."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(scene.project_id, current_user.id, db)
    
    # Update fields
    if scene_data.name is not None:
        scene.name = scene_data.name
    if scene_data.background_color is not None:
        scene.background_color = scene_data.background_color
    if scene_data.theme_id is not None:
        scene.theme_id = scene_data.theme_id
    if scene_data.layout_data is not None:
        scene.layout_data = scene_data.layout_data.dict()
    
    scene.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scene)
    
    # Get elements
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    return {
        "id": scene.id,
        "project_id": scene.project_id,
        "name": scene.name,
        "scene_type": scene.scene_type,
        "canvas_width": scene.canvas_width,
        "canvas_height": scene.canvas_height,
        "background_color": scene.background_color,
        "theme_id": scene.theme_id,
        "layout_data": scene.layout_data,
        "thumbnail_url": scene.thumbnail_url,
        "elements": elements,
        "created_at": scene.created_at,
        "updated_at": scene.updated_at
    }


@router.patch("/scenes/{scene_id}", response_model=SceneResponse)
def patch_scene(
    scene_id: UUID,
    scene_data: SceneUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Partial update scene (name, background_color, theme_id only)."""
    return update_scene(scene_id, scene_data, current_user, db)


@router.delete("/scenes/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scene(
    scene_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a scene."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(scene.project_id, current_user.id, db)
    
    scene.is_active = False
    scene.updated_at = datetime.utcnow()
    db.commit()
    
    return None


@router.post("/scenes/{scene_id}/duplicate", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
def duplicate_scene(
    scene_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a scene."""
    original = db.get(Scene, scene_id)
    
    if not original or not original.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(original.project_id, current_user.id, db)
    
    # Create new scene
    new_scene = Scene(
        project_id=original.project_id,
        name=f"Copy of {original.name}",
        scene_type=original.scene_type,
        canvas_width=original.canvas_width,
        canvas_height=original.canvas_height,
        background_color=original.background_color,
        theme_id=original.theme_id,
        layout_data=original.layout_data
    )
    db.add(new_scene)
    db.commit()
    db.refresh(new_scene)
    
    # Copy elements
    original_elements = db.execute(
        select(Element).where(Element.scene_id == original.id)
    ).scalars().all()
    
    for element in original_elements:
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
    db.refresh(new_scene)
    
    # Get elements for response
    elements = db.execute(
        select(Element).where(Element.scene_id == new_scene.id)
    ).scalars().all()
    
    return {
        "id": new_scene.id,
        "project_id": new_scene.project_id,
        "name": new_scene.name,
        "scene_type": new_scene.scene_type,
        "canvas_width": new_scene.canvas_width,
        "canvas_height": new_scene.canvas_height,
        "background_color": new_scene.background_color,
        "theme_id": new_scene.theme_id,
        "layout_data": new_scene.layout_data,
        "thumbnail_url": new_scene.thumbnail_url,
        "elements": elements,
        "created_at": new_scene.created_at,
        "updated_at": new_scene.updated_at
    }
