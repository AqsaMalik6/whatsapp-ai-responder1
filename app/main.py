from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import webhook
from app.services.database_service import db_service
from app.config.settings import settings
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logging.info("🚀 Starting WhatsApp AI Responder...")

    try:
        # Connect to database
        await db_service.connect_to_database()
        logging.info("✅ Application startup complete!")

        yield

    except Exception as e:
        logging.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logging.info("🛑 Shutting down...")
        await db_service.close_connection()
        logging.info("✅ Shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title="WhatsApp AI Responder",
    description="AI-powered WhatsApp auto-responder using FastAPI and MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routes
app.include_router(webhook.router, prefix="/api/v1", tags=["WhatsApp"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WhatsApp AI Responder is running! 🚀",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/api/v1/webhook/whatsapp",
            "health": "/api/v1/health",
            "stats": "/api/v1/stats",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
