"""Export API endpoints."""
import json
import io
import base64
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.v1.auth import get_current_active_user
from app.api.v1.scenes import check_project_access
from app.db.database import get_db
from app.models.models import User, Scene, Element
from app.models.schemas import (
    PNGExportRequest,
    PNGExportResponse,
    JSONExportResponse
)

router = APIRouter()


@router.post("/scenes/{scene_id}/export/png", response_model=PNGExportResponse)
def export_png(
    scene_id: UUID,
    export_request: PNGExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export scene as PNG image."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(scene.project_id, current_user.id, db)
    
    # Check if scene has elements
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    if not elements:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot export empty scene - add at least one element"
        )
    
    # In a real implementation, this would render the scene to an image
    # For now, return a mock download URL
    
    width = int(scene.canvas_width * export_request.scale)
    height = int(scene.canvas_height * export_request.scale)
    
    # Generate mock download URL (in production, this would be an S3 URL)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    return {
        "download_url": f"/api/v1/download/png/{scene_id}?token=mock_token&scale={export_request.scale}",
        "expires_at": expires_at,
        "width": width,
        "height": height
    }


@router.post("/scenes/{scene_id}/export/json", response_model=JSONExportResponse)
def export_json(
    scene_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export scene as JSON for OBS Studio."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(scene.project_id, current_user.id, db)
    
    # Get elements
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    # Build OBS-compatible export
    obs_elements = []
    for el in elements:
        obs_element = {
            "id": str(el.id),
            "type": _map_element_type(el.element_type),
            "name": el.name,
            "pos": {"x": el.position_x, "y": el.position_y},
            "size": {"width": el.width, "height": el.height},
            "visible": el.is_visible,
            "streambuldr_meta": {
                "element_type": el.element_type,
                "z_index": el.z_index,
                **el.properties
            }
        }
        obs_elements.append(obs_element)
    
    export_data = {
        "streambuldr_version": "1.0",
        "name": scene.name,
        "canvas": {
            "width": scene.canvas_width,
            "height": scene.canvas_height,
            "background_color": scene.background_color
        },
        "elements": obs_elements,
        "sources": [],
        "transitions": []
    }
    
    # In production, this would upload to S3 and return a download URL
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    return {
        "download_url": f"/api/v1/download/json/{scene_id}?token=mock_token",
        "expires_at": expires_at,
        "format": "obs-studio",
        "version": "1.0"
    }


def _map_element_type(element_type: str) -> str:
    """Map StreamBldr element types to OBS source types."""
    mapping = {
        "webcam": "video_capture",
        "chat": "browser_source",
        "alert": "browser_source",
        "text": "text_gdiplus",
        "image": "image_source",
        "panel": "color_source"
    }
    return mapping.get(element_type, "unknown")


@router.get("/download/json/{scene_id}")
def download_json(
    scene_id: UUID,
    token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download scene JSON file."""
    scene = db.get(Scene, scene_id)
    
    if not scene or not scene.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    check_project_access(scene.project_id, current_user.id, db)
    
    # Get elements
    elements = db.execute(
        select(Element).where(Element.scene_id == scene.id)
    ).scalars().all()
    
    obs_elements = []
    for el in elements:
        obs_element = {
            "id": str(el.id),
            "type": _map_element_type(el.element_type),
            "name": el.name,
            "pos": {"x": el.position_x, "y": el.position_y},
            "size": {"width": el.width, "height": el.height},
            "visible": el.is_visible,
            "streambuldr_meta": {
                "element_type": el.element_type,
                "z_index": el.z_index,
                **el.properties
            }
        }
        obs_elements.append(obs_element)
    
    export_data = {
        "streambuldr_version": "1.0",
        "name": scene.name,
        "canvas": {
            "width": scene.canvas_width,
            "height": scene.canvas_height,
            "background_color": scene.background_color
        },
        "elements": obs_elements,
        "sources": [],
        "transitions": []
    }
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f'attachment; filename="{scene.name.replace(" ", "_")}_scene.json"'
        }
    )
