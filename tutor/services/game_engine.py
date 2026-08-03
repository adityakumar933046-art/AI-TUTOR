import json
import logging
from tutor.models import Game, GameQuestion, ChatSession
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

class GameEngineService:
    @staticmethod
    def generate_ai_game(student, subject='Math', topic='Fractions', game_type='match_pair', difficulty='Easy'):
        chat_session = ChatSession.objects.filter(student=student, subject=subject).first()
        if not chat_session:
            chat_session = ChatSession.objects.create(
                student=student,
                subject=subject,
                title=f"Game Session - {topic}"
            )

        gemini_service = GeminiTutorService(subject=subject)

        prompt = (
            f"Generate a fun educational game config for topic '{topic}' in subject '{subject}'.\n"
            f"Game type: '{game_type}', Difficulty: '{difficulty}'.\n"
            f"Return strict raw JSON format ONLY with key 'items', an array of objects.\n"
            f"For match_pair or memory_cards, each object has 'left' and 'right'.\n"
            f"For interactive_quiz, each object has 'question', 'options' (array of 4), 'correct_index', 'explanation'.\n"
            f"Example format for match_pair: {{\n  \"items\": [\n    {{\"left\": \"1/2\", \"right\": \"50%\"}},\n    {{\"left\": \"1/4\", \"right\": \"25%\"}},\n    {{\"left\": \"3/4\", \"right\": \"75%\"}}\n  ]\n}}"
        )

        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        items = []
        try:
            clean_json = raw_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            items = parsed.get('items', [])
        except Exception:
            # Fallback default items
            if game_type in ['match_pair', 'memory_cards']:
                items = [
                    {"left": "Photosynthesis", "right": "Plants make food using sunlight"},
                    {"left": "Chlorophyll", "right": "Green pigment in leaves"},
                    {"left": "Oxygen", "right": "Gas released by plants"}
                ]
            else:
                items = [
                    {
                        "question": "What do plants release during photosynthesis?",
                        "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"],
                        "correct_index": 0,
                        "explanation": "Plants release oxygen into the air!"
                    }
                ]

        game = Game.objects.create(
            student=student,
            chat_session=chat_session,
            title=f"{topic} ({game_type.replace('_', ' ').title()})",
            subject=subject,
            game_type=game_type,
            difficulty=difficulty,
            config_json=json.dumps(items)
        )

        return game
