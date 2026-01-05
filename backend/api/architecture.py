from fastapi import APIRouter
from backend.schemas.architecture import ArchitectureRequest, ArchitectureResponse
from backend.api.topic_extractor import extract_topic
from backend.api.resource_links import get_resource_links
from backend.api.scraper import scrape_multiple
from backend.api.architecture_generator import generate_architecture
from backend.api.svg_diagram_generator import generate_animated_svg_correct_flow
from backend.api.image_generator import generate_diagram

generate_architecture_router = APIRouter(
    prefix="/architecture",
    tags=["Architecture"]
)

@generate_architecture_router.post("/generate", response_model=ArchitectureResponse)
def generate_architecture_endpoint(req: ArchitectureRequest):
    topic = extract_topic(req.query)

    valid_links = get_resource_links(topic, req.level)

    raw_content = scrape_multiple(valid_links)

    architecture = generate_architecture(
        topic=topic,
        level=req.level,
        raw_content=raw_content
    )

    # Generate SVG and Image diagram from the architecture response
    try:
        diagram_filename = f"{topic.lower().replace(' ', '_')}_{req.level}_diagram"
        diagram_data = {
            'topic': f"{topic} - {req.level.upper()}",
            'components': architecture.get("components", {}),
            'relationships': architecture.get("relationships", [])
        }

        # generating SVG
        generate_animated_svg_correct_flow(config_path="backend/utils/design_rules.json",spec=diagram_data,output=f"{diagram_filename}.svg")

        # generating Image
        generate_diagram(config_path="backend/utils/design_rules.json",spec=diagram_data,output=f"{diagram_filename}.png")

    except Exception as e:
        print(f"⚠️ Diagram generation failed: {e}")

    return ArchitectureResponse(
        topic=topic,
        level=req.level,
        components=architecture.get("components", {}),
        relationships=architecture.get("relationships", []),
        resources=valid_links,
        raw_content=raw_content[:2000] if raw_content else "No content available"
    )