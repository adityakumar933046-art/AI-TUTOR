from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    SUBJECT_CHOICES = (
        ('Math', 'Mathematics 🔢'),
        ('Science', 'Science 🔬'),
        ('English', 'English & Reading 📖'),
        ('History', 'World History 🏛️'),
        ('Geography', 'Geography & Earth 🌍'),
        ('General Knowledge', 'General Knowledge 💡'),
        ('Coding', 'Computer Coding 💻'),
        ('Reasoning', 'Logic & Reasoning 🧠'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    title = models.CharField(max_length=200, default='New Learning Session')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='General Knowledge')
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"[{self.subject}] {self.title} - ({self.student.username})"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'Student'),
        ('model', 'AI Tutor'),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    token_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session.title} [{self.role}]: {self.content[:40]}..."


# ==========================================
# PHASE 3: VOICE TUTOR MODELS
# ==========================================
class VoiceSettings(models.Model):
    LANGUAGE_CHOICES = (
        ('en-US', 'English (US)'),
        ('hi-IN', 'Hindi (भारत)'),
        ('en-IN', 'Hinglish / Indian English'),
    )

    GENDER_CHOICES = (
        ('Female', 'Female (Friendly Teacher)'),
        ('Male', 'Male (Encouraging Mentor)'),
    )

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voice_settings'
    )
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='en-US')
    voice_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Female')
    speaking_rate = models.FloatField(default=1.0)
    pitch = models.FloatField(default=1.0)
    auto_listen = models.BooleanField(default=True)
    auto_read = models.BooleanField(default=True)
    wake_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VoiceSettings for {self.student.username} ({self.language})"


class VoiceSession(models.Model):
    MODE_CHOICES = (
        ('push_to_talk', 'Push to Talk'),
        ('hold_to_talk', 'Hold to Talk'),
        ('continuous', 'Continuous Conversation'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voice_sessions'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='voice_sessions'
    )
    mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='push_to_talk')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_duration_seconds = models.IntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"VoiceSession ({self.mode}) - {self.student.username} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class VoiceTranscript(models.Model):
    SPEAKER_CHOICES = (
        ('student', 'Student Spoken'),
        ('ai_tutor', 'AI Teacher Spoken'),
    )

    voice_session = models.ForeignKey(
        VoiceSession,
        on_delete=models.CASCADE,
        related_name='transcripts'
    )
    speaker = models.CharField(max_length=20, choices=SPEAKER_CHOICES)
    transcript_text = models.TextField()
    language = models.CharField(max_length=20, default='en-US')
    confidence_score = models.FloatField(default=0.95)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.speaker}] {self.transcript_text[:30]}..."


class AudioMetadata(models.Model):
    transcript = models.OneToOneField(
        VoiceTranscript,
        on_delete=models.CASCADE,
        related_name='audio_metadata'
    )
    audio_format = models.CharField(max_length=30, default='audio/webm')
    sample_rate = models.IntegerField(default=44100)
    duration_ms = models.IntegerField(default=0)
    file_size_bytes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AudioMeta ({self.audio_format}, {self.duration_ms}ms)"


# ==========================================
# PHASE 4: AI WHITEBOARD & MATH MODELS
# ==========================================
class Whiteboard(models.Model):
    MODE_CHOICES = (
        ('Drawing', 'Freehand Drawing 🎨'),
        ('Math Practice', 'Math Practice 🔢'),
        ('Geometry', 'Geometry 📐'),
        ('Mind Map', 'Mind Map 🧠'),
        ('Science Diagram', 'Science Diagram 🔬'),
        ('Flowchart', 'Flowchart 🔀'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='whiteboards'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='whiteboards',
        null=True, blank=True
    )
    title = models.CharField(max_length=200, default='New Math Workspace')
    mode = models.CharField(max_length=50, choices=MODE_CHOICES, default='Math Practice')
    canvas_json = models.TextField(default='{}')
    thumbnail_url = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"[{self.mode}] {self.title} - ({self.student.username})"


class WhiteboardElement(models.Model):
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='elements'
    )
    element_type = models.CharField(max_length=50)
    element_data = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Element {self.element_type} on Board {self.whiteboard.id}"


