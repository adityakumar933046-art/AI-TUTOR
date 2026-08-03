from tutor.models import Recommendation

DEFAULT_RECOMMENDATIONS = [
    {
        "target_role": "student",
        "action_text": "Play 1 Math Match-Pair game on Fractions to boost your daily streak! 🃏",
        "category": "Game Challenge"
    },
    {
        "target_role": "parent",
        "action_text": "Encourage 10 minutes of English story reading to support vocabulary growth. 📖",
        "category": "Parent Guidance"
    }
]

class AIRecommendationService:
    @staticmethod
    def get_or_seed_recommendations(student):
        for item in DEFAULT_RECOMMENDATIONS:
            Recommendation.objects.get_or_create(
                student=student,
                target_role=item['target_role'],
                action_text=item['action_text'],
                defaults={'category': item['category']}
            )
        return Recommendation.objects.filter(student=student, is_dismissed=False)
