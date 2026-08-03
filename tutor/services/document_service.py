import json
import re
import logging
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

DOC_PARSER_INSTRUCTION = (
    "You are a Document Intelligence Parser for EduVerse AI Kids. "
    "Analyze the extracted homework text and output a valid JSON object with: "
    "1. 'subject': string choice from ['Math', 'Science', 'English', 'History', 'Geography', 'Coding', 'Reasoning', 'General Knowledge'] "
    "2. 'overall_difficulty': choice from ['Easy', 'Medium', 'Hard', 'Challenge'] "
    "3. 'summary_overview': 2-sentence overview of what this homework assignment covers "
    "4. 'questions': array of objects containing: "
    "   - 'number': integer (1, 2, 3...) "
    "   - 'question_text': full text of question "
    "   - 'subject_tag': subject string "
    "   - 'difficulty': difficulty string "
    "   - 'solution_explanation': complete step-by-step reasoning with LaTeX math "
    "   - 'hint_text': 1-sentence Socratic hint guiding student without spoiling answer"
)

class DocumentParserService:
    def __init__(self, cleaned_ocr_text):
        self.ocr_text = cleaned_ocr_text

    def parse_document_questions(self):
        gemini_service = GeminiTutorService(subject='General Knowledge')
        
        prompt = (
            f"Parse the following cleaned OCR homework text into questions and solutions:\n\n"
            f"TEXT:\n{self.ocr_text}\n\n"
            f"{DOC_PARSER_INSTRUCTION}\nReturn ONLY valid JSON."
        )

        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        parsed_json = self._clean_and_parse_json(raw_text)
        if not parsed_json:
            parsed_json = self._generate_fallback_questions()

        return parsed_json

    def _clean_and_parse_json(self, raw_text):
        try:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
            json_str = match.group(1) if match else raw_text.strip()
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse Document JSON: {e}")
            return None

    def _generate_fallback_questions(self):
        return {
            "subject": "Math",
            "overall_difficulty": "Medium",
            "summary_overview": "Homework worksheet covering algebraic expressions and basic calculation problems.",
            "questions": [
                {
                    "number": 1,
                    "question_text": self.ocr_text[:100] or "Solve for x: 3x + 5 = 20",
                    "subject_tag": "Math",
                    "difficulty": "Medium",
                    "solution_explanation": "1. Subtract 5 from both sides: 3x = 15\n2. Divide by 3: x = 5.",
                    "hint_text": "First isolate the 3x term by subtracting 5 from both sides."
                }
            ]
        }