class DrawingHistory(models.Model):
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='history'
    )
    snapshot_json = models.TextField()
    action_type = models.CharField(max_length=50, default='draw')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class MathSession(models.Model):
    STATUS_CHOICES = (
        ('solving', 'Solving'),
        ('solved', 'Solved'),
        ('hint_given', 'Hint Provided'),
    )

    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='math_sessions'
    )
    detected_expression = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solving')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MathSession ({self.detected_expression}) on Board {self.whiteboard.id}"


class MathSolution(models.Model):
    math_session = models.ForeignKey(
        MathSession,
        on_delete=models.CASCADE,
        related_name='solutions'
    )
    final_answer = models.TextField()
    step_by_step_explanation = models.TextField()
    hint_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solution to: {self.math_session.detected_expression}"


class AutoSaveSnapshot(models.Model):
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='autosaves'
    )
    snapshot_data = models.TextField()
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']


# ==========================================
# PHASE 5: AI VISUAL LEARNING ENGINE MODELS
# ==========================================
class VisualLesson(models.Model):
    VISUAL_CHOICES = (
        ('Flowchart', 'Interactive Flowchart 🔀'),
        ('Mind Map', 'Mind Map Concept 🧠'),
        ('Timeline', 'Historical Timeline ⏳'),
        ('Chart', 'Data Chart / Graph 📊'),
        ('Cycle Diagram', 'Cycle Diagram 🔄'),
        ('Interactive Cards', 'Visual Step Cards 🎴'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visual_lessons'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='visual_lessons',
        null=True, blank=True
    )
    topic = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, default='General Knowledge')
    visualization_type = models.CharField(max_length=50, choices=VISUAL_CHOICES, default='Flowchart')
    explanation_text = models.TextField()
    analogy_text = models.TextField(blank=True)
    diagram_data = models.TextField()
    quiz_data = models.TextField(default='[]')
    summary_text = models.TextField(blank=True)
    is_bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.visualization_type}] {self.topic} ({self.student.username})"


class LessonDiagram(models.Model):
    lesson = models.ForeignKey(
        VisualLesson,
        on_delete=models.CASCADE,
        related_name='diagrams'
    )
    diagram_type = models.CharField(max_length=50, default='flowchart')
    code_definition = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagram ({self.diagram_type}) for Lesson {self.lesson.id}"


class AnimationAsset(models.Model):
    lesson = models.ForeignKey(
        VisualLesson,
        on_delete=models.CASCADE,
        related_name='animations'
    )
    animation_type = models.CharField(max_length=50, default='lottie')
    asset_url = models.TextField(blank=True)
    animation_config = models.TextField(default='{}')

    def __str__(self):
        return f"Animation ({self.animation_type}) for Lesson {self.lesson.id}"


