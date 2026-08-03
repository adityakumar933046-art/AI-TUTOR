import json
import logging
from django.utils import timezone
from tutor.models import Whiteboard, WhiteboardElement, DrawingHistory, AutoSaveSnapshot, ChatSession

logger = logging.getLogger(__name__)

class WhiteboardService:
    def __init__(self, student, whiteboard=None):
        self.student = student
        self.whiteboard = whiteboard

    def create_whiteboard(self, title='New Math Workspace', mode='Math Practice', chat_session=None):
        if not chat_session:
            chat_session = ChatSession.objects.filter(student=self.student).first()
            if not chat_session:
                chat_session = ChatSession.objects.create(
                    student=self.student,
                    subject='Math',
                    title=f"Math Workspace Chat"
                )

        whiteboard = Whiteboard.objects.create(
            student=self.student,
            chat_session=chat_session,
            title=title,
            mode=mode,
            canvas_json='{}'
        )
        return whiteboard

    def save_canvas_state(self, canvas_json, thumbnail_url='', is_auto_save=False):
        if not self.whiteboard:
            return None

        self.whiteboard.canvas_json = canvas_json
        if thumbnail_url:
            self.whiteboard.thumbnail_url = thumbnail_url
        self.whiteboard.save()

        # Log auto-save snapshot
        if is_auto_save:
            AutoSaveSnapshot.objects.create(
                whiteboard=self.whiteboard,
                snapshot_data=canvas_json
            )
            # Retain max 5 auto-saves
            old_saves = AutoSaveSnapshot.objects.filter(whiteboard=self.whiteboard)[5:]
            for s in old_saves:
                s.delete()

        # Log drawing history
        DrawingHistory.objects.create(
            whiteboard=self.whiteboard,
            snapshot_json=canvas_json,
            action_type='auto_save' if is_auto_save else 'save'
        )

        return self.whiteboard

    def duplicate_whiteboard(self):
        if not self.whiteboard:
            return None

        new_board = Whiteboard.objects.create(
            student=self.student,
            chat_session=self.whiteboard.chat_session,
            title=f"{self.whiteboard.title} (Copy)",
            mode=self.whiteboard.mode,
            canvas_json=self.whiteboard.canvas_json,
            thumbnail_url=self.whiteboard.thumbnail_url
        )
        return new_board
