import os
import logging
from django.conf import settings
from tutor.services.model_router import ModelRouter

logger = logging.getLogger(__name__)

SUBJECT_PROMPTS = {
    'Math': "Focus on step-by-step problem solving, using numbers, visual analogies, and clear LaTeX math formatting ($...$ or $$...$$).",
    'Science': "Focus on real-world phenomena, fun experiments, biological wonders, space exploration, and scientific discovery.",
    'English': "Focus on vocabulary development, creative writing, grammar rules, reading comprehension, and storytelling.",
    'History': "Focus on historical events, inspiring leaders, ancient civilizations, and cultural heritage explained as exciting stories.",
    'Geography': "Focus on continents, climates, countries, maps, ocean life, and natural wonders of planet Earth.",
    'General Knowledge': "Focus on curious facts, everyday technology, nature secrets, and fun trivia.",
    'Coding': "Focus on Python/Block programming logic, clean readable code snippets, and explaining logic step-by-step.",
    'Reasoning': "Focus on logic puzzles, riddles, pattern recognition, and critical reasoning challenges.",
}

class GeminiTutorService:
    def __init__(self, subject='General Knowledge'):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
        self.subject = subject
        
        dynamic_prompt = ModelRouter.get_dynamic_prompt('AI Chat')
        self.system_instruction = f"{dynamic_prompt}\nSubject Focus: {SUBJECT_PROMPTS.get(subject, '')}"

    def generate_tutor_response(self, user_message, chat_history=None):
        """
        Communicates with the Gemini API using google.generativeai and dynamic model parameters with automatic fallback handling.
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY is not set in environment. Please configure your API key in .env.",
                "response": "I'm ready to help, but my Gemini API Key needs to be configured in the system `.env` file!"
            }

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        kwargs = ModelRouter.get_dynamic_model_kwargs()
        primary_model = kwargs.get('model_name', 'gemini-1.5-flash-latest')
        candidate_models = [primary_model, 'gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-exp']

        formatted_history = []
        if chat_history:
            recent_history = list(chat_history)[-16:]
            for msg in recent_history:
                role = 'user' if msg.role == 'user' else 'model'
                formatted_history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        last_error = None
        for m_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=self.system_instruction
                )
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_message)
                
                if response and response.text:
                    return {
                        "success": True,
                        "response": response.text.strip(),
                        "error": None
                    }
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[GEMINI RETRY]: Model '{m_name}' failed: {e}. Trying fallback...")
                continue

        logger.error(f"[GEMINI API ERROR]: All model candidates failed. Last error: {last_error}")
        return {
            "success": False,
            "error": last_error,
            "response": f"I couldn't reach Gemini right now, but I'm ready to continue as soon as network connects! (Error: {last_error})"
        }

    def generate_tutor_response_stream(self, user_message, chat_history=None):
        """
        Yields chunked text responses from Gemini for real-time streaming to the client.
        """
        if not self.api_key:
            yield "GEMINI_API_KEY is not configured in .env!"
            return

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        kwargs = ModelRouter.get_dynamic_model_kwargs()
        primary_model = kwargs.get('model_name', 'gemini-1.5-flash-latest')
        candidate_models = [primary_model, 'gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-exp']

        formatted_history = []
        if chat_history:
            recent_history = list(chat_history)[-16:]
            for msg in recent_history:
                role = 'user' if msg.role == 'user' else 'model'
                formatted_history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        for m_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=self.system_instruction
                )
                chat = model.start_chat(history=formatted_history)
                response_stream = chat.send_message(user_message, stream=True)
                for chunk in response_stream:
                    if chunk and chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                logger.warning(f"[GEMINI STREAM RETRY]: Model '{m_name}' failed: {e}. Trying fallback...")
                continue

        yield "I am having trouble connecting to Gemini stream right now, but I will retry shortly!"