class LessonHistory(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_history'
    )
    lesson = models.ForeignKey(
        VisualLesson,
        on_delete=models.CASCADE,
        related_name='view_history'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']


class BookmarkedLesson(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_lessons'
    )
    lesson = models.ForeignKey(
        VisualLesson,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bookmarked_at']


# ==========================================
# PHASE 6: AI HOMEWORK SCANNER & OCR MODELS
# ==========================================
class Homework(models.Model):
    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy 🟢'),
        ('Medium', 'Medium 🟡'),
        ('Hard', 'Hard 🔴'),
        ('Challenge', 'Challenge 🏆'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Scan'),
        ('processing', 'OCR Processing'),
        ('analyzed', 'Analyzed'),
        ('completed', 'Completed'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='homeworks'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='homeworks',
        null=True, blank=True
    )
    title = models.CharField(max_length=200, default='Scanned Homework')
    subject = models.CharField(max_length=50, default='General Knowledge')
    difficulty_level = models.CharField(max_length=30, choices=DIFFICULTY_CHOICES, default='Medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    is_bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.subject}] {self.title} - ({self.student.username})"


class HomeworkFile(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_obj = models.FileField(upload_to='homework_uploads/')
    file_type = models.CharField(max_length=30, default='image')
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File: {self.original_filename} ({self.file_type})"


class OCRResult(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='ocr_results'
    )
    extracted_text = models.TextField()
    cleaned_text = models.TextField()
    confidence_score = models.FloatField(default=0.95)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCRResult for HW {self.homework.id} ({self.confidence_score*100:.0f}%)"


class DetectedQuestion(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_number = models.IntegerField(default=1)
    question_text = models.TextField()
    subject_tag = models.CharField(max_length=50, default='General Knowledge')
    difficulty = models.CharField(max_length=30, default='Medium')
    step_by_step_solution = models.TextField()
    hint_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:30]}..."


class HomeworkAnalysis(models.Model):
    homework = models.OneToOneField(
        Homework,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    summary_overview = models.TextField()
    key_concepts_found = models.TextField(default='[]')
    student_errors_found = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for HW {self.homework.id}"


class HomeworkAttempt(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    student_submission_text = models.TextField()
    ai_feedback = models.TextField()
    score_achieved = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class PracticeQuestion(models.Model):
    question = models.ForeignKey(
        DetectedQuestion,
        on_delete=models.CASCADE,
        related_name='practice_questions'
    )
    difficulty = models.CharField(max_length=30, default='Medium')
    question_text = models.TextField()
    options_json = models.TextField(default='[]')
    correct_index = models.IntegerField(default=0)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Practice ({self.difficulty}) for Q{self.question.question_number}"


class HomeworkHistory(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='homework_history'
    )
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='view_history'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']


# ==========================================
# PHASE 7: AI READING COACH & PRONUNCIATION MODELS
# ==========================================
class ReadingPassage(models.Model):
    DIFFICULTY_CHOICES = (
        ('Beginner', 'Beginner 🌱'),
        ('Intermediate', 'Intermediate 🌿'),
        ('Advanced', 'Advanced 🌳'),
    )

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, default='English')
    difficulty_level = models.CharField(max_length=30, choices=DIFFICULTY_CHOICES, default='Beginner')
    content_text = models.TextField()
    word_count = models.IntegerField(default=0)
    audio_url = models.TextField(blank=True)
    language = models.CharField(max_length=20, default='en-US')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.difficulty_level}] {self.title}"


class ReadingSession(models.Model):
    MODE_CHOICES = (
        ('guided', 'Guided Reading 📖'),
        ('independent', 'Independent Reading 🎤'),
        ('echo', 'Echo Reading 🔁'),
        ('challenge', 'Challenge Reading ⏱️'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_sessions'
    )
    passage = models.ForeignKey(
        ReadingPassage,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='reading_sessions',
        null=True, blank=True
    )
    mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='independent')
    language = models.CharField(max_length=20, default='en-US')
    status = models.CharField(max_length=30, default='reading')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"ReadingSession ({self.mode}) - {self.passage.title} ({self.student.username})"


class ReadingRecording(models.Model):
    session = models.OneToOneField(
        ReadingSession,
        on_delete=models.CASCADE,
        related_name='recording'
    )
    audio_format = models.CharField(max_length=30, default='audio/webm')
    duration_seconds = models.FloatField(default=0.0)
    spoken_transcript = models.TextField()
    words_per_minute = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording ({self.duration_seconds}s, {self.words_per_minute:.1f} WPM)"


class PronunciationScore(models.Model):
    session = models.OneToOneField(
        ReadingSession,
        on_delete=models.CASCADE,
        related_name='score'
    )
    accuracy_score = models.FloatField(default=0.0)
    fluency_score = models.FloatField(default=0.0)
    pacing_score = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    skipped_words_count = models.IntegerField(default=0)
    repeated_words_count = models.IntegerField(default=0)
    mispronounced_words_count = models.IntegerField(default=0)
    gemini_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score {self.overall_score:.0f}% for Session {self.session.id}"


class WordAssessment(models.Model):
    STATUS_CHOICES = (
        ('correct', 'Correct 🟩'),
        ('mispronounced', 'Mispronounced 🟥'),
        ('skipped', 'Skipped 🟨'),
        ('repeated', 'Repeated 🟧'),
    )

    score = models.ForeignKey(
        PronunciationScore,
        on_delete=models.CASCADE,
        related_name='words'
    )
    target_word = models.CharField(max_length=100)
    spoken_word = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='correct')
    phoneme_hint = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"[{self.status}] {self.target_word}"


class ReadingProgress(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_progress'
    )
    total_passages_read = models.IntegerField(default=0)
    total_words_read = models.IntegerField(default=0)
    average_accuracy = models.FloatField(default=0.0)
    average_wpm = models.FloatField(default=0.0)
    total_reading_xp = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ReadingProgress for {self.student.username} ({self.total_reading_xp} XP)"


class ReadingRecommendation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_recommendations'
    )
    recommended_passage = models.ForeignKey(
        ReadingPassage,
        on_delete=models.CASCADE
    )
    target_focus_words = models.TextField(default='[]')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


# ==========================================
# PHASE 8: AI SPEAKING COACH & CONVERSATION SIMULATOR MODELS
# ==========================================
class ConversationScenario(models.Model):
    CATEGORY_CHOICES = (
        ('School', 'School & Teacher 🏫'),
        ('Restaurant', 'Ordering at Restaurant 🍕'),
        ('Doctor', 'Doctor & Health 🩺'),
        ('Airport', 'Airport & Travel ✈️'),
        ('Science', 'Science Lab Experiment 🔬'),
        ('Debate', 'Student Debate 🗣️'),
        ('Storytelling', 'Interactive Storytelling 📖'),
        ('Shopping', 'Shopping Mall 🛒'),
    )

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='School')
    description = models.TextField()
    ai_role_name = models.CharField(max_length=100, default='Sparky AI')
    initial_greeting = models.TextField()
    system_prompt = models.TextField()
    icon_class = models.CharField(max_length=100, default='bi-chat-dots-fill')

    def __str__(self):
        return f"[{self.category}] {self.title}"


