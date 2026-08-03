class GamificationService:
    @staticmethod
    def calculate_next_difficulty(current_difficulty, accuracy_percentage):
        diff_order = ['Easy', 'Medium', 'Hard', 'Challenge', 'Master']
        idx = diff_order.index(current_difficulty) if current_difficulty in diff_order else 0

        if accuracy_percentage >= 90.0 and idx < len(diff_order) - 1:
            return diff_order[idx + 1]
        elif accuracy_percentage < 50.0 and idx > 0:
            return diff_order[idx - 1]
        return current_difficulty
