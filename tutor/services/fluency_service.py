import logging
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

READING_FEEDBACK_INSTRUCTION = (
    "You are Sparky, an encouraging and friendly AI Reading Coach for EduVerse AI Kids. "
    "Evaluate the child's reading attempt with warm praise. Highlight what they did great (accuracy, pacing, or effort) "
    "and give gentle constructive tips on any mispronounced or skipped words. Never use harsh grades."
)

class FluencyAnalysisService:
    @staticmethod
    def calculate_wpm(word_count, duration_seconds):
        if duration_seconds <= 0:
            return 0.0
        wpm = (word_count / duration_seconds) * 60.0
        return round(wpm, 1)

    @staticmethod
    def calculate_fluency_score(wpm, target_wpm=90.0):
        if wpm <= 0:
            return 0.0
        ratio = min(wpm / target_wpm, 1.2)
        score = min(ratio * 85.0, 100.0)
        return round(score, 1)

    @staticmethod
    def generate_gemini_reading_feedback(passage_title, spoken_transcript, accuracy_score, wpm, mispronounced_words):
        gemini_service = GeminiTutorService(subject='English')

        mis_str = ", ".join([w.get('target', '') for w in mispronounced_words]) if mispronounced_words else "none"

        prompt = (
            f"Child read passage '{passage_title}'.\n"
            f"Spoken Transcript: '{spoken_transcript}'\n"
            f"Accuracy: {accuracy_score}%, Pace: {wpm} WPM. Mispronounced words: {mis_str}.\n"
            f"{READING_FEEDBACK_INSTRUCTION}"
        )

        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        return res.get('response', f"Great effort reading '{passage_title}'! You scored {accuracy_score}% accuracy!")