class SpeakingSession(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active Conversation'),
        ('completed', 'Completed & Evaluated'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='speaking_sessions'
    )
    scenario = models.ForeignKey(
        ConversationScenario,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='speaking_sessions',
        null=True, blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    duration_seconds = models.IntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"SpeakingSession ({self.scenario.title}) - {self.student.username}"


class ConversationHistory(models.Model):
    SPEAKER_CHOICES = (
        ('student', 'Student Spoken'),
        ('ai_coach', 'AI Speaking Coach'),
    )

    session = models.ForeignKey(
        SpeakingSession,
        on_delete=models.CASCADE,
        related_name='turns'
    )
    speaker = models.CharField(max_length=20, choices=SPEAKER_CHOICES)
    text_content = models.TextField()
    audio_url = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.speaker}] {self.text_content[:30]}..."


class SpeakingFeedback(models.Model):
    session = models.OneToOneField(
        SpeakingSession,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    grammar_score = models.FloatField(default=0.0)
    vocabulary_score = models.FloatField(default=0.0)
    fluency_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    overall_speaking_score = models.FloatField(default=0.0)
    summary_report = models.TextField()
    xp_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Speaking Session {self.session.id} ({self.overall_speaking_score:.0f}%)"


class GrammarCorrection(models.Model):
    feedback = models.ForeignKey(
        SpeakingFeedback,
        on_delete=models.CASCADE,
        related_name='grammar_corrections'
    )
    original_sentence = models.TextField()
    corrected_sentence = models.TextField()
    explanation_rule = models.TextField()


class VocabularyProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vocabulary_progress'
    )
    word = models.CharField(max_length=100)
    better_synonym = models.CharField(max_length=100)
    times_used = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)


class SpeakingChallenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    xp_reward = models.IntegerField(default=50)
    is_daily = models.BooleanField(default=True)


class SpeakingAchievement(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='speaking_achievements'
    )
    badge_name = models.CharField(max_length=100)
    earned_at = models.DateTimeField(auto_now_add=True)


# ==========================================
# PHASE 9: AI GAME ENGINE & GAMIFICATION PLATFORM MODELS
# ==========================================
class Game(models.Model):
    GAME_TYPES = (
        ('match_pair', 'Match the Pair 🃏'),
        ('memory_cards', 'Memory Flip Cards 🧠'),
        ('interactive_quiz', 'Interactive Quiz ⚡'),
        ('drag_drop', 'Drag & Drop Bins 🎯'),
        ('sorting', 'Concept Sorting 🔀'),
    )

    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy 🟢'),
        ('Medium', 'Medium 🟡'),
        ('Hard', 'Hard 🔴'),
        ('Challenge', 'Challenge 🏆'),
        ('Master', 'Master 👑'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='games'
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='games',
        null=True, blank=True
    )
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, default='General Knowledge')
    game_type = models.CharField(max_length=50, choices=GAME_TYPES, default='match_pair')
    difficulty = models.CharField(max_length=30, choices=DIFFICULTY_CHOICES, default='Easy')
    config_json = models.TextField(default='{}')
    is_bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.game_type}] {self.title} ({self.student.username})"


