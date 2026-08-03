from tutor.models import SkillNode, SkillProgress

DEFAULT_SKILL_NODES = [
    {"subject": "Math", "name": "Numbers & Counting", "order": 1},
    {"subject": "Math", "name": "Addition & Subtraction", "order": 2},
    {"subject": "Math", "name": "Multiplication & Division", "order": 3},
    {"subject": "Math", "name": "Fractions & Decimals", "order": 4},
    {"subject": "Science", "name": "Living Things & Plants", "order": 1},
    {"subject": "Science", "name": "Photosynthesis & Solar Power", "order": 2},
    {"subject": "English", "name": "Vocabulary & Phonics", "order": 1},
    {"subject": "English", "name": "Sentence Structure & Grammar", "order": 2},
]

class KnowledgeGraphService:
    @staticmethod
    def seed_and_get_student_skills(student):
        for item in DEFAULT_SKILL_NODES:
            node, _ = SkillNode.objects.get_or_create(
                subject=item['subject'],
                name=item['name'],
                defaults={'order': item['order']}
            )
            SkillProgress.objects.get_or_create(
                student=student,
                skill_node=node,
                defaults={'status': 'learning' if item['order'] == 1 else 'not_started', 'mastery_percentage': 85.0 if item['order'] == 1 else 0.0}
            )

        return SkillProgress.objects.filter(student=student)
