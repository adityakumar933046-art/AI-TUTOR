import logging
from tutor.models import SpeakingSession, ConversationHistory, ChatSession, ChatMessage
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

class SpeakingCoachEngine:
    def __init__(self, student, session):
        self.student = student
        self.session = session

    def process_spoken_turn(self, spoken_text):
        # 1. Log student turn
        student_turn = ConversationHistory.objects.create(
            session=self.session,
            speaker='student',
            text_content=spoken_text
        )

        # 2. Build history context for Gemini
        history_turns = self.session.turns.all()
        history_list = []
        for turn in history_turns:
            role = 'user' if turn.speaker == 'student' else 'model'
            history_list.append({'role': role, 'content': turn.text_content})

        scenario = self.session.scenario
        system_instruction = f"Roleplay Scenario: '{scenario.title}'. Role: '{scenario.ai_role_name}'. {scenario.system_prompt}"

        gemini_service = GeminiTutorService(subject='English')
        gemini_service.system_instruction = system_instruction

        res_dict = gemini_service.generate_tutor_response(spoken_text, chat_history=self.session.chat_session.messages.all() if self.session.chat_session else [])
        ai_reply = res_dict.get('response', f"That is wonderful! Tell me more about what you think.")

        # 3. Log AI coach turn
        ai_turn = ConversationHistory.objects.create(
            session=self.session,
            speaker='ai_coach',
            text_content=ai_reply
        )

        # 4. Sync to shared ChatMessage history
        if self.session.chat_session:
            ChatMessage.objects.create(
                session=self.session.chat_session,
                role='user',
                content=f"[Speaking Coach - {scenario.title}]: {spoken_text}"
            )
            ChatMessage.objects.create(
                session=self.session.chat_session,
                role='model',
                content=ai_reply
            )

        return {
            'success': True,
            'student_turn_id': student_turn.id,
            'ai_reply': ai_reply,
            'ai_role_name': scenario.ai_role_name
        }
