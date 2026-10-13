import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1.api import api_router
from backend.app.database.session import init_db, SessionLocal
from backend.app.models.models import Asset
from backend.app.sample_data.enterprise_topology import load_sample_topology

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyber_digital_twin")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered Cybersecurity Digital Twin for Vulnerability Assessment and Intelligent Risk Analysis. "
        "A final-year B.Tech academic software project mapping enterprise network topology, "
        "performing offline multi-hop attack path simulations (BFS/Dijkstra), contextual risk quantification, "
        "and what-if patch remediation analysis."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS Middleware
origins = ["*"] if not settings.BACKEND_CORS_ORIGINS else settings.BACKEND_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing Cyber Digital Twin SQLite database schema...")
    init_db()

    # Auto-seed initial enterprise sample data if database is empty
    db = SessionLocal()
    try:
        count = db.query(Asset).count()
        if count == 0:
            logger.info("Empty database detected. Seeding initial enterprise demonstration topology...")
            load_sample_topology(db)
            logger.info("Demonstration enterprise topology successfully seeded.")
        else:
            logger.info(f"Database contains {count} existing assets. Preserving stored state.")
    finally:
        db.close()

# Include versioned API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "AI-Powered Cybersecurity Digital Twin API is active",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
