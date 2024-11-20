from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from .core.config import settings
from .api.routes import borrowing, returns, reservations
from .services.notification_service import NotificationService
from .services.background_tasks import LibraryTasks
import asyncio
import aiojobs

app = FastAPI(
    title="Book Borrowing Service",
    description="Microservice for managing book borrowings and returns",
    version="1.0.0"
)

# Initialize
mongodb_client = None
redis_client = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    global mongodb_client
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = mongodb_client[settings.DATABASE_NAME]
    app.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
    if app.redis:
        await app.redis.close()

@app.on_event("startup")
async def setup_background_tasks():
    scheduler = await aiojobs.create_scheduler()
    app.scheduler = scheduler
    
    async def run_periodic_tasks():
        while True:
            try:
                tasks = LibraryTasks(app.mongodb, NotificationService(app.redis))
                await tasks.check_due_dates()
                await tasks.check_overdue_books()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                print(f"Error in periodic tasks: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    await scheduler.spawn(run_periodic_tasks())

@app.on_event("shutdown")
async def cleanup_background_tasks():
    await app.scheduler.close()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

app.include_router(borrowing.router, prefix="/api/borrowings", tags=["borrowings"])
app.include_router(returns.router, prefix="/api/returns", tags=["returns"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["reservations"])

@app.get("/health")
async def health_check():
    try:
        await app.mongodb.command('ping')
        await app.redis.ping()
        return {"status": "healthy", "database": "connected", "redis": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )