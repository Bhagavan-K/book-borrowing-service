from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from .notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

class LibraryTasks:
    def __init__(self, db: AsyncIOMotorDatabase, notification_service: NotificationService):
        self.db = db
        self.notification_service = notification_service

    async def check_due_dates(self):
        try:
            tomorrow = datetime.utcnow() + timedelta(days=1)
            cursor = self.db.borrowings.find({
                "status": "ACTIVE",
                "due_date": {"$lt": tomorrow}
            })
            
            async for borrowing in cursor:
                await self.notification_service.send_due_date_reminder(
                    borrowing["user_id"],
                    borrowing["book_id"],
                    borrowing["due_date"]
                )
        except Exception as e:
            logger.error(f"Error in check_due_dates: {e}")

    async def check_overdue_books(self):
        try:
            today = datetime.utcnow()
            cursor = self.db.borrowings.find({
                "status": "ACTIVE",
                "due_date": {"$lt": today}
            })
            
            async for borrowing in cursor:
                days_overdue = (today - borrowing["due_date"]).days
                if days_overdue > 0:
                    await self.notification_service.send_overdue_notification(
                        borrowing["user_id"],
                        borrowing["book_id"],
                        days_overdue
                    )
        except Exception as e:
            logger.error(f"Error in check_overdue_books: {e}")