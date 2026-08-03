import logging
from tutor.models import SpeakingFeedback, GrammarCorrection, VocabularyProgress
from tutor.services.grammar_service import GrammarAnalysisService
from tutor.services.vocabulary_service import VocabularyBuilderService
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

class SpeakingFeedbackEngine:
    @staticmethod
    def generate_session_feedback(session):
        turns = session.turns.all()
        grammar_data = GrammarAnalysisService.analyze_session_grammar(turns)
        vocab_data = VocabularyBuilderService.analyze_session_vocabulary(turns)

        turn_count = turns.filter(speaker='student').count()
        fluency_score = min(100.0, 70.0 + (turn_count * 5.0))
        confidence_score = min(100.0, 75.0 + (turn_count * 4.0))

        overall_score = round(
            (grammar_data['grammar_score'] * 0.3) +
            (vocab_data['vocabulary_score'] * 0.3) +
            (fluency_score * 0.2) +
            (confidence_score * 0.2),
            1
        )

        gemini_service = GeminiTutorService(subject='English')
        prompt = (
            f"Generate a child-friendly speaking coach report for scenario '{session.scenario.title}'.\n"
            f"Student completed {turn_count} turns.\n"
            f"Overall score: {overall_score}%. Give warm praise and 2 encouraging tips."
        )
        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        summary_report = res.get('response', f"Great job practicing '{session.scenario.title}'! You scored {overall_score}%!")

        xp_earned = int(overall_score * 2.5)

        feedback_obj, _ = SpeakingFeedback.objects.get_or_create(
            session=session,
            defaults={
                'grammar_score': grammar_data['grammar_score'],
                'vocabulary_score': vocab_data['vocabulary_score'],
                'fluency_score': fluency_score,
                'confidence_score': confidence_score,
                'overall_speaking_score': overall_score,
                'summary_report': summary_report,
                'xp_earned': xp_earned
            }
        )

        # Save grammar corrections
        for corr in grammar_data['corrections']:
            GrammarCorrection.objects.create(
                feedback=feedback_obj,
                original_sentence=corr['original'],
                corrected_sentence=corr['corrected'],
                explanation_rule=corr['rule']
            )

        # Save vocabulary progress
        for upg in vocab_data['upgrades']:
            VocabularyProgress.objects.create(
                student=session.student,
                word=upg['word'],
                better_synonym=upg['better_synonym']
            )

        session.status = 'completed'
        session.save()

        return {
            'overall_score': overall_score,
            'grammar_score': grammar_data['grammar_score'],
            'vocabulary_score': vocab_data['vocabulary_score'],
            'fluency_score': fluency_score,
            'confidence_score': confidence_score,
            'summary_report': summary_report,
            'corrections': grammar_data['corrections'],
            'upgrades': vocab_data['upgrades'],
            'xp_earned': xp_earned
        }
