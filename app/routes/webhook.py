# from fastapi import APIRouter, Form, HTTPException, BackgroundTasks
# from app.services.whatsapp_service import whatsapp_service
# from app.services.ai_service import ai_service
# from app.services.database_service import db_service
# import logging

# router = APIRouter()


# @router.post("/webhook/whatsapp")
# async def handle_whatsapp_message(
#     background_tasks: BackgroundTasks,
#     Body: str = Form(...),
#     From: str = Form(...),
#     To: str = Form(...),
#     MessageSid: str = Form(None),
# ):
#     """Handle incoming WhatsApp messages"""
#     try:
#         logging.info(f"📩 Received message from {From}: {Body}")

#         # Extract phone number
#         user_phone = From.replace("whatsapp:", "")

#         # Get conversation history for context
#         conversation_history = await db_service.get_conversation_history(user_phone)

#         # Generate AI response using Gemini
#         ai_result = await ai_service.generate_response(Body, conversation_history)
#         ai_response = ai_result["response"]
#         response_time_ms = ai_result["response_time_ms"]
#         provider = ai_result["provider"]

#         logging.info(f"🤖 Generated response using {provider} in {response_time_ms}ms")

#         # Send response to user
#         success = await whatsapp_service.send_message(From, ai_response)

#         if success:
#             # Save to database in background
#             background_tasks.add_task(
#                 save_conversation_background,
#                 user_phone,
#                 Body,
#                 ai_response,
#                 response_time_ms,
#             )

#             logging.info(f"✅ Response sent to {user_phone}")
#         else:
#             logging.error(f"❌ Failed to send response to {user_phone}")

#         return {
#             "status": "success",
#             "message": "Message processed",
#             "provider": provider,
#         }

#     except Exception as e:
#         logging.error(f"❌ Webhook error: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")


# async def save_conversation_background(
#     user_phone: str, user_message: str, ai_response: str, response_time_ms: int
# ):
#     """Save conversation in background"""
#     try:
#         await db_service.save_conversation(
#             user_phone, user_message, ai_response, response_time_ms
#         )
#     except Exception as e:
#         logging.error(f"❌ Background save error: {e}")


# @router.get("/webhook/whatsapp")
# async def verify_webhook():
#     """Webhook verification endpoint"""
#     return {"status": "webhook_verified", "message": "WhatsApp webhook is active"}


# @router.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "service": "WhatsApp AI Responder",
#         "version": "1.0.0",
#         "ai_provider": "Google Gemini",
#     }


# @router.get("/test-gemini")
# async def test_gemini_api():
#     """Test Gemini API connection"""
#     try:
#         is_working = await ai_service.test_gemini_connection()
#         return {
#             "gemini_status": "working" if is_working else "failed",
#             "message": (
#                 "Gemini API is working!"
#                 if is_working
#                 else "Gemini API connection failed"
#             ),
#         }
#     except Exception as e:
#         logging.error(f"❌ Gemini test error: {e}")
#         return {"gemini_status": "error", "message": str(e)}


# @router.get("/stats")
# async def get_stats():
#     """Get basic statistics"""
#     try:
#         # You can add analytics here
#         return {
#             "status": "active",
#             "database": "connected" if db_service.db else "disconnected",
#             "ai_provider": "Google Gemini",
#         }
#     except Exception as e:
#         logging.error(f"❌ Stats error: {e}")
#         return {"status": "error", "message": str(e)}


# # File: app/routes/webhook.py
from fastapi import APIRouter, Form, HTTPException, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.services.database_service import db_service
import logging

router = APIRouter()


def extract_name_from_phone(phone_number: str) -> str:
    """
    Extract name from phone number or return generic name
    You can enhance this to use a user database
    """
    # For now, return a generic greeting approach
    # In production, you'd query user database for actual names
    return "there"  # Generic friendly greeting


@router.post("/webhook/whatsapp")
async def handle_whatsapp_message(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    MessageSid: str = Form(None),
):
    """Handle incoming WhatsApp messages with smart personalization"""
    try:
        logging.info(f"📩 Received message from {From}: {Body}")

        # Extract phone number
        user_phone = From.replace("whatsapp:", "")

        # Get conversation history for context
        conversation_history = await db_service.get_conversation_history(user_phone)
        conversation_history = None
        # conversation_history = None  # Disable history temporarily

        # Extract user name (you can enhance this with actual user database)
        user_name = extract_name_from_phone(user_phone)

        # Generate AI response with smart personalization
        ai_result = await ai_service.generate_response(
            Body, conversation_history, user_name
        )
        ai_response = ai_result["response"]
        response_time_ms = ai_result["response_time_ms"]
        provider = ai_result["provider"]

        logging.info(f"🤖 Generated response using {provider} in {response_time_ms}ms")

        # Send response to user
        success = await whatsapp_service.send_message(From, ai_response)

        if success:
            # Save to database in background
            background_tasks.add_task(
                save_conversation_background,
                user_phone,
                Body,
                ai_response,
                response_time_ms,
            )

            logging.info(f"✅ Response sent to {user_phone}")
        else:
            logging.error(f"❌ Failed to send response to {user_phone}")

        return {
            "status": "success",
            "message": "Message processed",
            "provider": provider,
        }

    except Exception as e:
        logging.error(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def save_conversation_background(
    user_phone: str, user_message: str, ai_response: str, response_time_ms: int
):
    """Save conversation in background"""
    try:
        await db_service.save_conversation(
            user_phone, user_message, ai_response, response_time_ms
        )
    except Exception as e:
        logging.error(f"❌ Background save error: {e}")


@router.get("/webhook/whatsapp")
async def verify_webhook():
    """Webhook verification endpoint"""
    return {"status": "webhook_verified", "message": "WhatsApp webhook is active"}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "WhatsApp AI Responder",
        "version": "1.0.0",
        "ai_provider": "Google Gemini",
    }


@router.get("/test-gemini")
async def test_gemini_api():
    """Test Gemini API connection"""
    try:
        is_working = await ai_service.test_gemini_connection()
        return {
            "gemini_status": "working" if is_working else "failed",
            "message": (
                "Gemini API is working!"
                if is_working
                else "Gemini API connection failed"
            ),
        }
    except Exception as e:
        logging.error(f"❌ Gemini test error: {e}")
        return {"gemini_status": "error", "message": str(e)}


@router.get("/stats")
async def get_stats():
    """Get basic statistics"""
    try:
        return {
            "status": "active",
            "database": "connected" if db_service.db else "disconnected",
            "ai_provider": "Google Gemini",
        }
    except Exception as e:
        logging.error(f"❌ Stats error: {e}")
        return {"status": "error", "message": str(e)}


@router.delete("/clear-all-conversations")
async def clear_all_conversations():
    """Clear all conversations for fresh start"""
    try:
        result = await db_service.db.conversations.delete_many({})
        return {
            "deleted_count": result.deleted_count,
            "message": "All conversations cleared",
        }
    except Exception as e:
        return {"error": str(e)}
