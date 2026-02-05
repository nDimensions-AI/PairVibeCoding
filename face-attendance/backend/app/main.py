"""
Face Attendance System - FastAPI Backend

High-speed, high-accuracy face recognition system for marking attendance
using Computer Vision with InsightFace (ArcFace) embeddings.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import registration, attendance, reports
from app.services.face_embedding import FaceEmbeddingService
from app.services.face_detection import FaceDetectionService
from app.services.liveness import LivenessService
from app.services.database import DatabaseService

import sys
sys.path.append("..")
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - initialize and cleanup services."""
    settings = get_settings()
    logger.info("Initializing Face Attendance System services...")

    # Initialize services
    services["face_detection"] = FaceDetectionService(
        min_detection_confidence=settings.face_detection_confidence
    )
    services["face_embedding"] = FaceEmbeddingService()
    services["liveness"] = LivenessService(
        threshold=settings.liveness_threshold
    )
    services["database"] = DatabaseService(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key
    )

    logger.info("All services initialized successfully!")

    yield

    # Cleanup
    logger.info("Shutting down Face Attendance System...")
    services.clear()


# Create FastAPI application
app = FastAPI(
    title="Face Attendance System",
    description="""
    ## Mobile Face-Attendance Demo API

    High-speed, high-accuracy proof-of-concept for marking attendance using Computer Vision.

    ### Features:
    - **User Registration**: Capture Master Selfie and generate 512-D Face Vector
    - **Attendance Marking**: Real-time face detection with liveness check
    - **Anti-Spoofing**: Passive liveness detection to prevent photo-based attacks
    - **Vector Search**: Cosine similarity matching against 5,000+ identities

    ### Performance:
    - Match Accuracy: >99.5%
    - Processing Time: <1.5 seconds
    - Search Time: <10ms for 5,000 identities
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for mobile/web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(registration.router, prefix="/api/v1", tags=["Registration"])
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "healthy",
        "service": "Face Attendance System",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "face_detection": "face_detection" in services,
            "face_embedding": "face_embedding" in services,
            "liveness": "liveness" in services,
            "database": "database" in services
        }
    }


def get_service(name: str):
    """Get a service instance by name."""
    return services.get(name)
