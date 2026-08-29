"""
AegisMesh — FastAPI Application Entry Point
Traces to: docs/architecture/aegismesh-design.md Section 2
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.v1.endpoints import router as api_v1_router

app = FastAPI(
    title="AegisMesh Security Engine API",
    description=(
        "Zero-Trust Policy Evaluation, Multi-Factor Risk Assessment, and "
        "Automated Blast-Radius Containment Engine for Hybrid Enterprise Environments. "
        "[SIMULATION MODE: Packet Tracer DC Architecture + Simulated AWS/K8s Telemetry]"
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 REST API routes
app.include_router(api_v1_router)

# Mount frontend directory for static assets
current_dir = os.path.dirname(os.path.abspath(__file__))
# AegisMesh root is 2 levels up from backend/app
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
frontend_dir = os.path.join(project_root, "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "AegisMesh API Online", "dashboard": "frontend/index.html not found"}
