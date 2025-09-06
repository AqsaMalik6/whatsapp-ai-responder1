# File: app/services/ai_service.py
import google.generativeai as genai
from app.config.settings import settings
from typing import Dict, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta


class AIService:
    """Intelligent AI Assistant - ChatGPT Style Behavior"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def _is_first_interaction(
        self, conversation_history: Optional[List[Dict]] = None
    ) -> bool:
        """Check if this is the first interaction (no history or very old)"""
        if not conversation_history:
            return True

        # Check if last interaction was more than 6 hours ago
        try:
            if conversation_history:
                last_conv = conversation_history[0]  # Most recent
                if "timestamp" in last_conv:
                    last_time = last_conv["timestamp"]
                    if isinstance(last_time, str):
                        last_time = datetime.fromisoformat(
                            last_time.replace("Z", "+00:00")
                        )

                    time_diff = datetime.utcnow() - last_time
                    return time_diff > timedelta(hours=6)
        except:
            pass

        return False

    def _is_greeting_message(self, message: str) -> bool:
        """Detect if message is a greeting"""
        greetings = [
            "salam",
            "assalam",
            "aoa",
            "assalamu alaikum",
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "namaste",
            "adab",
        ]
        msg_lower = message.lower().strip()
        return any(greeting in msg_lower for greeting in greetings)

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_name: str = None,
    ) -> Dict:
        """Generate intelligent AI response like ChatGPT"""
        start_time = datetime.utcnow()

        try:
            # Check if we should use name (first interaction + greeting)
            is_first = self._is_first_interaction(conversation_history)
            is_greeting = self._is_greeting_message(user_message)
            use_personalized_greeting = is_first and is_greeting and user_name

            # Generate AI response
            response = await self._generate_gemini_response(
                user_message, conversation_history, use_personalized_greeting, user_name
            )

            if response:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return {
                    "response": response,
                    "provider": "gemini",
                    "response_time_ms": int(response_time),
                }

            # Fallback to smart responses
            response = self._intelligent_fallback(
                user_message, use_personalized_greeting, user_name
            )
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "response": response,
                "provider": "intelligent_fallback",
                "response_time_ms": int(response_time),
            }

        except Exception as e:
            logging.error(f"AI Service error: {e}")
            return {
                "response": "I'm here to help! Could you please ask your question again?",
                "provider": "error",
                "response_time_ms": 0,
            }

    async def _generate_gemini_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        use_personalized_greeting: bool = False,
        user_name: str = None,
    ) -> Optional[str]:
        """Generate intelligent Gemini response"""
        try:
            # Build dynamic system prompt based on context
            if use_personalized_greeting:
                system_prompt = f"""You are a helpful, intelligent AI assistant. This is your first interaction with the user.

CRITICAL RULES:
- The user's name appears to be {user_name}, so you can greet them personally this ONE time
- If they say Islamic greeting (Salam, AOA, Assalam), respond with "Walaikum Assalam {user_name}!"
- If they say other greetings, respond naturally with their name once
- Be warm, friendly, and professional
- Ask how you can help them today
- Keep response under 100 words
- NEVER mention WhatsApp, messaging apps, or customer support
# In system_prompt sections, make sure this line exists:
- NEVER mention WhatsApp, messaging apps, or customer support unless specifically asked
- After this greeting, NEVER use their name again unless they specifically ask"""

            elif conversation_history and len(conversation_history) > 0:
                system_prompt = """You are an intelligent AI assistant continuing a conversation.

CRITICAL RULES:
- Be helpful, smart, and conversational like ChatGPT
- NEVER use the user's name (you already greeted them before)
- Answer any question on any topic - technology, education, life, science, etc.
- Be concise but informative (under 150 words)
- Handle multiple languages: English, Urdu, Roman Urdu, Hindi
- If you don't know something, say so honestly
- Be natural and engaging
- NEVER mention WhatsApp, messaging apps, or customer support unless specifically asked
- NEVER mention WhatsApp, messaging, or customer support unless specifically asked"""

            else:
                system_prompt = """You are an intelligent AI assistant like ChatGPT.

CRITICAL RULES:
- Be helpful, smart, and conversational
- Answer any question on any topic
- Handle multiple languages: English, Urdu, Roman Urdu, Hindi  
- Be concise but informative (under 150 words)
- Be natural, friendly, and engaging
- If you don't know something, admit it honestly
- NEVER mention WhatsApp, messaging apps, or customer support unless specifically asked
- NEVER mention WhatsApp, messaging apps, or customer support unless specifically asked"""

            # Build conversation context
            full_prompt = system_prompt + "\n\n"

            # Add recent conversation for context (last 3 exchanges)
            if conversation_history:
                full_prompt += "Recent conversation context:\n"
                for conv in conversation_history[-3:]:
                    full_prompt += f"User: {conv.get('user_message', '')}\n"
                    full_prompt += f"You: {conv.get('ai_response', '')}\n"
                full_prompt += "\n"

            # Add current message
            full_prompt += f"Current user message: {user_message}\n"
            full_prompt += "Your response:"

            # Generate response with timeout
            response = await asyncio.wait_for(
                self._call_gemini_api(full_prompt), timeout=8
            )

            # Clean response
            if response:
                response = response.strip()
                # Remove any unwanted prefixes
                for prefix in ["You:", "Assistant:", "Response:", "Your response:"]:
                    if response.startswith(prefix):
                        response = response[len(prefix) :].strip()

            return response if response else None

        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return None

    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API with optimized settings"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=150,
                        temperature=0.8,  # More natural responses
                        top_p=0.9,
                        top_k=40,
                    ),
                ),
            )
            return response.text if response and response.text else None
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return None

    def _intelligent_fallback(
        self,
        user_message: str,
        use_personalized_greeting: bool = False,
        user_name: str = None,
    ) -> str:
        """Intelligent fallback responses"""
        msg_lower = user_message.lower().strip()

        # Personalized greetings for first interaction
        if use_personalized_greeting and user_name:
            if any(greet in msg_lower for greet in ["salam", "aoa", "assalam"]):
                return f"Walaikum Assalam {user_name}! How can I help you today?"
            elif any(greet in msg_lower for greet in ["hello", "hi", "hey"]):
                return f"Hello {user_name}! How can I assist you today?"

        # Regular responses (no name)
        if any(greet in msg_lower for greet in ["salam", "aoa", "assalam"]):
            return "Walaikum Assalam! How can I help you?"
        elif any(greet in msg_lower for greet in ["hello", "hi", "hey"]):
            return "Hello! How can I assist you today?"
        elif (
            "thanks" in msg_lower or "thank you" in msg_lower or "shukriya" in msg_lower
        ):
            return "You're welcome! Is there anything else I can help you with?"
        elif "bye" in msg_lower or "goodbye" in msg_lower or "alvida" in msg_lower:
            return "Goodbye! Feel free to reach out anytime you need help."
        elif "how are you" in msg_lower or "kya haal" in msg_lower:
            return "I'm doing well, thank you! How can I help you today?"
        elif any(word in msg_lower for word in ["help", "madad", "sahayata"]):
            return "I'm here to help! What do you need assistance with?"
        else:
            return "I'm here to assist you! Could you please tell me what you'd like to know or discuss?"

    async def test_gemini_connection(self) -> bool:
        """Test Gemini connection"""
        try:
            test_response = await self._call_gemini_api(
                "Reply with: Connection successful"
            )
            return test_response is not None and "successful" in test_response.lower()
        except Exception as e:
            logging.error(f"Gemini test failed: {e}")
            return False


ai_service = AIService()
