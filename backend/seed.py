"""Database seeding script for default themes and templates."""
from sqlmodel import Session
from app.db.database import engine
from app.models.models import Theme, Template, TemplateScene


def seed_themes():
    """Seed default themes."""
    themes = [
        Theme(
            name="Dark Modern",
            is_system=True,
            color_primary="#6366f1",
            color_secondary="#06b6d4",
            color_background="#0f0f0f",
            color_surface="#1a1a1a",
            color_text="#ffffff",
            color_text_muted="#a1a1aa",
            font_heading="Inter",
            font_body="Inter",
        ),
        Theme(
            name="Neon Future",
            is_system=True,
            color_primary="#00f5ff",
            color_secondary="#ff00ff",
            color_background="#0a0a0f",
            color_surface="#12121a",
            color_text="#ffffff",
            color_text_muted="#888899",
            font_heading="Orbitron",
            font_body="Inter",
        ),
        Theme(
            name="Cozy Warm",
            is_system=True,
            color_primary="#ff6b35",
            color_secondary="#f7931e",
            color_background="#1a1512",
            color_surface="#2d241e",
            color_text="#faf6f1",
            color_text_muted="#b8a99a",
            font_heading="Poppins",
            font_body="Inter",
        ),
        Theme(
            name="Minimal Light",
            is_system=True,
            color_primary="#18181b",
            color_secondary="#71717a",
            color_background="#fafafa",
            color_surface="#ffffff",
            color_text="#18181b",
            color_text_muted="#71717a",
            font_heading="Inter",
            font_body="Inter",
        ),
        Theme(
            name="Purple Dream",
            is_system=True,
            color_primary="#a855f7",
            color_secondary="#ec4899",
            color_background="#0f0518",
            color_surface="#1a0f2e",
            color_text="#faf5ff",
            color_text_muted="#a855f7",
            font_heading="Poppins",
            font_body="Inter",
        ),
    ]
    return themes


