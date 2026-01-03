from fastapi import APIRouter
from backend.schemas.architecture import ArchitectureRequest, ArchitectureResponse
from backend.api.topic_extractor import extract_topic
from backend.api.resource_links import get_resource_links

generate_architecture_router = APIRouter(
    prefix="/architecture",
    tags=["Architecture"]
)

@generate_architecture_router.post("/generate", response_model=ArchitectureResponse)
def generate_architecture(req: ArchitectureRequest):
    topic = extract_topic(req.query)
    links = get_resource_links(topic, req.level)

    return ArchitectureResponse(
        topic=topic,
        level=req.level,
        components={},
        relationships=[],
        resources=links
    )
