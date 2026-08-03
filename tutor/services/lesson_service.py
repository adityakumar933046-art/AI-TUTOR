import json
from tutor.models import VisualLesson, LessonDiagram, LessonHistory, BookmarkedLesson, ChatSession, ChatMessage

class LessonManagerService:
    def __init__(self, student):
        self.student = student

    def create_or_get_visual_lesson(self, topic, subject='General Knowledge', payload=None):
        chat_session = ChatSession.objects.filter(student=self.student).first()
        if not chat_session:
            chat_session = ChatSession.objects.create(
                student=self.student,
                subject=subject,
                title=f"Visual Learning - {topic}"
            )

        vis_type = payload.get('visualization_type', 'Flowchart') if payload else 'Flowchart'
        explanation = payload.get('explanation', '') if payload else ''
        analogy = payload.get('analogy', '') if payload else ''
        mermaid_script = payload.get('mermaid_script', '') if payload else ''
        quiz_data = json.dumps(payload.get('quiz', [])) if payload else '[]'
        summary_text = "\n".join(payload.get('summary', [])) if payload else ''

        lesson = VisualLesson.objects.create(
            student=self.student,
            chat_session=chat_session,
            topic=topic,
            subject=subject,
            visualization_type=vis_type,
            explanation_text=explanation,
            analogy_text=analogy,
            diagram_data=mermaid_script,
            quiz_data=quiz_data,
            summary_text=summary_text
        )

        LessonDiagram.objects.create(
            lesson=lesson,
            diagram_type=vis_type.lower().replace(' ', '_'),
            code_definition=mermaid_script
        )

        LessonHistory.objects.create(
            student=self.student,
            lesson=lesson
        )

        # Log to shared ChatMessage history
        ChatMessage.objects.create(
            session=chat_session,
            role='user',
            content=f"[Visual Learning Requested]: {topic}"
        )
        ChatMessage.objects.create(
            session=chat_session,
            role='model',
            content=f"I generated a visual {vis_type} diagram for '{topic}'! {explanation[:150]}..."
        )

        return lesson

    def toggle_bookmark(self, lesson_id):
        lesson = VisualLesson.objects.filter(id=lesson_id, student=self.student).first()
        if not lesson:
            return False

        lesson.is_bookmarked = not lesson.is_bookmarked
        lesson.save()

        if lesson.is_bookmarked:
            BookmarkedLesson.objects.get_or_create(student=self.student, lesson=lesson)
        else:
            BookmarkedLesson.objects.filter(student=self.student, lesson=lesson).delete()

        return lesson.is_bookmarked
