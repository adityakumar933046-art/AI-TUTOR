import logging
from django.utils import timezone
from tutor.models import VoiceSession, VoiceTranscript, VoiceSettings, AudioMetadata, ChatMessage
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

class VoiceTutorService:
    def __init__(self, student, chat_session):
        self.student = student
        self.chat_session = chat_session
        self.settings, _ = VoiceSettings.objects.get_or_create(student=student)

    def get_or_create_active_voice_session(self, mode='push_to_talk'):
        active_session = VoiceSession.objects.filter(
            student=self.student,
            chat_session=self.chat_session,
            ended_at__isnull=True
        ).first()

        if not active_session:
            active_session = VoiceSession.objects.create(
                student=self.student,
                chat_session=self.chat_session,
                mode=mode
            )
        return active_session

    def process_student_voice_turn(self, spoken_text, mode='push_to_talk', language='en-US', duration_ms=0):
        """
        1. Logs spoken student transcript to VoiceTranscript & ChatMessage.
        2. Queries Gemini API via GeminiTutorService using shared context memory.
        3. Logs AI teacher transcript to VoiceTranscript & ChatMessage.
        4. Returns structured JSON for voice synthesis.
        """
        voice_session = self.get_or_create_active_voice_session(mode=mode)

        # 1. Log Student Voice Transcript & ChatMessage
        student_transcript = VoiceTranscript.objects.create(
            voice_session=voice_session,
            speaker='student',
            transcript_text=spoken_text,
            language=language
        )
        AudioMetadata.objects.create(
            transcript=student_transcript,
            duration_ms=duration_ms
        )
        user_chat_msg = ChatMessage.objects.create(
            session=self.chat_session,
            role='user',
            content=spoken_text
        )

        # 2. Query Gemini API with teacher persona & shared conversation memory
        gemini_service = GeminiTutorService(subject=self.chat_session.subject)
        history = self.chat_session.messages.exclude(id=user_chat_msg.id)
        
        # Add voice specific instruction wrapper
        voice_prompt = (
            f"The student just spoke to you via voice: '{spoken_text}'. "
            f"Respond concisely in natural conversational language suitable for spoken speech reading. "
            f"Keep math formulas clear and easy to listen to."
        )
        
        res = gemini_service.generate_tutor_response(voice_prompt, chat_history=history)
        ai_response_text = res.get('response', "That's a great question! Let's explore it together.")

        # 3. Log AI Teacher Transcript & ChatMessage
        ai_transcript = VoiceTranscript.objects.create(
            voice_session=voice_session,
            speaker='ai_tutor',
            transcript_text=ai_response_text,
            language=language
        )
        ai_chat_msg = ChatMessage.objects.create(
            session=self.chat_session,
            role='model',
            content=ai_response_text
        )

        self.chat_session.save()

        return {
            "success": True,
            "voice_session_id": voice_session.id,
            "student_text": spoken_text,
            "ai_response": ai_response_text,
            "language": language,
            "speaking_rate": self.settings.speaking_rate,
            "pitch": self.settings.pitch,
            "voice_gender": self.settings.voice_gender,
            "timestamp": ai_transcript.timestamp.strftime('%H:%M')
        }
