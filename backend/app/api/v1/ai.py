"""AI generation API endpoints."""
import re
import json
from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_active_user
from app.db.database import get_db
from app.core.config import get_settings
from app.models.models import User, AIGeneration
from app.models.schemas import AIGenerateRequest, AIGenerationResponse

router = APIRouter()


AI_SYSTEM_PROMPT = """You are an expert streaming scene designer. Your task is to generate professional OBS/streaming layouts based on user descriptions.

RULES:
1. Always return valid JSON matching the SceneLayout schema
2. Ensure all element positions are within the canvas bounds (0 to canvas_width/height)
3. Elements should not overlap significantly (min 10px spacing preferred)
4. Use appropriate default sizes for each element type:
   - webcam: 320x180 or 480x270 (16:9)
   - chat: 300x400 to 450x500
   - alert: 400x150
   - text: based on content length, font_size * char_count
   - image: varies by use case
   - panel: depends on purpose
5. Apply the requested style through colors, fonts, and spacing
6. Use logical positioning (webcam usually corner, chat side, gameplay center)
7. All color values must be valid hex codes (#RRGGBB)
8. Font families: prefer "Inter", "Poppins", "Orbitron", "Roboto", "Open Sans"

SCENE TYPES:
- starting_soon: Countdown/timer area prominent, minimal clutter
- live: Balanced layout with webcam, chat, and gameplay space
- brb: Centered message, minimal elements, maybe timer
- ending: Thank you message, social links, schedule
- custom: User-defined purpose

OUTPUT FORMAT:
You must return ONLY a JSON object with this exact structure:
{
  "name": "Scene name",
  "scene_type": "live|starting_soon|brb|ending|custom",
  "background_color": "#RRGGBB",
  "theme": {
    "name": "Theme name",
    "color_primary": "#RRGGBB",
    "color_secondary": "#RRGGBB",
    "color_background": "#RRGGBB",
    "color_surface": "#RRGGBB",
    "color_text": "#RRGGBB",
    "color_text_muted": "#RRGGBB",
    "font_heading": "Font Name",
    "font_body": "Font Name"
  },
  "layout": {
    "version": "1.0",
    "elements": [
      {
        "type": "webcam|chat|alert|text|image|panel",
        "x": integer,
        "y": integer,
        "width": integer,
        "height": integer,
        "z_index": integer,
        "properties": { /* element-specific */ }
      }
    ]
  }
}

STYLES:
- minimal: Clean lines, lots of whitespace, monochrome or single accent color
- futuristic: Neon accents (#00f5ff, #ff00ff), dark backgrounds, sharp edges
- cozy: Warm colors (#ffaa00, #ff5500), rounded corners, soft shadows
- professional: Blues (#0066ff), grays, clean typography, structured layout
- vibrant: High contrast, bold colors (#ff006e, #00ff00), energetic
- retro: Pixel fonts, scanlines, CRT effects, 90s gaming aesthetic"""


def validate_hex_color(color: str) -> bool:
    """Validate hex color format."""
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


def validate_element_position(element: dict, canvas_width: int, canvas_height: int) -> list:
    """Validate element is within canvas bounds."""
    errors = []
    x = element.get("x", 0)
    y = element.get("y", 0)
    width = element.get("width", 0)
    height = element.get("height", 0)
    
    if x < 0:
        errors.append(f"Element x position {x} is negative")
    if y < 0:
        errors.append(f"Element y position {y} is negative")
    if x + width > canvas_width:
        errors.append(f"Element extends beyond canvas width ({x + width} > {canvas_width})")
    if y + height > canvas_height:
        errors.append(f"Element extends beyond canvas height ({y + height} > {canvas_height})")
    
    return errors


def auto_correct_layout(layout_data: dict, canvas_width: int, canvas_height: int) -> dict:
    """Auto-correct layout issues."""
    elements = layout_data.get("layout", {}).get("elements", [])
    
    for i, element in enumerate(elements):
        # Clamp positions
        element["x"] = max(0, min(element.get("x", 0), canvas_width - 20))
        element["y"] = max(0, min(element.get("y", 0), canvas_height - 20))
        
        # Clamp sizes
        element["width"] = min(element.get("width", 100), canvas_width - element["x"])
        element["height"] = min(element.get("height", 100), canvas_height - element["y"])
        
        # Ensure z-index exists
        if "z_index" not in element:
            element["z_index"] = i
        
        elements[i] = element
    
    layout_data["layout"]["elements"] = elements
    return layout_data


