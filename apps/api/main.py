from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from apps.api.core.config import settings
from apps.api.core.database import check_db_health, Base, engine
from apps.api.core.redis import check_redis_health
from apps.api.routes.reports import router as reports_router
from apps.api.routes.spatial import router as spatial_router
from apps.api.routes.clusters import router as clusters_router

# Ensure tables are ready on boot
Base.metadata.create_all(bind=engine)

def create_app() -> FastAPI:
    app = FastAPI(
        title="CitySense Civic Impact API",
        description="Intelligent Municipal Infrastructure & Rapid Action Platform (From Complaints to Action)",
        version="0.1.0"
    )

    # CORS Middleware allowing Next.js web client
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files for uploaded evidence & demo media
    uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

    # Health Check Endpoints
    @app.get("/", tags=["Health"])
    def root():
        return {
            "platform": "CitySense",
            "mission": "From Complaints to Action",
            "status": "operational",
            "docs": "/docs"
        }

    @app.get("/api/health/db", tags=["Health"])
    def health_db():
        return check_db_health()

    @app.get("/api/health/redis", tags=["Health"])
    async def health_redis():
        return await check_redis_health()

    # Mount Route Collections
    app.include_router(reports_router)
    app.include_router(spatial_router)
    app.include_router(clusters_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)