class GameSession(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_sessions'
    )
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)
    time_spent_seconds = models.IntegerField(default=0)
    status = models.CharField(max_length=30, default='playing')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"GameSession ({self.game.title}) - Score: {self.score}/{self.max_score}"


class GameQuestion(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    correct_answer = models.TextField()
    distractors_json = models.TextField(default='[]')
    hint = models.TextField(blank=True)


class GameResult(models.Model):
    session = models.OneToOneField(
        GameSession,
        on_delete=models.CASCADE,
        related_name='result'
    )
    xp_earned = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)
    stars_earned = models.IntegerField(default=3)
    accuracy_percentage = models.FloatField(default=0.0)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GameResult (+{self.xp_earned} XP, +{self.coins_earned} Coins)"


class Mission(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Daily Mission ☀️'),
        ('weekly', 'Weekly Quest 📅'),
        ('monthly', 'Monthly Milestone 🏆'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='missions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_count = models.IntegerField(default=1)
    current_count = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=50)
    coins_reward = models.IntegerField(default=25)
    is_completed = models.BooleanField(default=False)
    period = models.CharField(max_length=30, choices=PERIOD_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.period}] {self.title} ({self.current_count}/{self.target_count})"


class Avatar(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='avatar')
    icon_class = models.CharField(max_length=100, default='bi-robot')
    cost_coins = models.IntegerField(default=100)

    def __str__(self):
        return f"Avatar ({self.name}) - {self.cost_coins} Coins"


class StudentReward(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_profile'
    )
    coins_balance = models.IntegerField(default=100)
    total_xp = models.IntegerField(default=0)
    daily_streak = models.IntegerField(default=1)
    unlocked_items_json = models.TextField(default='["sparky_robot"]')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RewardProfile for {self.student.username} ({self.coins_balance} Coins, {self.total_xp} XP)"


class LeaderboardEntry(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries'
    )
    weekly_xp = models.IntegerField(default=0)
    rank_position = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-weekly_xp']

    def __str__(self):
        return f"Rank #{self.rank_position}: {self.student.username} ({self.weekly_xp} XP)"


# ==========================================
# PHASE 10: PARENT & TEACHER DASHBOARDS, ANALYTICS & NOTIFICATION MODELS
# ==========================================
class ParentChildRelation(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linked_children'
    )
    child = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linked_parents'
    )
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return f"Parent ({self.parent.username}) -> Child ({self.child.username})"



class DailyStudyPlan(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_plans'
    )
    date = models.DateField(auto_now_add=True)
    plan_json = models.TextField(default='{"Math":20, "Science":15, "Reading":15, "Speaking":10, "Homework":10, "Games":10}')
    total_target_minutes = models.IntegerField(default=80)
    total_completed_minutes = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"StudyPlan for {self.student.username} on {self.date} ({self.completion_percentage:.0f}%)"


class DailyProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_progresses'
    )
    date = models.DateField(auto_now_add=True)
    study_time_minutes = models.IntegerField(default=0)
    chats_count = models.IntegerField(default=0)
    voice_minutes = models.IntegerField(default=0)
    whiteboards_solved = models.IntegerField(default=0)
    visual_lessons_viewed = models.IntegerField(default=0)
    homeworks_completed = models.IntegerField(default=0)
    reading_passages_read = models.IntegerField(default=0)
    speaking_sessions_done = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    xp_gained = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"DailyProgress ({self.student.username}) on {self.date} ({self.study_time_minutes}m)"


class AnalyticsSnapshot(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_snapshot'
    )
    learning_speed_score = models.FloatField(default=85.0)
    retention_trend_score = models.FloatField(default=88.0)
    weak_topics_json = models.TextField(default='["Fractions", "Past Tense"]')
    strong_topics_json = models.TextField(default='["Addition", "Vocabulary"]')
    ai_recommendation_text = models.TextField(default="Practice Fractions for 10 minutes tomorrow to build confidence!")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AnalyticsSnapshot for {self.student.username}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('hw_completed', 'Homework Completed 📝'),
        ('goal_achieved', 'Daily Goal Achieved 🎯'),
        ('badge_unlocked', 'Badge Unlocked 🏆'),
        ('inactivity', 'Study Reminder ⏰'),
        ('weak_perf', 'Needs Practice Alert 💡'),
        ('login_alert', 'New Login Alert 🔒'),
    )

    CHANNEL_CHOICES = (
        ('in_app', 'In-App Notification'),
        ('sms', 'SMS Message'),
        ('whatsapp', 'WhatsApp Message'),
        ('email', 'Email Message'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='goal_achieved')
    channel = models.CharField(max_length=30, choices=CHANNEL_CHOICES, default='in_app')
    is_read = models.BooleanField(default=False)
    sent_status = models.CharField(max_length=30, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] {self.title} -> ({self.user.username})"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_prefs'
    )
    enable_sms = models.BooleanField(default=True)
    enable_whatsapp = models.BooleanField(default=True)
    enable_email = models.BooleanField(default=True)
    enable_in_app = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"NotifPrefs for {self.user.username}"


