from django.contrib.auth import get_user_model
from tutor.models import StudentReward, LeaderboardEntry

User = get_user_model()

class LeaderboardService:
    @staticmethod
    def calculate_weekly_rankings():
        rewards = StudentReward.objects.all().order_by('-total_xp')
        rankings = []
        for idx, rew in enumerate(rewards, start=1):
            entry, _ = LeaderboardEntry.objects.get_or_create(
                student=rew.student,
                defaults={'weekly_xp': rew.total_xp, 'rank_position': idx}
            )
            entry.weekly_xp = rew.total_xp
            entry.rank_position = idx
            entry.save()
            rankings.append({
                'rank': idx,
                'username': rew.student.username,
                'total_xp': rew.total_xp,
                'coins': rew.coins_balance
            })
        return rankings
