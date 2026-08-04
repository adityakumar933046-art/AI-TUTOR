import os
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutor.models import (
    ChatSession, ChatMessage, VoiceSession,
    VoiceTranscript, VoiceSettings, AudioMetadata,
    Whiteboard, WhiteboardElement, DrawingHistory,
    MathSession, MathSolution, AutoSaveSnapshot,
    VisualLesson, LessonDiagram, AnimationAsset,
    LessonHistory, BookmarkedLesson,
    Homework, HomeworkFile, OCRResult, DetectedQuestion,
    HomeworkAnalysis, PracticeQuestion,
    ReadingPassage, ReadingSession, ReadingRecording,
    PronunciationScore, WordAssessment, ReadingProgress, ReadingRecommendation,
    ConversationScenario, SpeakingSession, ConversationHistory, SpeakingFeedback,
    GrammarCorrection, VocabularyProgress, SpeakingChallenge, SpeakingAchievement,
    Game, GameSession, GameQuestion, GameResult, Mission, StudentReward, LeaderboardEntry,
    ParentChildRelation, DailyStudyPlan, DailyProgress, AnalyticsSnapshot, Notification, NotificationPreference,
    LearningProfile, SkillNode, SkillProgress, KnowledgeGraph, Recommendation, RevisionSchedule, LearningGoal, LearningInsight, AdaptivePlan, StudyPattern,
    AIConfiguration, PromptCategory, PromptTemplate, PromptVersion, PromptTest, ConfigurationHistory
)
from tutor.services.gemini_service import GeminiTutorService
from tutor.services.voice_service import VoiceTutorService
from tutor.services.whiteboard_service import WhiteboardService
from tutor.services.math_service import MathSolverService
from tutor.services.visual_learning_service import VisualLearningEngine
from tutor.services.lesson_service import LessonManagerService
from tutor.services.ocr_service import OCRVisionService
from tutor.services.document_service import DocumentParserService
from tutor.services.homework_service import HomeworkManagerService
from tutor.services.practice_generator import PracticeGeneratorService
from tutor.services.reading_service import ReadingPassageService
from tutor.services.speech_analysis_service import SpeechAlignmentService
from tutor.services.pronunciation_service import PronunciationScoringService
from tutor.services.fluency_service import FluencyAnalysisService
from tutor.services.conversation_service import RoleplayScenarioService
from tutor.services.speaking_service import SpeakingCoachEngine
from tutor.services.grammar_service import GrammarAnalysisService
from tutor.services.vocabulary_service import VocabularyBuilderService
from tutor.services.feedback_service import SpeakingFeedbackEngine
from tutor.services.game_engine import GameEngineService
from tutor.services.reward_service import RewardService
from tutor.services.mission_service import MissionService
from tutor.services.leaderboard_service import LeaderboardService
from tutor.services.analytics_service import StudentAnalyticsEngine
from tutor.services.notification_service import NotificationEngine
from tutor.services.sms_service import SMSProviderAbstraction
from tutor.services.whatsapp_service import WhatsAppReportService
from tutor.services.email_service import EmailDigestService
from tutor.services.study_plan_service import StudyPlanGeneratorService
from tutor.services.report_service import DailyReportService
from tutor.services.learning_memory_service import LearningMemoryService
from tutor.services.knowledge_graph_service import KnowledgeGraphService
from tutor.services.adaptive_curriculum_service import AdaptiveCurriculumEngine
from tutor.services.recommendation_service import AIRecommendationService
from tutor.services.revision_service import SpacedRevisionService
from tutor.services.learning_profile_service import LearningProfileAnalyticsService
from tutor.services.system_monitor_service import SystemMonitorService
from tutor.services.global_search_service import GlobalSearchEngine
from tutor.services.configuration_service import ConfigurationService
from tutor.services.prompt_service import PromptService
from tutor.services.model_router import ModelRouter
from tutor.services.storage_service import StorageService
from tutor.services.backup_service import BackupService
from tutor.services.restore_service import RestoreService
from tutor.services.analytics_logging_service import AnalyticsLoggingService
from tutor.services.performance_monitor_service import PerformanceMonitorService
from tutor.services.report_exporter_service import ReportExporterService
from tutor.services.cache_management_service import CacheManagementService
from tutor.services.system_diagnostics_service import SystemDiagnosticsService
from tutor.services.maintenance_mode_service import MaintenanceModeService

