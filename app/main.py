import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import logging
from app.routes import events
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
import redis
import time

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware for timing requests
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(TimingMiddleware)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await asyncio.gather(
        connect_to_mongo(),
        print_routes(),
        setup_cache()
    )

async def print_routes():
    routes = [f"{route.methods} {route.path}" for route in app.routes]
    logger.info("Available routes:\n" + "\n".join(routes))

async def setup_cache():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache:")

app.add_event_handler("shutdown", close_mongo_connection)

# Include routers
app.include_router(events.router, prefix="/api")

# Test route
@app.get("/test")
async def test_route():
    return {"message": "Test route is working"}

# Cached route example
@app.get("/cached")
@cache(expire=60)
async def cached_route():
    return {"message": "This response is cached for 60 seconds"}

# Background task example
@app.post("/background")
async def background_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(some_long_running_task)
    return {"message": "Background task started"}

async def some_long_running_task():
    await asyncio.sleep(10)  # Simulating a long-running task
    logger.info("Long-running task completed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, workers=10)