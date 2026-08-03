import json
from tutor.models import AdaptivePlan
from tutor.services.gemini_service import GeminiTutorService

class AdaptiveCurriculumEngine:
    @staticmethod
    def generate_adaptive_plan(student):
        service = GeminiTutorService(subject='General Knowledge')

        prompt = (
            f"Generate a personalized adaptive curriculum sequence for student '{student.username}'.\n"
            f"Select next 3 topics with difficulty and activity types (visual, game, practice, speaking).\n"
            f"Return ONLY valid raw JSON array of 3 objects with keys: topic, subject, difficulty, recommended_activity.\n"
            f"Example: [{{\"topic\":\"Fractions\", \"subject\":\"Math\", \"difficulty\":\"Medium\", \"recommended_activity\":\"Match Pair Game\"}}]"
        )

        res = service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        curr_items = [
            {"topic": "Fractions & Decimals", "subject": "Math", "difficulty": "Medium", "recommended_activity": "Interactive Math Game"},
            {"topic": "Photosynthesis & Solar Energy", "subject": "Science", "difficulty": "Easy", "recommended_activity": "Visual Flowchart"},
            {"topic": "Roleplay: Ordering Food", "subject": "English", "difficulty": "Medium", "recommended_activity": "Speaking Coach"}
        ]

        try:
            clean_json = raw_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            if isinstance(parsed, list):
                curr_items = parsed
        except Exception:
            pass

        plan = AdaptivePlan.objects.create(
            student=student,
            curriculum_json=json.dumps(curr_items),
            difficulty_level='Adaptive'
        )

        return plan
