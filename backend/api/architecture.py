from fastapi import APIRouter
from backend.schemas.architecture import ArchitectureRequest, ArchitectureResponse
from backend.api.topic_extractor import extract_topic
from backend.api.resource_links import get_resource_links
from backend.api.scraper import scrape_multiple
from backend.api.architecture_generator import generate_architecture
from backend.api.svg_diagram_generator import generate_svg_diagram

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

    # Generate SVG diagram from the architecture response
    try:
        diagram_filename = f"{topic.lower().replace(' ', '_')}_{req.level}_diagram"
        normalized_arch = normalize_for_diagram(architecture)
        diagram_data = {
        'topic': f"{topic} - {req.level.upper()}",
        'components': normalized_arch["components"],
        'relationships': normalized_arch["relationships"]
        }
        svg_content = generate_svg_diagram(
            data=diagram_data,
            output=diagram_filename
        )
        print(f"✅ SVG diagram generated: {diagram_filename}.svg")
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


def normalize_for_diagram(architecture: dict) -> dict:
    """
    Minimal normalization to improve diagram quality
    without changing original architecture output.
    """

    components = architecture.get("components", {})
    relationships = architecture.get("relationships", [])

    for name, comp in components.items():
        ctype = comp.get("type", "")

        if ctype in ["client", "frontend"]:
            comp["layer"] = "client"
        elif ctype in ["gateway", "load_balancer"]:
            comp["layer"] = "edge"
        elif ctype in ["microservice", "service"]:
            comp["layer"] = "service"
        elif ctype in ["database", "cache"]:
            comp["layer"] = "data"
        else:
            comp["layer"] = "external"

        # IMPORTANT: remove LLM visual noise
        comp.pop("shape", None)
        comp.pop("color", None)

    # Remove unreliable visual hints from edges
    for rel in relationships:
        rel.pop("line", None)

    return {
        "components": components,
        "relationships": relationships
    }