def seed_templates():
    """Seed default templates."""
    templates = []
    
    # Gaming setup template
    gaming_template = Template(
        name="Standard Gaming",
        description="Classic gaming layout with webcam, chat, and gameplay areas",
        template_type="single_scene",
        category="gaming",
        is_system=True,
    )
    templates.append((gaming_template, [
        TemplateScene(
            name="Gaming Scene",
            scene_type="live",
            layout_data={
                "version": "1.0",
                "elements": [
                    {
                        "type": "webcam",
                        "x": 20,
                        "y": 860,
                        "width": 320,
                        "height": 180,
                        "z_index": 2,
                        "properties": {
                            "border_radius": 8,
                            "border_width": 2,
                            "border_color": "#6366f1",
                        },
                    },
                    {
                        "type": "chat",
                        "x": 1420,
                        "y": 580,
                        "width": 460,
                        "height": 460,
                        "z_index": 1,
                        "properties": {
                            "font_family": "Inter",
                            "font_size": 14,
                            "text_color": "#ffffff",
                            "background_color": "#1a1a1acc",
                            "border_radius": 8,
                        },
                    },
                    {
                        "type": "panel",
                        "x": 10,
                        "y": 850,
                        "width": 340,
                        "height": 200,
                        "z_index": 0,
                        "properties": {
                            "background_color": "#0f0f0f",
                            "border_radius": 12,
                            "opacity": 0.9,
                        },
                    },
                ],
            },
        ),
    ]))
    
    # Just Chatting template
    chatting_template = Template(
        name="Just Chatting",
        description="Focused layout for conversation streams with centered webcam",
        template_type="single_scene",
        category="chatting",
        is_system=True,
    )
    templates.append((chatting_template, [
        TemplateScene(
            name="Chatting Scene",
            scene_type="live",
            layout_data={
                "version": "1.0",
                "elements": [
                    {
                        "type": "webcam",
                        "x": 560,
                        "y": 200,
                        "width": 800,
                        "height": 450,
                        "z_index": 1,
                        "properties": {
                            "border_radius": 16,
                            "border_width": 3,
                            "border_color": "#6366f1",
                        },
                    },
                    {
                        "type": "chat",
                        "x": 20,
                        "y": 580,
                        "width": 500,
                        "height": 460,
                        "z_index": 2,
                        "properties": {
                            "font_family": "Inter",
                            "font_size": 16,
                            "text_color": "#ffffff",
                            "background_color": "#1a1a1acc",
                            "border_radius": 12,
                        },
                    },
                    {
                        "type": "text",
                        "x": 560,
                        "y": 680,
                        "width": 800,
                        "height": 60,
                        "z_index": 3,
                        "properties": {
                            "content": "Live Chat",
                            "font_family": "Poppins",
                            "font_size": 32,
                            "font_weight": "bold",
                            "text_color": "#6366f1",
                            "text_align": "center",
                        },
                    },
                ],
            },
        ),
    ]))
    
    # Starting Soon template
    starting_template = Template(
        name="Starting Soon",
        description="Pre-stream scene with countdown and social links",
        template_type="single_scene",
        category="intermission",
        is_system=True,
    )
    templates.append((starting_template, [
        TemplateScene(
            name="Starting Soon",
            scene_type="starting_soon",
            layout_data={
                "version": "1.0",
                "elements": [
                    {
                        "type": "text",
                        "x": 460,
                        "y": 300,
                        "width": 1000,
                        "height": 80,
                        "z_index": 1,
                        "properties": {
                            "content": "Starting Soon",
                            "font_family": "Poppins",
                            "font_size": 64,
                            "font_weight": "bold",
                            "text_color": "#ffffff",
                            "text_align": "center",
                        },
                    },
                    {
                        "type": "text",
                        "x": 560,
                        "y": 420,
                        "width": 800,
                        "height": 40,
                        "z_index": 1,
                        "properties": {
                            "content": "Stream begins in a few minutes...",
                            "font_family": "Inter",
                            "font_size": 20,
                            "text_color": "#a1a1aa",
                            "text_align": "center",
                        },
                    },
                    {
                        "type": "panel",
                        "x": 660,
                        "y": 500,
                        "width": 600,
                        "height": 100,
                        "z_index": 0,
                        "properties": {
                            "background_color": "#1a1a1a",
                            "border_radius": 12,
                            "opacity": 0.8,
                        },
                    },
                ],
            },
        ),
    ]))
    
    # BRB template
    brb_template = Template(
        name="Be Right Back",
        description="Intermission scene for breaks",
        template_type="single_scene",
        category="intermission",
        is_system=True,
    )
    templates.append((brb_template, [
        TemplateScene(
            name="BRB",
            scene_type="brb",
            layout_data={
                "version": "1.0",
                "elements": [
                    {
                        "type": "text",
                        "x": 560,
                        "y": 400,
                        "width": 800,
                        "height": 100,
                        "z_index": 1,
                        "properties": {
                            "content": "Be Right Back",
                            "font_family": "Poppins",
                            "font_size": 72,
                            "font_weight": "bold",
                            "text_color": "#ffffff",
                            "text_align": "center",
                        },
                    },
                    {
                        "type": "text",
                        "x": 660,
                        "y": 520,
                        "width": 600,
                        "height": 40,
                        "z_index": 1,
                        "properties": {
                            "content": "Taking a quick break!",
                            "font_family": "Inter",
                            "font_size": 18,
                            "text_color": "#a1a1aa",
                            "text_align": "center",
                        },
                    },
                ],
            },
        ),
    ]))
    
    # Stream Ending template
    ending_template = Template(
        name="Stream Ending",
        description="Thank you and goodbye scene",
        template_type="single_scene",
        category="intermission",
        is_system=True,
    )
    templates.append((ending_template, [
        TemplateScene(
            name="Ending",
            scene_type="ending",
            layout_data={
                "version": "1.0",
                "elements": [
                    {
                        "type": "text",
                        "x": 560,
                        "y": 350,
                        "width": 800,
                        "height": 80,
                        "z_index": 1,
                        "properties": {
                            "content": "Thanks for Watching!",
                            "font_family": "Poppins",
                            "font_size": 56,
                            "font_weight": "bold",
                            "text_color": "#ffffff",
                            "text_align": "center",
                        },
                    },
                    {
                        "type": "text",
                        "x": 660,
                        "y": 450,
                        "width": 600,
                        "height": 100,
                        "z_index": 1,
                        "properties": {
                            "content": "Follow for more streams\nSee you next time!",
                            "font_family": "Inter",
                            "font_size": 18,
                            "text_color": "#a1a1aa",
                            "text_align": "center",
                        },
                    },
                ],
            },
        ),
    ]))
    
    return templates


def seed_database():
    """Seed database with default data."""
    with Session(engine) as session:
        # Check if themes already exist
        existing_themes = session.query(Theme).where(Theme.is_system == True).first()
        if not existing_themes:
            print("Seeding themes...")
            themes = seed_themes()
            for theme in themes:
                session.add(theme)
            session.commit()
            print(f"Added {len(themes)} default themes")
        else:
            print("Themes already seeded, skipping...")
        
        # Check if templates already exist
        existing_templates = session.query(Template).where(Template.is_system == True).first()
        if not existing_templates:
            print("Seeding templates...")
            templates_data = seed_templates()
            for template, scenes in templates_data:
                session.add(template)
                session.flush()  # Get template ID
                for scene in scenes:
                    scene.template_id = template.id
                    session.add(scene)
            session.commit()
            print(f"Added {len(templates_data)} default templates")
        else:
            print("Templates already seeded, skipping...")
        
        print("Seeding complete!")


if __name__ == "__main__":
    seed_database()
