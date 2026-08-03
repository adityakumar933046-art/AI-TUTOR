from tutor.models import Mission

DEFAULT_MISSIONS = [
    {
        "title": "Daily Reading Quest",
        "description": "Complete 1 story reading session in AI Reading Coach!",
        "target_count": 1,
        "xp_reward": 50,
        "coins_reward": 25,
        "period": "daily"
    },
    {
        "title": "Math Master Challenge",
        "description": "Solve 3 math problems on the AI Whiteboard!",
        "target_count": 3,
        "xp_reward": 75,
        "coins_reward": 40,
        "period": "daily"
    },
    {
        "title": "Speech & Speaking Practice",
        "description": "Practice speaking for 5 minutes in Speaking Coach!",
        "target_count": 1,
        "xp_reward": 100,
        "coins_reward": 50,
        "period": "weekly"
    }
]

class MissionService:
    @staticmethod
    def get_or_seed_missions(student):
        for item in DEFAULT_MISSIONS:
            Mission.objects.get_or_create(
                student=student,
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'target_count': item['target_count'],
                    'xp_reward': item['xp_reward'],
                    'coins_reward': item['coins_reward'],
                    'period': item['period']
                }
            )
        return Mission.objects.filter(student=student)
