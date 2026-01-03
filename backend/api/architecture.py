from fastapi import APIRouter
from backend.schemas.architecture import ArchitectureRequest, ArchitectureResponse
from backend.api.topic_extractor import extract_topic

generate_architecture_router = APIRouter(
    prefix="/architecture",
    tags=["Architecture"]
)

@generate_architecture_router.post("/generate", response_model=ArchitectureResponse)
def generate_architecture(req: ArchitectureRequest):
    topic = extract_topic(req.query)

    return ArchitectureResponse(
        topic=topic,
        level=req.level,
        components={},
        relationships=[]
    )
