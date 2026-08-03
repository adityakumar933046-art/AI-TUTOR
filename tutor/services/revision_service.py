from datetime import date, timedelta
from tutor.models import RevisionSchedule

class SpacedRevisionService:
    @staticmethod
    def schedule_spaced_revisions(student, topic='Fractions'):
        intervals = [1, 3, 7, 14, 30]
        schedules = []
        today = date.today()

        for days in intervals:
            sch, _ = RevisionSchedule.objects.get_or_create(
                student=student,
                topic=topic,
                interval_days=days,
                defaults={'scheduled_date': today + timedelta(days=days)}
            )
            schedules.append(sch)
        return schedules

    @staticmethod
    def get_due_revisions(student):
        SpacedRevisionService.schedule_spaced_revisions(student, topic='Fractions')
        return RevisionSchedule.objects.filter(student=student, is_completed=False)