User = get_user_model()

class Phase2TutorSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_a = User.objects.create_user(
            username='student_a',
            email='student_a@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.student_b = User.objects.create_user(
            username='student_b',
            email='student_b@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )

        self.session_a = ChatSession.objects.create(
            student=self.student_a,
            subject='Math',
            title='Algebra Fundamentals'
        )

    def test_chatsession_model_creation(self):
        self.assertEqual(self.session_a.subject, 'Math')
        self.assertEqual(self.session_a.student, self.student_a)
        self.assertTrue(str(self.session_a).startswith('[Math]'))

    def test_gemini_service_prompt_initialization(self):
        service = GeminiTutorService(subject='Science')
        self.assertIn('Subject Focus:', service.system_instruction)
        self.assertIn('real-world phenomena', service.system_instruction)

    def test_student_dashboard_access(self):
        self.client.force_login(self.student_a)
        response = self.client.get(reverse('student_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mathematics')
        self.assertContains(response, 'Algebra Fundamentals')

    def test_create_new_chat_session(self):
        self.client.force_login(self.student_a)
        response = self.client.get(reverse('chat_create'), {'subject': 'Coding'})
        self.assertEqual(response.status_code, 302)
        new_session = ChatSession.objects.filter(student=self.student_a, subject='Coding').first()
        self.assertIsNotNone(new_session)

    def test_chat_send_message_api(self):
        self.client.force_login(self.student_a)
        response = self.client.post(
            reverse('chat_send_api', kwargs={'session_id': self.session_a.id}),
            data='{"message": "How do I solve linear equations?"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertTrue(ChatMessage.objects.filter(session=self.session_a, role='user').exists())
        self.assertTrue(ChatMessage.objects.filter(session=self.session_a, role='model').exists())

    def test_student_session_ownership_security(self):
        self.client.force_login(self.student_b)
        response = self.client.post(
            reverse('chat_send_api', kwargs={'session_id': self.session_a.id}),
            data='{"message": "Unauthorized message"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_rename_and_delete_session(self):
        self.client.force_login(self.student_a)
        response_rename = self.client.post(
            reverse('chat_rename_api', kwargs={'session_id': self.session_a.id}),
            data='{"title": "Advanced Linear Algebra"}',
            content_type='application/json'
        )
        self.assertEqual(response_rename.status_code, 200)
        self.session_a.refresh_from_db()
        self.assertEqual(self.session_a.title, 'Advanced Linear Algebra')

        response_delete = self.client.post(
            reverse('chat_delete_api', kwargs={'session_id': self.session_a.id})
        )
        self.assertEqual(response_delete.status_code, 200)
        self.assertFalse(ChatSession.objects.filter(id=self.session_a.id).exists())


class Phase3VoiceTutorSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='voice_kid',
            email='voice_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.chat_session = ChatSession.objects.create(
            student=self.student,
            subject='Science',
            title='Voice Science Session'
        )

    def test_voice_models_creation(self):
        v_settings, _ = VoiceSettings.objects.get_or_create(student=self.student, language='en-US')
        v_service = VoiceTutorService(self.student, self.chat_session)
        v_session = v_service.get_or_create_active_voice_session(mode='push_to_talk')

        v_transcript = VoiceTranscript.objects.create(
            voice_session=v_session,
            speaker='student',
            transcript_text='Why is the sky blue?',
            language='en-US'
        )
        audio_meta = AudioMetadata.objects.create(
            transcript=v_transcript,
            duration_ms=2500
        )

        self.assertEqual(v_settings.language, 'en-US')
        self.assertEqual(v_session.mode, 'push_to_talk')
        self.assertEqual(v_transcript.speaker, 'student')
        self.assertEqual(audio_meta.duration_ms, 2500)

    def test_voice_tutor_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('voice_tutor_session', kwargs={'session_id': self.chat_session.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voice AI Tutor')
        self.assertContains(response, 'Science Focus')

    def test_voice_send_api_turn_processing(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('voice_send_api', kwargs={'session_id': self.chat_session.id}),
            data='{"spoken_text": "What are photosynthesis and chlorophyll?", "language": "en-US", "mode": "push_to_talk"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['student_text'], 'What are photosynthesis and chlorophyll?')
        self.assertTrue(VoiceTranscript.objects.filter(speaker='student').exists())
        self.assertTrue(VoiceTranscript.objects.filter(speaker='ai_tutor').exists())
        self.assertTrue(ChatMessage.objects.filter(session=self.chat_session, role='user').exists())
        self.assertTrue(ChatMessage.objects.filter(session=self.chat_session, role='model').exists())

    def test_voice_settings_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('voice_settings_api'),
            data='{"language": "hi-IN", "voice_gender": "Female", "speaking_rate": 1.25, "pitch": 1.1, "auto_listen": true}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        v_settings = VoiceSettings.objects.get(student=self.student)
        self.assertEqual(v_settings.language, 'hi-IN')
        self.assertEqual(v_settings.speaking_rate, 1.25)


class Phase4WhiteboardSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='math_kid',
            email='math_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.chat_session = ChatSession.objects.create(
            student=self.student,
            subject='Math',
            title='Math Board Session'
        )
        self.whiteboard = Whiteboard.objects.create(
            student=self.student,
            chat_session=self.chat_session,
            title='Math Practice Board',
            mode='Math Practice',
            canvas_json='{"objects":[]}'
        )

    def test_whiteboard_models_creation(self):
        elem = WhiteboardElement.objects.create(
            whiteboard=self.whiteboard,
            element_type='shape',
            element_data='{"type":"rect"}'
        )
        dh = DrawingHistory.objects.create(
            whiteboard=self.whiteboard,
            snapshot_json='{"objects":[]}',
            action_type='draw'
        )
        self.assertEqual(self.whiteboard.mode, 'Math Practice')
        self.assertEqual(elem.element_type, 'shape')
        self.assertEqual(dh.action_type, 'draw')

    def test_whiteboard_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('whiteboard_session', kwargs={'board_id': self.whiteboard.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Math Practice Board')
        self.assertContains(response, 'Sparky AI Math Solver')

    def test_whiteboard_save_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('whiteboard_save_api', kwargs={'board_id': self.whiteboard.id}),
            data='{"canvas_json": "{\\"objects\\":[{\\"type\\":\\"circle\\"}]}", "is_auto_save": true}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(AutoSaveSnapshot.objects.filter(whiteboard=self.whiteboard).exists())

    def test_math_solve_and_hint_api(self):
        self.client.force_login(self.student)
        solve_response = self.client.post(
            reverse('math_solve_api', kwargs={'board_id': self.whiteboard.id}),
            data='{"expression": "27 * 13"}',
            content_type='application/json'
        )
        self.assertEqual(solve_response.status_code, 200)
        data = solve_response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['expression'], '27 * 13')
        self.assertTrue(MathSession.objects.filter(whiteboard=self.whiteboard).exists())
        self.assertTrue(MathSolution.objects.exists())

        self.assertTrue(ChatMessage.objects.filter(session=self.chat_session, role='user').exists())
        self.assertTrue(ChatMessage.objects.filter(session=self.chat_session, role='model').exists())

        hint_response = self.client.post(
            reverse('math_hint_api', kwargs={'board_id': self.whiteboard.id}),
            data='{"expression": "27 * 13"}',
            content_type='application/json'
        )
        self.assertEqual(hint_response.status_code, 200)
        self.assertTrue(hint_response.json()['success'])


class Phase5VisualLearningSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='visual_kid',
            email='visual_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.chat_session = ChatSession.objects.create(
            student=self.student,
            subject='Science',
            title='Visual Science Session'
        )
        self.lesson = VisualLesson.objects.create(
            student=self.student,
            chat_session=self.chat_session,
            topic='Photosynthesis',
            subject='Science',
            visualization_type='Flowchart',
            explanation_text='Photosynthesis is how plants make food using sunlight!',
            analogy_text='Think of a leaf like a tiny solar-powered kitchen.',
            diagram_data='graph TD\n A[Sunlight] --> B[Leaf]',
            quiz_data='[{"question":"What do leaves need?","options":["Sunlight","Ice","Pizza","Rocks"],"correct_index":0,"explanation":"Sunlight!"}]',
            summary_text='Leaves use sunlight to make food.'
        )

    def test_visual_models_creation(self):
        diagram = LessonDiagram.objects.create(
            lesson=self.lesson,
            diagram_type='flowchart',
            code_definition='graph TD'
        )
        history = LessonHistory.objects.create(
            student=self.student,
            lesson=self.lesson
        )
        self.assertEqual(self.lesson.topic, 'Photosynthesis')
        self.assertEqual(diagram.diagram_type, 'flowchart')
        self.assertEqual(history.lesson, self.lesson)

    def test_visual_learning_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('visual_lesson_view', kwargs={'lesson_id': self.lesson.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Photosynthesis')
        self.assertContains(response, 'AI Visual Learning Engine')

    def test_visual_generate_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('visual_generate_api'),
            data='{"topic": "Water Cycle", "subject": "Science"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['topic'], 'Water Cycle')

    def test_visual_bookmark_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('visual_bookmark_api', kwargs={'lesson_id': self.lesson.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_bookmarked'])


class Phase6HomeworkScannerSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='hw_kid',
            email='hw_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.chat_session = ChatSession.objects.create(
            student=self.student,
            subject='Math',
            title='Homework Discussion'
        )
        self.homework = Homework.objects.create(
            student=self.student,
            chat_session=self.chat_session,
            title='Algebra Worksheet 1',
            subject='Math',
            difficulty_level='Medium',
            status='analyzed'
        )
        self.question = DetectedQuestion.objects.create(
            homework=self.homework,
            question_number=1,
            question_text='Solve for x: 3x + 5 = 20',
            subject_tag='Math',
            difficulty='Medium',
            step_by_step_solution='1. Subtract 5: 3x = 15\n2. Divide by 3: x = 5',
            hint_text='Subtract 5 from both sides first.'
        )

    def test_homework_models_creation(self):
        ocr = OCRResult.objects.create(
            homework=self.homework,
            extracted_text='Solve 3x + 5 = 20',
            cleaned_text='Solve 3x + 5 = 20',
            confidence_score=0.98
        )
        pq = PracticeQuestion.objects.create(
            question=self.question,
            difficulty='Easy',
            question_text='Solve 2x + 4 = 10',
            options_json='["x=3", "x=5", "x=2", "x=4"]',
            correct_index=0,
            explanation='Subtract 4 then divide by 2.'
        )

        self.assertEqual(self.homework.title, 'Algebra Worksheet 1')
        self.assertEqual(ocr.confidence_score, 0.98)
        self.assertEqual(pq.difficulty, 'Easy')

    def test_homework_scanner_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('homework_detail_view', kwargs={'hw_id': self.homework.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algebra Worksheet 1')
        self.assertContains(response, 'Solve for x: 3x + 5 = 20')

    def test_homework_upload_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('homework_upload_api'),
            data={'raw_text': 'Solve for y: 4y - 8 = 16'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Homework.objects.filter(student=self.student).count() >= 2)
        self.assertTrue(ChatMessage.objects.filter(session__student=self.student, role='user').exists())

    def test_homework_practice_api(self):
        self.client.force_login(self.student)
        PracticeQuestion.objects.create(
            question=self.question,
            difficulty='Easy',
            question_text='Solve 2x + 4 = 10',
            options_json='["x=3", "x=5", "x=2", "x=4"]',
            correct_index=0,
            explanation='Subtract 4 then divide by 2.'
        )
        response = self.client.get(
            reverse('homework_practice_api', kwargs={'question_id': self.question.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['practice_set']), 1)


class Phase7ReadingCoachSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='reader_kid',
            email='reader_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        chat_session = ChatSession.objects.create(student=self.student, subject='English', title='Reading Session')
        ReadingPassageService.seed_default_passages()
        self.passage = ReadingPassage.objects.first()
        self.session = ReadingPassageService.start_reading_session(self.student, self.passage.id)
        self.session.chat_session = chat_session
        self.session.save()

    def test_reading_models_creation(self):
        recording = ReadingRecording.objects.create(
            session=self.session,
            duration_seconds=12.5,
            spoken_transcript=self.passage.content_text,
            words_per_minute=85.0
        )
        score = PronunciationScore.objects.create(
            session=self.session,
            accuracy_score=95.0,
            fluency_score=90.0,
            pacing_score=85.0,
            overall_score=92.5,
            gemini_feedback='Fantastic reading performance!'
        )
        word_ast = WordAssessment.objects.create(
            score=score,
            target_word='little',
            spoken_word='little',
            status='correct'
        )

        self.assertEqual(self.passage.title, 'The Little Red Fox')
        self.assertEqual(recording.duration_seconds, 12.5)
        self.assertEqual(score.accuracy_score, 95.0)
        self.assertEqual(word_ast.status, 'correct')

    def test_speech_alignment_service(self):
        alignment = SpeechAlignmentService.align_transcript_with_target(
            target_text="the little red fox ran",
            spoken_transcript="the little red fox"
        )
        self.assertEqual(alignment['correct_count'], 4)
        self.assertEqual(alignment['skipped_count'], 1)
        self.assertTrue(alignment['accuracy_percentage'] > 75.0)

    def test_reading_coach_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('reading_coach_session', kwargs={'session_id': self.session.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Little Red Fox')
        self.assertContains(response, 'Reading Score Dashboard')

    def test_reading_submit_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('reading_submit_api', kwargs={'session_id': self.session.id}),
            data=f'{{"spoken_transcript": "{self.passage.content_text}", "duration_seconds": 15.0}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['accuracy_score'] > 90.0)
        self.assertTrue(PronunciationScore.objects.filter(session=self.session).exists())
        self.assertTrue(ReadingProgress.objects.filter(student=self.student).exists())
        self.assertTrue(ChatMessage.objects.filter(session__student=self.student, role='user').exists())


class Phase8SpeakingCoachSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='speaker_kid',
            email='speaker_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        RoleplayScenarioService.seed_default_scenarios()
        self.scenario = ConversationScenario.objects.first()
        self.chat_session = ChatSession.objects.create(
            student=self.student,
            subject='English',
            title='Speaking Coach'
        )
        self.session = SpeakingSession.objects.create(
            student=self.student,
            scenario=self.scenario,
            chat_session=self.chat_session
        )

    def test_speaking_models_creation(self):
        turn = ConversationHistory.objects.create(
            session=self.session,
            speaker='student',
            text_content='Hello teacher, I love science!'
        )
        feedback = SpeakingFeedback.objects.create(
            session=self.session,
            grammar_score=90.0,
            vocabulary_score=85.0,
            fluency_score=88.0,
            confidence_score=92.0,
            overall_speaking_score=89.0,
            summary_report='Great speaking confidence!'
        )
        corr = GrammarCorrection.objects.create(
            feedback=feedback,
            original_sentence='i goes to school',
            corrected_sentence='I go to school',
            explanation_rule='Subject-verb agreement rule.'
        )

        self.assertEqual(self.scenario.title, 'Classroom Teacher & Student')
        self.assertEqual(turn.speaker, 'student')
        self.assertEqual(feedback.overall_speaking_score, 89.0)
        self.assertEqual(corr.corrected_sentence, 'I go to school')

    def test_speaking_coach_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('speaking_coach_session', kwargs={'session_id': self.session.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classroom Teacher')
        self.assertContains(response, 'Roleplay Scenarios')

    def test_speaking_respond_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('speaking_respond_api', kwargs={'session_id': self.session.id}),
            data='{"spoken_text": "I really enjoy learning about space and planets!"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(ConversationHistory.objects.filter(session=self.session, speaker='student').exists())
        self.assertTrue(ConversationHistory.objects.filter(session=self.session, speaker='ai_coach').exists())
        self.assertTrue(ChatMessage.objects.filter(session=self.chat_session, role='user').exists())

    def test_speaking_feedback_api(self):
        self.client.force_login(self.student)
        ConversationHistory.objects.create(
            session=self.session,
            speaker='student',
            text_content='i goes to the big park'
        )
        response = self.client.post(
            reverse('speaking_feedback_api', kwargs={'session_id': self.session.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['overall_score'] > 0)
        self.assertTrue(SpeakingFeedback.objects.filter(session=self.session).exists())
        self.assertEqual(self.session.refresh_from_db() or self.session.status, 'completed')


class Phase9GameEngineSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='gamer_kid',
            email='gamer_kid@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        self.game = GameEngineService.generate_ai_game(
            student=self.student,
            subject='Math',
            topic='Fractions',
            game_type='match_pair',
            difficulty='Easy'
        )

    def test_game_models_creation(self):
        sess = GameSession.objects.create(
            game=self.game,
            student=self.student,
            score=80,
            max_score=100
        )
        res = GameResult.objects.create(
            session=sess,
            xp_earned=120,
            coins_earned=64,
            stars_earned=3,
            accuracy_percentage=80.0,
            feedback_text='Great game performance!'
        )
        rew_prof = RewardService.get_or_create_profile(self.student)
        mission = Mission.objects.create(
            student=self.student,
            title='Daily Game Challenge',
            description='Play 1 game',
            xp_reward=50,
            coins_reward=25
        )

        self.assertEqual(self.game.subject, 'Math')
        self.assertEqual(sess.score, 80)
        self.assertEqual(res.xp_earned, 120)
        self.assertEqual(rew_prof.coins_balance, 100)
        self.assertEqual(mission.xp_reward, 50)

    def test_game_center_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('game_detail_view', kwargs={'game_id': self.game.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Game Center')
        self.assertContains(response, 'Fractions')

    def test_game_generate_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('game_generate_api'),
            data='{"subject": "Science", "topic": "Solar System", "game_type": "memory_cards", "difficulty": "Medium"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Game.objects.filter(student=self.student, subject='Science').exists())

    def test_game_submit_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('game_submit_api', kwargs={'game_id': self.game.id}),
            data='{"score": 90, "max_score": 100}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['result']['accuracy'], 90.0)
        self.assertTrue(GameSession.objects.filter(game=self.game).exists())

    def test_game_store_buy_api(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('game_store_buy_api'),
            data='{"item_id": "fox_pet", "item_cost": 50}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['coins_balance'], 50)


class Phase10ParentAnalyticsSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username='parent_user',
            email='parent@eduverse.ai',
            password='Password123!',
            role='Parent',
            email_verified=True,
            is_profile_complete=True
        )
        self.student = User.objects.create_user(
            username='child_student',
            email='child@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )
        ParentChildRelation.objects.create(parent=self.parent, child=self.student)

    def test_phase10_models_creation(self):
        plan = StudyPlanGeneratorService.generate_daily_plan(self.student)
        prog = DailyProgress.objects.create(student=self.student, study_time_minutes=45)
        analytics = StudentAnalyticsEngine.compute_student_analytics(self.student)
        notif_res = NotificationEngine.send_notification(self.parent, "Goal Achieved", "Alex reached 85% today!")

        self.assertIsNotNone(plan)
        self.assertEqual(prog.study_time_minutes, 45)
        self.assertTrue(analytics['learning_speed'] >= 70.0)
        self.assertTrue(notif_res['success'])

    def test_parent_dashboard_view_access(self):
        self.client.force_login(self.parent)
        response = self.client.get(reverse('parent_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Parent Hub')
        self.assertContains(response, 'child_student')

    def test_analytics_center_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('analytics_center'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Analytics Center')

    def test_notification_prefs_api(self):
        self.client.force_login(self.parent)
        response = self.client.post(
            reverse('notification_prefs_api'),
            data='{"enable_sms": true, "enable_whatsapp": true, "phone_number": "+1234567890"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])


class Phase11LearningBrainSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='brainy_kid',
            email='brainy@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )

    def test_learning_brain_models(self):
        profile = LearningMemoryService.get_or_create_profile(self.student)
        skills = KnowledgeGraphService.seed_and_get_student_skills(self.student)
        plan = AdaptiveCurriculumEngine.generate_adaptive_plan(self.student)
        recs = AIRecommendationService.get_or_seed_recommendations(self.student)
        revs = SpacedRevisionService.get_due_revisions(self.student)
        insights = LearningProfileAnalyticsService.get_learning_insights(self.student)

        self.assertEqual(profile.preferred_learning_style, 'Visual Learner')
        self.assertTrue(skills.count() > 0)
        self.assertIsNotNone(plan)
        self.assertTrue(recs.count() > 0)
        self.assertTrue(revs.count() > 0)
        self.assertTrue(insights['confidence_score'] >= 50.0)

    def test_learning_memory_impact_recording(self):
        updated_profile = LearningMemoryService.record_activity_impact(
            student=self.student,
            subject='Math',
            topic='Fractions',
            score_pct=95.0
        )
        self.assertTrue(updated_profile.confidence_score > 80.0)

    def test_learning_brain_view_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('learning_brain'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Personal AI Learning Brain')
        self.assertContains(response, 'Skill Tree Graph')


class Phase12AdminAndSystemInfrastructureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_boss',
            email='admin@eduverse.ai',
            password='Password123!',
            role='Admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_profile_complete=True
        )
        self.student = User.objects.create_user(
            username='target_student',
            email='target@eduverse.ai',
            password='Password123!',
            role='Student',
            email_verified=True,
            is_profile_complete=True
        )

    def test_system_monitor_service(self):
        metrics = SystemMonitorService.get_system_metrics()
        self.assertTrue(metrics['total_students'] >= 1)
        self.assertEqual(metrics['database_status'], 'Healthy')
        self.assertEqual(metrics['gemini_api_status'], 'Operational')

    def test_admin_hub_view_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Production Admin Dashboard')
        self.assertContains(response, 'User Management')

    def test_admin_user_action_api(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('admin_user_action_api', kwargs={'user_id': self.student.id}),
            data='{"action": "toggle_active"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_active'])

    def test_global_search_engine(self):
        res = GlobalSearchEngine.search_all('target')
        self.assertTrue(len(res['students']) >= 1)
        self.assertEqual(res['students'][0].username, 'target_student')

    def test_health_check_view(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'ok')


class Phase13AIConfigAndPromptStudioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='ai_admin',
            email='ai_admin@eduverse.ai',
            password='Password123!',
            role='Admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_profile_complete=True
        )
        PromptService.seed_default_prompts()

    def test_configuration_service_and_cache(self):
        config = ConfigurationService.get_active_config()
        self.assertEqual(config.provider, 'Gemini')

        updated = ConfigurationService.update_config(self.admin, temperature=0.85)
        self.assertEqual(updated.temperature, 0.85)
        self.assertTrue(ConfigurationHistory.objects.filter(field_name='temperature').exists())

    def test_prompt_versioning_and_rollback(self):
        prompt_text = ModelRouter.get_dynamic_prompt('AI Chat')
        self.assertIn('Sparky', prompt_text)

        template = PromptTemplate.objects.get(name='default_chat_prompt')
        v2 = PromptService.create_new_version(template, "New Prompt V2 Body", change_log="V2 test", user=self.admin)
        self.assertEqual(v2.version_number, 2)
        self.assertEqual(ModelRouter.get_dynamic_prompt('AI Chat'), "New Prompt V2 Body")

        v3 = PromptService.rollback_to_version(template, 1, user=self.admin)
        self.assertEqual(v3.version_number, 3)
        self.assertIn('Sparky', ModelRouter.get_dynamic_prompt('AI Chat'))

    def test_ai_config_center_view_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('ai_config_center'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Configuration Center')
        self.assertContains(response, 'Prompt Template Studio')

    def test_prompt_update_api(self):
        self.client.force_login(self.admin)
        template = PromptTemplate.objects.first()
        response = self.client.post(
            reverse('prompt_update_api', kwargs={'template_id': template.id}),
            data='{"prompt_body": "Updated test prompt", "change_log": "Test edit"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['version_number'], 2)


class Phase14BackupAndRestoreSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='sys_admin',
            email='sys_admin@eduverse.ai',
            password='Password123!',
            role='Admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_profile_complete=True
        )

    def test_backup_service_creation_and_checksum(self):
        bfile = BackupService.create_backup(job_type='Full', user=self.admin)
        self.assertIsNotNone(bfile)
        self.assertTrue(os.path.exists(bfile.file_path))
        self.assertTrue(len(bfile.checksum_sha256) == 64)
        self.assertTrue(StorageService.verify_file_integrity(bfile.file_path, bfile.checksum_sha256))

    def test_restore_service_execution(self):
        bfile = BackupService.create_backup(job_type='Database', user=self.admin)
        rjob = RestoreService.restore_backup(bfile, user=self.admin)
        self.assertEqual(rjob.status, 'Completed')
        self.assertTrue(os.path.exists(rjob.safety_backup_path))

    def test_backup_dashboard_view_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('backup_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backup, Restore & Disaster Recovery Center')
        self.assertContains(response, 'Backup Archive Repository')

    def test_backup_create_api(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('backup_create_api'),
            data='{"job_type": "Database"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])


class Phase15AIAnalyticsAndPerformanceIntelligenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='analytics_admin',
            email='analytics_admin@eduverse.ai',
            password='Password123!',
            role='Admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_profile_complete=True
        )

    def test_analytics_logging_service(self):
        AnalyticsLoggingService.log_ai_request('AI Chat', response_time_ms=250, user=self.admin)
        AnalyticsLoggingService.log_ai_request('Voice Tutor', response_time_ms=450, user=self.admin)

        perf = PerformanceMonitorService.compute_performance_metrics()
        self.assertEqual(perf['total_requests'], 2)
        self.assertTrue(perf['avg_latency_ms'] > 0.0)

    def test_report_exporter_service(self):
        report = ReportExporterService.export_report('CSV', user=self.admin)
        self.assertIsNotNone(report)
        self.assertTrue(os.path.exists(report.file_path))

    def test_ai_analytics_dashboard_view_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('ai_analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Usage Analytics & Performance Intelligence')
        self.assertContains(response, 'Average Latency')

    def test_analytics_export_api(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('analytics_export_api'), {'format': 'csv'})
        self.assertEqual(response.status_code, 200)


class Phase16EnterpriseSecurityAndDiagnosticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='diag_admin',
            email='diag_admin@eduverse.ai',
            password='Password123!',
            role='Admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_profile_complete=True
        )

    def test_system_diagnostics_service(self):
        diag = SystemDiagnosticsService.run_full_diagnostics()
        self.assertTrue(diag['db_latency_ms'] >= 0.0)
        self.assertEqual(diag['redis_status'], 'Healthy')
        self.assertEqual(diag['overall_health'], 'PASS')

    def test_cache_management_service(self):
        res = CacheManagementService.flush_all_cache()
        self.assertTrue(res)

    def test_maintenance_mode_service(self):
        self.assertFalse(MaintenanceModeService.is_maintenance_mode())
        MaintenanceModeService.set_maintenance_mode(True)
        self.assertTrue(MaintenanceModeService.is_maintenance_mode())
        MaintenanceModeService.set_maintenance_mode(False)

    def test_system_diagnostics_center_view_access(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('system_diagnostics_center'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enterprise Security, Diagnostics & Cache Studio')
        self.assertContains(response, 'DB Query Latency')

    def test_cache_flush_api(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('cache_flush_api'),
            data='{"target": "AI_CONFIG"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])