async def generate_scene_with_ai(prompt: str, style: Optional[str], canvas_width: int, canvas_height: int) -> dict:
    """Generate scene layout using AI."""
    settings = get_settings()
    
    if not settings.openai_api_key:
        # Return mock response for development
        return {
            "name": "AI Generated Scene",
            "scene_type": "live",
            "background_color": "#1a1a1a",
            "theme": {
                "name": "AI Theme",
                "color_primary": "#4f46e5",
                "color_secondary": "#06b6d4",
                "color_background": "#1a1a1a",
                "color_surface": "#2a2a2a",
                "color_text": "#ffffff",
                "color_text_muted": "#a1a1aa",
                "font_heading": "Inter",
                "font_body": "Inter"
            },
            "layout": {
                "version": "1.0",
                "elements": [
                    {
                        "type": "webcam",
                        "x": 50,
                        "y": 750,
                        "width": 320,
                        "height": 180,
                        "z_index": 1,
                        "properties": {
                            "border_radius": 8,
                            "border_width": 2,
                            "border_color": "#4f46e5"
                        }
                    },
                    {
                        "type": "chat",
                        "x": 1450,
                        "y": 600,
                        "width": 420,
                        "height": 420,
                        "z_index": 2,
                        "properties": {
                            "font_family": "Inter",
                            "font_size": 14,
                            "text_color": "#ffffff",
                            "background_color": "#2a2a2acc",
                            "border_radius": 8
                        }
                    },
                    {
                        "type": "text",
                        "x": 960,
                        "y": 50,
                        "width": 400,
                        "height": 60,
                        "z_index": 3,
                        "properties": {
                            "content": "Live Stream",
                            "font_family": "Inter",
                            "font_size": 36,
                            "font_weight": "bold",
                            "text_color": "#4f46e5",
                            "text_align": "center"
                        }
                    }
                ]
            }
        }
    
    try:
        import openai
        openai.api_key = settings.openai_api_key
        
        user_prompt = f"""Create a streaming layout based on this description: {prompt}

Canvas size: {canvas_width}x{canvas_height}
Style: {style or "professional"}

Generate a complete scene layout with appropriate elements and styling."""
        
        response = openai.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")


@router.post("/ai/generate-scene", response_model=AIGenerationResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_scene(
    request: AIGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a scene layout using AI."""
    # Create generation record
    generation = AIGeneration(
        user_id=current_user.id,
        prompt=request.prompt,
        style_hint=request.style,
        status="pending"
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    # Start async generation
    background_tasks.add_task(
        process_generation,
        generation.id,
        request.prompt,
        request.style,
        request.canvas_width,
        request.canvas_height,
        db
    )
    
    return {
        "id": generation.id,
        "status": "pending",
        "prompt": request.prompt,
        "style_hint": request.style,
        "created_at": generation.created_at,
        "processing_time_ms": None,
        "result": None,
        "error_message": None,
        "completed_at": None
    }


async def process_generation(
    generation_id: UUID,
    prompt: str,
    style: Optional[str],
    canvas_width: int,
    canvas_height: int,
    db: Session
):
    """Process AI generation in background."""
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        generation = db.get(AIGeneration, generation_id)
        if not generation:
            return
        
        start_time = datetime.utcnow()
        
        try:
            # Generate layout
            result = await generate_scene_with_ai(prompt, style, canvas_width, canvas_height)
            
            # Validate and auto-correct
            result = auto_correct_layout(result, canvas_width, canvas_height)
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update generation record
            generation.status = "success"
            generation.generated_layout = result
            generation.processing_time_ms = processing_time
            generation.completed_at = datetime.utcnow()
            
        except Exception as e:
            generation.status = "error"
            generation.error_message = str(e)
            generation.completed_at = datetime.utcnow()
        
        db.commit()
        
    finally:
        db.close()


@router.get("/ai/generations/{generation_id}", response_model=AIGenerationResponse)
def get_generation_status(
    generation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check generation status and retrieve result."""
    generation = db.get(AIGeneration, generation_id)
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    if generation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this generation"
        )
    
    return {
        "id": generation.id,
        "status": generation.status,
        "prompt": generation.prompt,
        "style_hint": generation.style_hint,
        "created_at": generation.created_at,
        "processing_time_ms": generation.processing_time_ms,
        "result": generation.generated_layout if generation.status == "success" else None,
        "error_message": generation.error_message if generation.status == "error" else None,
        "completed_at": generation.completed_at
    }
