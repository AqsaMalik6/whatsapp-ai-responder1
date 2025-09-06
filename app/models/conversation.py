# File: app/models/conversation.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic v2"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId format")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, field_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pydantic v2 method for JSON schema"""
        field_schema.update(type="string")
        return field_schema


class ConversationModel(BaseModel):
    """Model for storing WhatsApp conversations"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_phone: str = Field(..., description="User's phone number")
    user_message: str = Field(..., description="Message from user")
    ai_response: str = Field(..., description="AI generated response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = Field(
        default=None, description="Response generation time"
    )
    message_type: str = Field(default="text", description="Type of message")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "user_phone": "+1234567890",
                "user_message": "Hello, I need help",
                "ai_response": "Hi! How can I help you?",
                "message_type": "text",
            }
        },
    }
