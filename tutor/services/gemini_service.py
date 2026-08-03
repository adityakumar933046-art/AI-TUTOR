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
        Communicates with the Gemini API using google.generativeai and dynamic model parameters.
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY is not set in environment. Please configure your API key in .env.",
                "response": "I'm ready to help, but my Gemini API Key needs to be configured in the system `.env` file!"
            }

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            
            kwargs = ModelRouter.get_dynamic_model_kwargs()
            model_name = kwargs.get('model_name', 'gemini-1.5-flash')

            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=self.system_instruction
                )
            except Exception as e:
                model = genai.GenerativeModel(
                    model_name='gemini-pro',
                    system_instruction=self.system_instruction
                )

            formatted_history = []
            if chat_history:
                recent_history = list(chat_history)[-16:]
                for msg in recent_history:
                    role = 'user' if msg.role == 'user' else 'model'
                    formatted_history.append({
                        "role": role,
                        "parts": [msg.content]
                    })

            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(user_message)
            
            if response and response.text:
                return {
                    "success": True,
                    "response": response.text.strip(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": "Gemini API returned an empty response.",
                    "response": "I couldn't generate an answer right now. Could you rephrase your question?"
                }

        except Exception as e:
            logger.error(f"[GEMINI API ERROR]: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "response": f"Oops! I ran into an issue connecting to Gemini: {str(e)}"
            }
