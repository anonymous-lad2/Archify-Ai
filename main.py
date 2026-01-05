from fastapi import FastAPI
from backend.api.architecture import generate_architecture_router

app = FastAPI(
    title="Archify AI",
    description="HLD/LLD Architecture Generator",
    version="1.0.0"
)

app.include_router(generate_architecture_router)

@app.get("/")
def health():
    return {"status": "ok"}