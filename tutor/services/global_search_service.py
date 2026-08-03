from django.db.models import Q
from django.contrib.auth import get_user_model
from tutor.models import (
    ChatSession, Homework, VisualLesson, ReadingSession, SpeakingSession, Game
)

User = get_user_model()

class GlobalSearchEngine:
    @staticmethod
    def search_all(query_str):
        if not query_str or len(query_str.strip()) < 2:
            return {
                'query': query_str,
                'students': [],
                'parents': [],
                'chats': [],
                'homeworks': [],
                'lessons': [],
                'readings': [],
                'speakings': [],
                'games': [],
                'total_results': 0
            }

        q = query_str.strip()

        students = User.objects.filter(role='Student').filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(email__icontains=q)
        )[:5]

        parents = User.objects.filter(role='Parent').filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(email__icontains=q)
        )[:5]

        chats = ChatSession.objects.filter(
            Q(title__icontains=q) | Q(subject__icontains=q)
        )[:5]

        homeworks = Homework.objects.filter(
            Q(title__icontains=q) | Q(subject__icontains=q)
        )[:5]

        lessons = VisualLesson.objects.filter(
            Q(topic__icontains=q) | Q(subject__icontains=q)
        )[:5]

        readings = ReadingSession.objects.filter(
            Q(passage__title__icontains=q) | Q(passage__subject__icontains=q)
        )[:5]

        speakings = SpeakingSession.objects.filter(
            Q(scenario__title__icontains=q) | Q(scenario__category__icontains=q)
        )[:5]

        games = Game.objects.filter(
            Q(title__icontains=q) | Q(subject__icontains=q)
        )[:5]

        total_results = (
            len(students) + len(parents) + len(chats) + len(homeworks) +
            len(lessons) + len(readings) + len(speakings) + len(games)
        )

        return {
            'query': q,
            'students': students,
            'parents': parents,
            'chats': chats,
            'homeworks': homeworks,
            'lessons': lessons,
            'readings': readings,
            'speakings': speakings,
            'games': games,
            'total_results': total_results
        }
