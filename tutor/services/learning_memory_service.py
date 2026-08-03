import json
import logging
from tutor.models import LearningProfile

logger = logging.getLogger(__name__)

class LearningMemoryService:
    @staticmethod
    def get_or_create_profile(student):
        profile, _ = LearningProfile.objects.get_or_create(student=student)
        return profile

    @staticmethod
    def record_activity_impact(student, subject='Math', topic='Fractions', score_pct=85.0):
        profile = LearningMemoryService.get_or_create_profile(student)

        try:
            weaks = json.loads(profile.weak_concepts_json)
        except Exception:
            weaks = []

        try:
            strongs = json.loads(profile.strong_concepts_json)
        except Exception:
            strongs = []

        if score_pct >= 80.0:
            if topic in weaks:
                weaks.remove(topic)
            if topic not in strongs:
                strongs.append(topic)
        elif score_pct < 60.0:
            if topic not in weaks:
                weaks.append(topic)
            if topic in strongs:
                strongs.remove(topic)

        profile.weak_concepts_json = json.dumps(weaks)
        profile.strong_concepts_json = json.dumps(strongs)
        profile.confidence_score = min(100.0, max(50.0, (profile.confidence_score * 0.9) + (score_pct * 0.1)))
        profile.save()

        return profile
