import json
import re
import logging
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

PRACTICE_SYSTEM_INSTRUCTION = (
    "You are Sparky AI Practice Generator for EduVerse AI Kids. "
    "Generate 3 new, distinct practice questions similar to the student's homework question. "
    "Return a JSON array of objects, each containing: "
    "1. 'difficulty': string from ['Easy', 'Medium', 'Hard', 'Challenge'] "
    "2. 'question_text': string "
    "3. 'options': array of 4 multiple-choice choices "
    "4. 'correct_index': integer 0-3 "
    "5. 'explanation': step-by-step solution breakdown"
)

class PracticeGeneratorService:
    def __init__(self, question_text, subject="Math"):
        self.question_text = question_text
        self.subject = subject

    def generate_practice_set(self):
        gemini_service = GeminiTutorService(subject=self.subject)

        prompt = (
            f"Generate similar practice questions for: '{self.question_text}'. Subject: '{self.subject}'.\n"
            f"{PRACTICE_SYSTEM_INSTRUCTION}\nReturn ONLY valid JSON array."
        )

        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        parsed = self._clean_and_parse_json(raw_text)
        if not parsed:
            parsed = self._generate_fallback_practice()

        return parsed

    def _clean_and_parse_json(self, raw_text):
        try:
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', raw_text, re.DOTALL)
            json_str = match.group(1) if match else raw_text.strip()
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse Practice Questions JSON: {e}")
            return None

    def _generate_fallback_practice(self):
        return [
            {
                "difficulty": "Easy",
                "question_text": f"Similar Practice 1: Solve 2x + 4 = 10",
                "options": ["x = 3", "x = 5", "x = 2", "x = 4"],
                "correct_index": 0,
                "explanation": "Subtract 4 from 10 to get 6, then divide by 2 to get x = 3."
            },
            {
                "difficulty": "Medium",
                "question_text": f"Similar Practice 2: Solve 4x - 6 = 18",
                "options": ["x = 6", "x = 4", "x = 5", "x = 8"],
                "correct_index": 0,
                "explanation": "Add 6 to 18 to get 24, then divide by 4 to get x = 6."
            },
            {
                "difficulty": "Hard",
                "question_text": f"Similar Practice 3: Solve 5(x - 2) = 25",
                "options": ["x = 7", "x = 5", "x = 8", "x = 9"],
                "correct_index": 0,
                "explanation": "Divide 25 by 5 to get x - 2 = 5, then add 2 to get x = 7."
            }
        ]
