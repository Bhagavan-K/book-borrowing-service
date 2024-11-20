from redis.asyncio import Redis
from datetime import datetime
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, redis: Redis):
        self.redis = redis
        
    async def send_reservation_notification(self, user_id: int, book_id: int, position: int):
        notification = {
            "type": "RESERVATION_CREATED",
            "user_id": user_id,
            "book_id": book_id,
            "position": position,
            "message": f"You are #{position} in line for book (ID: {book_id})"
        }
        await self.queue_notification(notification)
    
    async def send_due_date_reminder(self, user_id: int, book_id: int, due_date: datetime):
        notification = {
            "type": "DUE_DATE_REMINDER",
            "user_id": user_id,
            "book_id": book_id,
            "due_date": due_date.isoformat(),
            "message": f"Your book (ID: {book_id}) is due on {due_date.strftime('%Y-%m-%d')}"
        }
        await self.queue_notification(notification)
    
    async def send_book_available_notification(self, user_id: int, book_id: int):
        notification = {
            "type": "BOOK_AVAILABLE",
            "user_id": user_id,
            "book_id": book_id,
            "message": f"Book (ID: {book_id}) is now available for borrowing"
        }
        await self.queue_notification(notification)
    
    async def queue_notification(self, notification: Dict):
        await self.redis.lpush("notifications", json.dumps(notification))
        logger.info(f"Queued notification: {notification['type']} for user {notification['user_id']}")