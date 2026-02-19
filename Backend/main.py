# backend/main.py

import os
import sys
# Add the backend directory itself to sys.path so "db", "api", etc. resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from db.session import engine
from db.models import Base

from api.database import router as database_router
from api.projects import router as projects_router
from api.shelves import router as shelves_router
from api.accession import router as accession_router
from api.batch_print import router as batch_print_router
from api.items import router as items_router


# Create tables - always create in packaged mode or if ENV=dev
if getattr(sys, 'frozen', False) or os.getenv("ENV", "dev") == "dev":
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created/verified")

app = FastAPI(
    title="Accessioning App API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    debug=True  # Enable debug mode
)
# CORS (restrict origins before production)
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/api/docs")

@app.get("/openapi.json", include_in_schema=False)
async def openapi_redirect():
    return RedirectResponse(url="/api/openapi.json")

@app.get("/redoc", include_in_schema=False)
async def redoc_redirect():
    return RedirectResponse(url="/api/redoc")

app.include_router(
    database_router,
    prefix="/api",
    tags=["Database"],
)

app.include_router(
    projects_router,
    prefix="/api",
    tags=["Projects"],
)

app.include_router(
    shelves_router,
    prefix="/api",
    tags=["Shelves"],
)

app.include_router(
    accession_router,
    prefix="/api",
    tags=["Accessioning"],
)

app.include_router(
    batch_print_router,
    prefix="/api",
    tags=["Batch Printing"],
)

app.include_router(
    items_router,
    prefix="/api",
    tags=["Items"],
)

# Serve React static files (for production/packaged app)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    static_dir = os.path.join(sys._MEIPASS, "Frontend", "dist")
else:
    # Running as script
    static_dir = os.path.join(os.path.dirname(__file__), "..", "Frontend", "dist")

print(f"Looking for static files at: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")

if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        print(f"✓ Mounted /assets from {assets_dir}")
    
    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react(full_path: str = ""):
        # Don't serve React for API routes
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}, 404
        
        # Serve index.html for all other routes (React Router handles routing)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Not Found"}, 404
    
    print(f"✓ Serving React app from {static_dir}")
else:
    print(f"✗ Warning: Static directory not found at {static_dir}")
    print("  Frontend will not be available. API only mode.")


