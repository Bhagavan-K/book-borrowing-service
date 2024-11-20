from fastapi import Depends
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...services.notification_service import NotificationService
from ...services.background_tasks import LibraryTasks
from .database import get_database
from .redis import get_redis

async def get_notification_service(redis: Redis = Depends(get_redis)) -> NotificationService:
    return NotificationService(redis)

async def get_library_tasks(
    db: AsyncIOMotorDatabase = Depends(get_database),
    notification_service: NotificationService = Depends(get_notification_service)
) -> LibraryTasks:
    return LibraryTasks(db, notification_service)