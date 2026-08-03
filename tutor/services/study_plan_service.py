import json
from tutor.models import DailyStudyPlan
from tutor.services.gemini_service import GeminiTutorService

class StudyPlanGeneratorService:
    @staticmethod
    def generate_daily_plan(student):
        service = GeminiTutorService(subject='General Knowledge')

        prompt = (
            f"Generate a balanced daily study plan for student '{student.username}'.\n"
            f"Allocate target study minutes across 6 areas: Math, Science, Reading, Speaking, Homework, Games.\n"
            f"Total target time must be exactly 80 minutes.\n"
            f"Return ONLY raw valid JSON object with keys: Math, Science, Reading, Speaking, Homework, Games.\n"
            f"Example: {{\"Math\": 20, \"Science\": 15, \"Reading\": 15, \"Speaking\": 10, \"Homework\": 10, \"Games\": 10}}"
        )

        res = service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        plan_dict = {"Math": 20, "Science": 15, "Reading": 15, "Speaking": 10, "Homework": 10, "Games": 10}
        try:
            clean_json = raw_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            if isinstance(parsed, dict):
                plan_dict = parsed
        except Exception:
            pass

        plan = DailyStudyPlan.objects.create(
            student=student,
            plan_json=json.dumps(plan_dict),
            total_target_minutes=80,
            total_completed_minutes=0,
            completion_percentage=0.0
        )

        return plan
