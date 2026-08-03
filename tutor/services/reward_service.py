import json
from tutor.models import StudentReward, GameResult, GameSession

class RewardService:
    @staticmethod
    def get_or_create_profile(student):
        profile, _ = StudentReward.objects.get_or_create(student=student)
        return profile

    @staticmethod
    def award_game_completion(student, session, score, max_score):
        profile = RewardService.get_or_create_profile(student)

        accuracy = round((score / max(max_score, 1)) * 100, 1)
        xp = int(accuracy * 1.5)
        coins = int(accuracy * 0.8)
        stars = 3 if accuracy >= 85 else (2 if accuracy >= 60 else 1)

        result, _ = GameResult.objects.get_or_create(
            session=session,
            defaults={
                'xp_earned': xp,
                'coins_earned': coins,
                'stars_earned': stars,
                'accuracy_percentage': accuracy,
                'feedback_text': f"Great job playing! You achieved {accuracy}% accuracy!"
            }
        )

        profile.total_xp += xp
        profile.coins_balance += coins
        profile.save()

        session.score = score
        session.max_score = max_score
        session.status = 'completed'
        session.save()

        return {
            'accuracy': accuracy,
            'xp': xp,
            'coins': coins,
            'stars': stars,
            'new_balance': profile.coins_balance,
            'total_xp': profile.total_xp
        }

    @staticmethod
    def purchase_store_item(student, item_id, item_cost):
        profile = RewardService.get_or_create_profile(student)
        if profile.coins_balance < item_cost:
            return {'success': False, 'error': 'Insufficient coins balance.'}

        try:
            unlocked = json.loads(profile.unlocked_items_json)
        except Exception:
            unlocked = []

        if item_id in unlocked:
            return {'success': False, 'error': 'Item is already unlocked!'}

        unlocked.append(item_id)
        profile.coins_balance -= item_cost
        profile.unlocked_items_json = json.dumps(unlocked)
        profile.save()

        return {
            'success': True,
            'coins_balance': profile.coins_balance,
            'unlocked_items': unlocked
        }
