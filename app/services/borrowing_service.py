from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        
    async def close_database_connection(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    @property
    def db(self):
        return self.client[settings.DATABASE_NAME]

db_manager = DatabaseManager()