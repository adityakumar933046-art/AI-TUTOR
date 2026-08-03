from tutor.models import ReadingPassage, ReadingSession, ChatSession

DEFAULT_PASSAGES = [
    {
        "title": "The Little Red Fox",
        "subject": "English",
        "difficulty_level": "Beginner",
        "content_text": "The little red fox ran through the green forest. He saw a shiny golden key under a big oak tree. Curiosity filled his brave heart as he picked up the magical key.",
        "language": "en-US"
    },
    {
        "title": "How Plants Produce Oxygen",
        "subject": "Science",
        "difficulty_level": "Intermediate",
        "content_text": "Plants use sunlight, water, and carbon dioxide to make food through a process called photosynthesis. During this process, plants release fresh oxygen into the air, which helps all living creatures breathe.",
        "language": "en-US"
    },
    {
        "title": "The Secrets of Space & Planets",
        "subject": "Science",
        "difficulty_level": "Advanced",
        "content_text": "Our solar system consists of the Sun and eight celestial planets orbiting around it. Gravity keeps these giant spheres in constant motion across the dark expanse of space.",
        "language": "en-US"
    }
]

class ReadingPassageService:
    @staticmethod
    def seed_default_passages():
        for item in DEFAULT_PASSAGES:
            words = item['content_text'].split()
            ReadingPassage.objects.get_or_create(
                title=item['title'],
                defaults={
                    'subject': item['subject'],
                    'difficulty_level': item['difficulty_level'],
                    'content_text': item['content_text'],
                    'word_count': len(words),
                    'language': item['language']
                }
            )

    @staticmethod
    def start_reading_session(student, passage_id, mode='independent', language='en-US'):
        passage = ReadingPassage.objects.filter(id=passage_id).first()
        if not passage:
            ReadingPassageService.seed_default_passages()
            passage = ReadingPassage.objects.first()

        chat_session = ChatSession.objects.filter(student=student).first()
        if not chat_session:
            chat_session = ChatSession.objects.create(
                student=student,
                subject=passage.subject,
                title=f"Reading Coach - {passage.title}"
            )

        session = ReadingSession.objects.create(
            student=student,
            passage=passage,
            chat_session=chat_session,
            mode=mode,
            language=language
        )
        return session
