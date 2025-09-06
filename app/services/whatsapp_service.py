from twilio.rest import Client
from app.config.settings import settings
import logging


class WhatsAppService:
    """Service for WhatsApp messaging via Twilio"""

    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    async def send_message(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message to user"""
        try:
            # Clean phone number format
            if to_phone.startswith("whatsapp:"):
                to_phone = to_phone.replace("whatsapp:", "")

            # Ensure proper WhatsApp format
            if not to_phone.startswith("+"):
                to_phone = f"+{to_phone}"

            # Final WhatsApp format
            to_whatsapp = f"whatsapp:{to_phone}"

            logging.info(f"📱 Sending to: {to_whatsapp} from: {self.from_number}")

            # Send message
            message_obj = self.client.messages.create(
                body=message, from_=self.from_number, to=to_whatsapp
            )

            logging.info(f"📱 Message sent successfully! SID: {message_obj.sid}")
            return True

        except Exception as e:
            logging.error(f"❌ WhatsApp send error: {e}")
            return False

    def validate_phone_number(self, phone: str) -> str:
        """Validate and format phone number"""
        # Remove whatsapp: prefix if exists
        phone = phone.replace("whatsapp:", "")

        # Add + if not exists
        if not phone.startswith("+"):
            phone = f"+{phone}"

        return phone


# Global WhatsApp service instance
whatsapp_service = WhatsAppService()