# ==========================================
# PHASE 11: AI LEARNING MEMORY, ADAPTIVE CURRICULUM & BRAIN MODELS
# ==========================================
class LearningProfile(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_profile'
    )
    reading_level = models.CharField(max_length=30, default='Beginner')
    speaking_level = models.CharField(max_length=30, default='Intermediate')
    preferred_learning_style = models.CharField(max_length=50, default='Visual Learner')
    preferred_teaching_style = models.CharField(max_length=50, default='Socratic & Encouraging')
    weak_concepts_json = models.TextField(default='["Fractions", "Past Tense"]')
    strong_concepts_json = models.TextField(default='["Addition", "Vocabulary"]')
    common_mistakes_json = models.TextField(default='[]')
    avg_study_duration_mins = models.FloatField(default=45.0)
    confidence_score = models.FloatField(default=85.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LearningProfile for {self.student.username} ({self.preferred_learning_style})"


class SkillNode(models.Model):
    subject = models.CharField(max_length=50, default='Math')
    name = models.CharField(max_length=100)
    parent_node = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children'
    )
    order = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.subject}] {self.name}"


class SkillProgress(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'Not Started ⚪'),
        ('learning', 'Learning 🟡'),
        ('practicing', 'Practicing 🔵'),
        ('mastered', 'Mastered 🟢'),
        ('revision_needed', 'Revision Needed 🔴'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_progresses'
    )
    skill_node = models.ForeignKey(
        SkillNode,
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='not_started')
    mastery_percentage = models.FloatField(default=0.0)
    last_practiced = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'skill_node')

    def __str__(self):
        return f"{self.student.username} -> {self.skill_node.name} [{self.status}] ({self.mastery_percentage:.0f}%)"


class KnowledgeGraph(models.Model):
    subject = models.CharField(max_length=50, default='Math')
    tree_json = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KnowledgeGraph ({self.subject})"


class Recommendation(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student Action'),
        ('parent', 'Parent Tip'),
        ('teacher', 'Teacher Insight'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations'
    )
    target_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    action_text = models.TextField()
    category = models.CharField(max_length=50, default='Practice')
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.target_role}] {self.action_text[:40]}..."


class RevisionSchedule(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revision_schedules'
    )
    topic = models.CharField(max_length=200)
    interval_days = models.IntegerField(default=1)
    scheduled_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"Revision: {self.topic} for {self.student.username} on {self.scheduled_date}"


class LearningGoal(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_goals'
    )
    title = models.CharField(max_length=200)
    target_date = models.DateField()
    progress_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Goal: {self.title} ({self.progress_percentage:.0f}%)"


class LearningInsight(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_insight'
    )
    strength_summary = models.TextField()
    weakness_summary = models.TextField()
    predicted_milestone = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight for {self.student.username}"


class AdaptivePlan(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adaptive_plans'
    )
    curriculum_json = models.TextField(default='[]')
    difficulty_level = models.CharField(max_length=30, default='Adaptive')
    created_at = models.DateTimeField(auto_now_add=True)


class StudyPattern(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_pattern'
    )
    best_study_hour = models.IntegerField(default=16)
    most_active_day = models.CharField(max_length=20, default='Wednesday')


