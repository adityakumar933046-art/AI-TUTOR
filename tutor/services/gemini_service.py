import os
import logging
from django.conf import settings
from tutor.services.model_router import ModelRouter

logger = logging.getLogger(__name__)

# Cached set of API-verified models to prevent repeated list_models network calls
_VERIFIED_MODELS_CACHE = None

def discover_valid_gemini_models(api_key):
    """
    Calls google.generativeai.list_models() to retrieve supported models for generateContent.
    Filters out deprecated models and caches the result.
    """
    global _VERIFIED_MODELS_CACHE
    if _VERIFIED_MODELS_CACHE is not None:
        return _VERIFIED_MODELS_CACHE

    valid_models = []
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            all_models = genai.list_models()
            excluded_keywords = ['tts', 'image', 'lyria', 'robotics', 'computer-use', 'banana', 'embedding']
            for m in all_models:
                methods = getattr(m, 'supported_generation_methods', [])
                if 'generateContent' in methods:
                    name = m.name.replace('models/', '')
                    if not any(k in name.lower() for k in excluded_keywords):
                        valid_models.append(name)
            logger.info(f"[GEMINI MODEL DISCOVERY]: Discovered {len(valid_models)} supported text generation models from API.")
        except Exception as e:
            logger.warning(f"[GEMINI MODEL DISCOVERY FAILED]: Could not list models dynamically: {e}")

    # Safe fallback defaults if list_models fails or API key missing
    if not valid_models:
        valid_models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']

    _VERIFIED_MODELS_CACHE = valid_models
    return _VERIFIED_MODELS_CACHE


def get_gemini_candidate_models(api_key, primary_model=None):
    """
    Builds a list of candidate model names by cross-referencing requested/configured models
    against API-discovered valid models.
    Guarantees no deprecated model names are returned.
    """
    available_api_models = discover_valid_gemini_models(api_key)

    candidates = []
    # 1. Primary requested model (if configured and valid)
    if primary_model and primary_model in available_api_models:
        candidates.append(primary_model)

    # 2. Preferred stable model defaults
    preferred_order = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']
    for pref in preferred_order:
        if pref in available_api_models and pref not in candidates:
            candidates.append(pref)

    # 3. Any other model returned by API
    for m in available_api_models:
        if m not in candidates:
            candidates.append(m)

    return candidates


def classify_gemini_error(error_str):
    """
    Classifies Gemini API exceptions into user-friendly diagnostic messages.
    """
    err = str(error_str).lower()
    if '429' in err or 'quota' in err or 'rate' in err:
        return "Quota exceeded: The AI service has reached its request rate limit. Please try again in a few moments."
    elif '404' in err or 'not found' in err or 'invalid model' in err:
        return "Invalid model: The requested AI model is unavailable. Automatically switching to a supported model."
    elif '401' in err or '403' in err or 'api key' in err or 'permission' in err:
        return "Authentication error: The configured GEMINI_API_KEY is invalid or lacks access permissions."
    elif 'timeout' in err or 'connection' in err or 'network' in err:
        return "Network error / Timeout: Connection to Gemini timed out. Please check your internet connection."
    else:
        return f"AI Service Error: {error_str}"


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
                "error": "Authentication error: GEMINI_API_KEY is not configured in .env.",
                "response": "I'm ready to help, but my Gemini API Key needs to be configured in the system `.env` file!"
            }

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        kwargs = ModelRouter.get_dynamic_model_kwargs()
        primary_model = kwargs.get('model_name', os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'))
        candidate_models = get_gemini_candidate_models(self.api_key, primary_model)

        formatted_history = []
        if chat_history:
            recent_history = list(chat_history)[-16:]
            for msg in recent_history:
                role = 'user' if msg.role == 'user' else 'model'
                formatted_history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        last_raw_error = None
        for attempt_idx, m_name in enumerate(candidate_models, start=1):
            try:
                logger.info(f"[GEMINI ATTEMPT {attempt_idx}/{len(candidate_models)}]: Trying model '{m_name}'...")
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=self.system_instruction
                )
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_message)
                
                if response and response.text:
                    logger.info(f"[GEMINI SUCCESS]: Model '{m_name}' responded successfully on attempt {attempt_idx}.")
                    return {
                        "success": True,
                        "response": response.text.strip(),
                        "model_used": m_name,
                        "error": None
                    }
            except Exception as e:
                last_raw_error = str(e)
                classified_err = classify_gemini_error(e)
                logger.warning(f"[GEMINI RETRY {attempt_idx}]: Model '{m_name}' failed ({classified_err}). Trying fallback model...")
                continue

        user_friendly_error = classify_gemini_error(last_raw_error)
        logger.error(f"[GEMINI API FAILURE]: All candidate models failed. Last error: {last_raw_error}")
        return {
            "success": False,
            "error": user_friendly_error,
            "response": f"I couldn't reach the AI service right now. ({user_friendly_error})"
        }

    def generate_tutor_response_stream(self, user_message, chat_history=None):
        """
        Yields chunked text responses from Gemini for real-time streaming to the client.
        """
        if not self.api_key:
            yield "Authentication error: GEMINI_API_KEY is not configured in .env!"
            return

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        kwargs = ModelRouter.get_dynamic_model_kwargs()
        primary_model = kwargs.get('model_name', os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'))
        candidate_models = get_gemini_candidate_models(self.api_key, primary_model)

        formatted_history = []
        if chat_history:
            recent_history = list(chat_history)[-16:]
            for msg in recent_history:
                role = 'user' if msg.role == 'user' else 'model'
                formatted_history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        last_raw_error = None
        for attempt_idx, m_name in enumerate(candidate_models, start=1):
            try:
                logger.info(f"[GEMINI STREAM ATTEMPT {attempt_idx}/{len(candidate_models)}]: Trying model '{m_name}'...")
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=self.system_instruction
                )
                chat = model.start_chat(history=formatted_history)
                response_stream = chat.send_message(user_message, stream=True)
                for chunk in response_stream:
                    if chunk and chunk.text:
                        yield chunk.text
                logger.info(f"[GEMINI STREAM SUCCESS]: Model '{m_name}' streamed successfully on attempt {attempt_idx}.")
                return
            except Exception as e:
                last_raw_error = str(e)
                classified_err = classify_gemini_error(e)
                logger.warning(f"[GEMINI STREAM RETRY {attempt_idx}]: Model '{m_name}' failed ({classified_err}). Trying fallback model...")
                continue

        user_friendly_error = classify_gemini_error(last_raw_error)
        yield f"AI Service Stream Warning: {user_friendly_error}"
