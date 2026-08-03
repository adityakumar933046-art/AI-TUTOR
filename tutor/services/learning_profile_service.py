from tutor.models import LearningInsight
from tutor.services.learning_memory_service import LearningMemoryService

class LearningProfileAnalyticsService:
    @staticmethod
    def get_learning_insights(student):
        profile = LearningMemoryService.get_or_create_profile(student)

        insight, _ = LearningInsight.objects.get_or_create(
            student=student,
            defaults={
                'strength_summary': 'Strong understanding of Addition, Vocabulary & Visual Flowcharts.',
                'weakness_summary': 'Needs extra practice on Fractions & Past Tense Verbs.',
                'predicted_milestone': '85% Likelihood of mastering Grade 4 Math by end of month!'
            }
        )

        return {
            'profile': profile,
            'learning_style': profile.preferred_learning_style,
            'confidence_score': profile.confidence_score,
            'strength_summary': insight.strength_summary,
            'weakness_summary': insight.weakness_summary,
            'predicted_milestone': insight.predicted_milestone
        }
