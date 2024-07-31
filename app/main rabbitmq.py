import logging
from fastapi import FastAPI
from app.routes import events
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Startup and shutdown events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Include routers
app.include_router(events.router, prefix="/api")

# Test route
@app.get("/test")
async def test_route():
    return {"message": "Test route is working"}

# Print available routes on startup
@app.on_event("startup")
async def print_routes():
    logger.info("Available routes:")
    for route in app.routes:
        logger.info(f"{route.methods} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)