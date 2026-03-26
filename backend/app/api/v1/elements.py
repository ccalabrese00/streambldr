"""Elements API endpoints."""
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.v1.auth import get_current_active_user
from app.api.v1.scenes import check_project_access
from app.db.database import get_db
from app.models.models import User, Scene, Element
from app.models.schemas import (
    ElementCreate,
    ElementUpdate,
    ElementResponse,
    ElementReorderRequest
)

router = APIRouter()


def check_scene_access(scene_id: UUID, user_id: UUID, db: Session) -> Scene:
    """Verify user has access to scene."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check project ownership
    check_project_access(scene.project_id, user_id, db)
    
    return scene


@router.get("/scenes/{scene_id}/elements", response_model=List[ElementResponse])
def list_elements(
    scene_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all elements in a scene (ordered by z_index)."""
    check_scene_access(scene_id, current_user.id, db)
    
    elements = db.execute(
        select(Element).where(
            Element.scene_id == scene_id
        ).order_by(Element.z_index.desc())
    ).scalars().all()
    
    return elements


@router.post("/scenes/{scene_id}/elements", response_model=ElementResponse, status_code=status.HTTP_201_CREATED)
def create_element(
    scene_id: UUID,
    element_data: ElementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new element to scene."""
    scene = check_scene_access(scene_id, current_user.id, db)
    
    # Validate element is within canvas bounds
    if element_data.position_x + element_data.width > scene.canvas_width:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Element extends beyond canvas width"
        )
    
    if element_data.position_y + element_data.height > scene.canvas_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Element extends beyond canvas height"
        )
    
    # Check for z-index conflicts and auto-adjust if needed
    existing_z = db.execute(
        select(Element.z_index).where(
            Element.scene_id == scene_id,
            Element.z_index == element_data.z_index
        )
    ).scalar_one_or_none()
    
    z_index = element_data.z_index
    if existing_z is not None:
        # Find next available z-index
        max_z = db.execute(
            select(Element.z_index).where(
                Element.scene_id == scene_id
            ).order_by(Element.z_index.desc())
        ).scalar()
        z_index = (max_z or 0) + 1
    
    element = Element(
        scene_id=scene_id,
        element_type=element_data.element_type,
        name=element_data.name,
        position_x=element_data.position_x,
        position_y=element_data.position_y,
        width=element_data.width,
        height=element_data.height,
        z_index=z_index,
        properties=element_data.properties,
        is_visible=element_data.is_visible
    )
    
    db.add(element)
    db.commit()
    db.refresh(element)
    
    return element


@router.put("/elements/{element_id}", response_model=ElementResponse)
def update_element(
    element_id: UUID,
    element_data: ElementUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an element."""
    element = db.get(Element, element_id)
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element not found"
        )
    
    # Check scene access
    scene = check_scene_access(element.scene_id, current_user.id, db)
    
    # Update fields
    if element_data.name is not None:
        element.name = element_data.name
    if element_data.position_x is not None:
        element.position_x = element_data.position_x
    if element_data.position_y is not None:
        element.position_y = element_data.position_y
    if element_data.width is not None:
        element.width = element_data.width
    if element_data.height is not None:
        element.height = element_data.height
    if element_data.z_index is not None:
        element.z_index = element_data.z_index
    if element_data.properties is not None:
        element.properties = element_data.properties
    if element_data.is_visible is not None:
        element.is_visible = element_data.is_visible
    
    # Validate bounds after update
    if element.position_x + element.width > scene.canvas_width:
        element.width = scene.canvas_width - element.position_x
    if element.position_y + element.height > scene.canvas_height:
        element.height = scene.canvas_height - element.position_y
    
    element.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(element)
    
    return element


@router.delete("/elements/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_element(
    element_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove an element."""
    element = db.get(Element, element_id)
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element not found"
        )
    
    check_scene_access(element.scene_id, current_user.id, db)
    
    db.delete(element)
    db.commit()
    
    return None


@router.post("/scenes/{scene_id}/elements/reorder")
def reorder_elements(
    scene_id: UUID,
    reorder_data: ElementReorderRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update z-index ordering for multiple elements."""
    check_scene_access(scene_id, current_user.id, db)
    
    updated_elements = []
    
    for order in reorder_data.orders:
        element_id = order.get("element_id")
        z_index = order.get("z_index")
        
        if not element_id or z_index is None:
            continue
        
        element = db.get(Element, element_id)
        if element and element.scene_id == scene_id:
            element.z_index = z_index
            element.updated_at = datetime.utcnow()
            updated_elements.append(element)
    
    db.commit()
    
    # Refresh all updated elements
    for element in updated_elements:
        db.refresh(element)
    
    return {"message": "Elements reordered", "updated_count": len(updated_elements)}