# ==========================================
# PHASE 13: AI CONFIGURATION & PROMPT MANAGEMENT MODELS
# ==========================================
class AIConfiguration(models.Model):
    provider = models.CharField(max_length=50, default='Gemini')
    model_name = models.CharField(max_length=100, default='gemini-1.5-flash')
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.95)
    top_k = models.IntegerField(default=40)
    max_tokens = models.IntegerField(default=2048)
    streaming = models.BooleanField(default=False)
    retry_attempts = models.IntegerField(default=3)
    timeout_seconds = models.IntegerField(default=30)
    response_language = models.CharField(max_length=20, default='en-US')
    default_student_tone = models.CharField(max_length=50, default='Friendly')
    safety_level = models.CharField(max_length=30, default='Balanced')
    daily_request_limit = models.IntegerField(default=1000)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AIConfig ({self.provider}:{self.model_name}, temp={self.temperature})"


class PromptCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PromptTemplate(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived'),
    )

    category = models.ForeignKey(PromptCategory, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Published')
    current_version_number = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.category.name}] {self.name} (v{self.current_version_number})"


class PromptVersion(models.Model):
    template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(default=1)
    prompt_body = models.TextField()
    change_log = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('template', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class PromptTest(models.Model):
    template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, related_name='tests')
    test_input = models.TextField()
    test_output = models.TextField()
    response_time_ms = models.IntegerField(default=0)
    tested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tested_at = models.DateTimeField(auto_now_add=True)


class ConfigurationHistory(models.Model):
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class ModelConfiguration(models.Model):
    provider = models.CharField(max_length=50, default='Gemini')
    model_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.provider} - {self.model_name}"


# ==========================================
# PHASE 14: BACKUP, RESTORE & DISASTER RECOVERY MODELS
# ==========================================
class BackupConfiguration(models.Model):
    storage_provider = models.CharField(max_length=50, default='Local')
    retention_days = models.IntegerField(default=30)
    compression_type = models.CharField(max_length=20, default='gzip')
    schedule_type = models.CharField(max_length=20, default='Daily')
    last_backup_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"BackupConfig ({self.storage_provider}, retention={self.retention_days}d)"


class BackupJob(models.Model):
    JOB_TYPES = (
        ('Full', 'Full System Backup'),
        ('Database', 'Database Dump Only'),
        ('Media', 'Media Files Only'),
        ('Prompts', 'AI Prompts Only'),
        ('Profiles', 'Student Profiles Only'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='Full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"BackupJob #{self.id} [{self.job_type}] - {self.status}"


class BackupFile(models.Model):
    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='files')
    component_type = models.CharField(max_length=50, default='Full')
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.component_type} Backup ({self.file_size_bytes} bytes)"


class BackupHistory(models.Model):
    action = models.CharField(max_length=50)
    backup_file_name = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class RestoreJob(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Restoring', 'Restoring'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    backup_file = models.ForeignKey(BackupFile, on_delete=models.CASCADE, related_name='restore_jobs')
    component_type = models.CharField(max_length=50, default='Full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    safety_backup_path = models.CharField(max_length=500, blank=True)
    restored_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"RestoreJob #{self.id} -> {self.status}"


class RestoreHistory(models.Model):
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


# ==========================================
# PHASE 15: AI USAGE ANALYTICS & PERFORMANCE INTELLIGENCE MODELS
# ==========================================
class AIUsageLog(models.Model):
    module_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, default='gemini-1.5-flash')
    tokens_used = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(default=0)
    status_code = models.IntegerField(default=200)
    is_success = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"AIUsageLog [{self.module_name}] {self.response_time_ms}ms"


class PerformanceMetric(models.Model):
    average_response_time_ms = models.FloatField(default=0.0)
    median_response_time_ms = models.FloatField(default=0.0)
    p95_response_time_ms = models.FloatField(default=0.0)
    failed_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    error_rate_percent = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class SystemMetric(models.Model):
    cpu_percent = models.FloatField(default=0.0)
    memory_percent = models.FloatField(default=0.0)
    disk_percent = models.FloatField(default=0.0)
    database_healthy = models.BooleanField(default=True)
    redis_healthy = models.BooleanField(default=True)
    celery_healthy = models.BooleanField(default=True)
    active_connections = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class FeatureUsage(models.Model):
    feature_name = models.CharField(max_length=100, unique=True)
    total_usage_count = models.IntegerField(default=0)
    unique_users_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.feature_name}: {self.total_usage_count} uses"


class UsageReport(models.Model):
    REPORT_TYPES = (
        ('CSV', 'CSV Export'),
        ('JSON', 'JSON Export'),
    )
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES, default='CSV')
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(default=0)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} Report ({self.file_size_bytes} bytes)"



