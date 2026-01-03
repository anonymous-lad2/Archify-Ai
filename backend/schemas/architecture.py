from pydantic import BaseModel
from typing import Dict, List

class ArchitectureRequest(BaseModel):
    query: str
    level: str  # HLD or LLD

class ArchitectureResponse(BaseModel):
    topic: str
    level: str
    components: Dict
    relationships: List
    resources: List[str]