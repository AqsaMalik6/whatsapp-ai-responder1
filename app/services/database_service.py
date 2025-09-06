from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.models.conversation import ConversationModel
from typing import List, Dict, Optional
import logging
from datetime import datetime


class DatabaseService:
    """Service for MongoDB operations"""

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect_to_database(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]

            # Test connection
            await self.client.admin.command("ping")
            logging.info("✅ Connected to MongoDB successfully!")

        except Exception as e:
            logging.error(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def save_conversation(
        self,
        user_phone: str,
        user_message: str,
        ai_response: str,
        response_time_ms: int = None,
    ) -> Optional[str]:
        """Save conversation to database"""
        try:
            conversation = ConversationModel(
                user_phone=user_phone,
                user_message=user_message,
                ai_response=ai_response,
                response_time_ms=response_time_ms,
            )

            result = await self.db.conversations.insert_one(
                conversation.dict(by_alias=True, exclude_unset=True)
            )

            logging.info(f"💾 Conversation saved with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logging.error(f"❌ Database save error: {e}")
            return None

    async def get_conversation_history(
        self, user_phone: str, limit: int = 5
    ) -> List[Dict]:
        """Get recent conversations for context"""
        try:
            cursor = (
                self.db.conversations.find({"user_phone": user_phone})
                .sort("timestamp", -1)
                .limit(limit)
            )

            conversations = await cursor.to_list(length=limit)

            # Convert ObjectId to string
            for conv in conversations:
                conv["_id"] = str(conv["_id"])

            return conversations

        except Exception as e:
            logging.error(f"❌ Database fetch error: {e}")
            return []

    async def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logging.info("🔌 Database connection closed")


# Global database service instance
db_service = DatabaseService()
