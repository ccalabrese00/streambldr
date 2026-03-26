# AI Prompt Specifications - AI Stream Scene Builder

## Overview
AI scene generation uses structured prompts to generate valid scene layouts. The system validates AI output against a JSON schema before returning to the user.

---

## System Prompt

```
You are an expert streaming scene designer. Your task is to generate professional OBS/streaming layouts based on user descriptions.

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
        "properties": { /* type-specific */ }
      }
    ]
  }
}

ELEMENT PROPERTIES BY TYPE:
- webcam: border_radius (0-50), border_width (0-5), border_color, background_color, aspect_ratio
- chat: font_family, font_size (10-24), text_color, background_color, border_radius, max_messages
- alert: animation_type (slide_in|fade_in|bounce), duration_seconds, font_family, font_size, text_color
- text: content, font_family, font_size (12-72), font_weight, text_color, text_align, text_transform
- image: src, alt, object_fit (contain|cover|fill), border_radius
- panel: background_color, border_radius, border_width, border_color, opacity (0.0-1.0)

STYLES:
- minimal: Clean lines, lots of whitespace, monochrome or single accent color
- futuristic: Neon accents (#00f5ff, #ff00ff), dark backgrounds, sharp edges
- cozy: Warm colors (#ffaa00, #ff5500), rounded corners, soft shadows
- professional: Blues (#0066ff), grays, clean typography, structured layout
- vibrant: High contrast, bold colors (#ff006e, #00ff00), energetic
- retro: Pixel fonts, scanlines, CRT effects, 90s gaming aesthetic

CANVAS BOUNDS CHECK:
- Every element must satisfy: 0 <= x and x + width <= canvas_width
- Every element must satisfy: 0 <= y and y + height <= canvas_height

AVOID:
- Overlapping elements (unless intentional like overlay effects)
- Elements that go off-canvas
- Invalid hex colors
- Empty or null required fields
```

---

## User Prompt Structure

**Basic Format:**
```
Create a [style] streaming layout with [key elements]. 
[Webcam position], [chat position], [additional details].
[Color preferences or theme description].
```

**Example Prompts:**

1. **Gaming Setup:**
```
Create a futuristic gaming setup with a webcam in the bottom left corner, 
chat on the right side, and a large central area for gameplay. 
Use a dark theme with neon blue accents.
```

2. **Just Chatting:**
```
Create a cozy just chatting layout with a prominent webcam in the center-left, 
small chat widget bottom right, and my logo in the top left. 
Warm amber and brown color scheme, very homey feeling.
```

3. **Starting Soon:**
```
Create a starting soon screen with a large countdown timer in the center, 
small webcam preview bottom right, and my social handles at the bottom. 
Dark purple theme with electric pink accents.
```

4. **BRB Screen:**
```
Create a BRB screen with "Be Right Back" text center, 
a small animated area for looping video/gif on the left, 
and a progress bar at the bottom. Minimal black and white design.
```

---

## JSON Schema (Validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "scene_type", "background_color", "theme", "layout"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "scene_type": {
      "type": "string",
      "enum": ["starting_soon", "live", "brb", "ending", "custom"]
    },
    "background_color": {
      "type": "string",
      "pattern": "^#[0-9A-Fa-f]{6}$"
    },
    "theme": {
      "type": "object",
      "required": ["name", "color_primary", "color_secondary", "color_background", 
                   "color_surface", "color_text", "color_text_muted", "font_heading", "font_body"],
      "properties": {
        "name": { "type": "string" },
        "color_primary": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "color_secondary": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "color_background": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "color_surface": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "color_text": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "color_text_muted": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
        "font_heading": { "type": "string" },
        "font_body": { "type": "string" }
      }
    },
    "layout": {
      "type": "object",
      "required": ["version", "elements"],
      "properties": {
        "version": { "type": "string", "enum": ["1.0"] },
        "elements": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["type", "x", "y", "width", "height", "z_index", "properties"],
            "properties": {
              "type": { "type": "string", "enum": ["webcam", "chat", "alert", "text", "image", "panel"] },
              "x": { "type": "integer", "minimum": 0 },
              "y": { "type": "integer", "minimum": 0 },
              "width": { "type": "integer", "minimum": 20 },
              "height": { "type": "integer", "minimum": 20 },
              "z_index": { "type": "integer", "minimum": 0 },
              "properties": { "type": "object" }
            }
          }
        }
      }
    }
  }
}
```

---

## AI Provider Configuration

**Primary Provider:** OpenAI GPT-4

**Parameters:**
```json
{
  "model": "gpt-4-turbo-preview",
  "temperature": 0.7,
  "max_tokens": 2000,
  "response_format": { "type": "json_object" },
  "timeout_seconds": 30
}
```

**Fallback Provider:** Claude (Anthropic)

**Parameters:**
```json
{
  "model": "claude-3-opus-20240229",
  "max_tokens": 2000,
  "temperature": 0.7,
  "timeout_seconds": 30
}
```

---

## Error Handling

**Invalid Prompt:**
```json
{
  "error": "INVALID_PROMPT",
  "message": "Could not generate layout from prompt",
  "suggestion": "Try describing specific elements and their positions"
}
```

**Invalid AI Output (Schema Violation):**
```json
{
  "error": "GENERATION_FAILED",
  "message": "AI generated invalid layout structure",
  "details": [
    "Element 0: x position 2000 exceeds canvas width 1920",
    "Theme color_primary is not a valid hex code"
  ],
  "retry_allowed": true
}
```

**Timeout:**
```json
{
  "error": "GENERATION_TIMEOUT",
  "message": "AI generation took too long",
  "retry_allowed": true
}
```

**Rate Limit:**
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many generation requests",
  "retry_after_seconds": 360
}
```

