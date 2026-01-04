from fastapi import APIRouter
from backend.schemas.architecture import ArchitectureRequest, ArchitectureResponse
from backend.api.topic_extractor import extract_topic
from backend.api.resource_links import get_resource_links
from backend.api.scraper import scrape_multiple
from backend.api.architecture_generator import generate_architecture

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

    return ArchitectureResponse(
        topic=topic,
        level=req.level,
        components=architecture.get("components", {}),
        relationships=architecture.get("relationships", []),
        resources=valid_links,
        raw_content=raw_content[:2000] if raw_content else "No content available"
    )