---

## Validation Rules

### Position Validation
```python
def validate_element_position(element, canvas_width, canvas_height):
    errors = []
    
    if element['x'] < 0:
        errors.append(f"Element {element['id']}: x position {element['x']} is negative")
    
    if element['y'] < 0:
        errors.append(f"Element {element['id']}: y position {element['y']} is negative")
    
    if element['x'] + element['width'] > canvas_width:
        errors.append(f"Element {element['id']}: right edge extends beyond canvas")
    
    if element['y'] + element['height'] > canvas_height:
        errors.append(f"Element {element['id']}: bottom edge extends beyond canvas")
    
    return errors
```

### Overlap Detection
```python
def detect_overlaps(elements, min_spacing=10):
    overlaps = []
    
    for i, el1 in enumerate(elements):
        for el2 in elements[i+1:]:
            # Check for overlap
            if (el1['x'] < el2['x'] + el2['width'] + min_spacing and
                el1['x'] + el1['width'] > el2['x'] - min_spacing and
                el1['y'] < el2['y'] + el2['height'] + min_spacing and
                el1['y'] + el1['height'] > el2['y'] - min_spacing):
                overlaps.append((el1['id'], el2['id']))
    
    return overlaps
```

### Color Validation
```python
import re

HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')

def validate_hex_color(color, field_name):
    if not HEX_COLOR_PATTERN.match(color):
        return f"{field_name}: '{color}' is not a valid hex color (expected #RRGGBB)"
    return None
```

---

## Auto-Correction Rules

When AI output has minor issues, attempt auto-correction:

1. **Off-canvas elements:**
   - Clamp x to [0, canvas_width - width]
   - Clamp y to [0, canvas_height - height]

2. **Overlapping elements:**
   - Attempt to nudge by 10-50px
   - If still overlapping, flag for user review

3. **Invalid colors:**
   - Convert 3-digit hex to 6-digit (#fff → #ffffff)
   - Replace invalid colors with theme defaults

4. **Missing z-index:**
   - Assign incremental z-index based on array position

5. **Missing properties:**
   - Apply type-specific defaults

---

## Sample AI Output (Valid)

```json
{
  "name": "Cyberpunk Live Stream",
  "scene_type": "live",
  "background_color": "#0a0a0f",
  "theme": {
    "name": "Neon Cyberpunk",
    "color_primary": "#00f5ff",
    "color_secondary": "#ff006e",
    "color_background": "#0a0a0f",
    "color_surface": "#1a1a24",
    "color_text": "#ffffff",
    "color_text_muted": "#8a8a9a",
    "font_heading": "Orbitron",
    "font_body": "Inter"
  },
  "layout": {
    "version": "1.0",
    "elements": [
      {
        "type": "webcam",
        "x": 50,
        "y": 800,
        "width": 320,
        "height": 180,
        "z_index": 1,
        "properties": {
          "border_radius": 4,
          "border_width": 2,
          "border_color": "#00f5ff",
          "background_color": "#1a1a24",
          "aspect_ratio": "16:9"
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
          "background_color": "#1a1a24cc",
          "border_radius": 8,
          "max_messages": 10
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
          "content": "LIVE - Gaming Stream",
          "font_family": "Orbitron",
          "font_size": 36,
          "font_weight": "bold",
          "text_color": "#00f5ff",
          "text_align": "center",
          "text_transform": "uppercase"
        }
      }
    ]
  }
}
```

---

## Analytics Logging

Track AI generation attempts for improvement:

```json
{
  "generation_id": "uuid",
  "user_id": "uuid",
  "prompt": "user input",
  "style": "futuristic",
  "status": "success|error|timeout",
  "output": "...",
  "error_details": "...",
  "processing_time_ms": 3250,
  "corrections_applied": ["clamp_x", "default_properties"],
  "user_feedback": "accepted|rejected|edited"
}
```

---

## Version History

- v1.0 (2026-03-26): Initial AI prompt specifications
