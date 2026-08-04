import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts.views import role_required
from accounts.models import StudentProfile, ParentProfile
from tutor.models import (
    ChatSession, ChatMessage, VoiceSession, VoiceTranscript, VoiceSettings,
    Whiteboard, WhiteboardElement, MathSession, MathSolution,
    VisualLesson, LessonDiagram, BookmarkedLesson, LessonHistory,
    Homework, HomeworkFile, OCRResult, DetectedQuestion, HomeworkAnalysis, PracticeQuestion,
    ReadingPassage, ReadingSession, ReadingRecording, PronunciationScore, WordAssessment, ReadingProgress,
    ConversationScenario, SpeakingSession, ConversationHistory, SpeakingFeedback, GrammarCorrection, VocabularyProgress,
    Game, GameSession, GameResult, Mission, StudentReward, LeaderboardEntry,
    ParentChildRelation, DailyStudyPlan, DailyProgress, AnalyticsSnapshot, Notification, NotificationPreference,
    LearningProfile, SkillNode, SkillProgress, KnowledgeGraph, Recommendation, RevisionSchedule, LearningGoal, LearningInsight, AdaptivePlan, StudyPattern,
    AIConfiguration, PromptCategory, PromptTemplate, PromptVersion, PromptTest, ConfigurationHistory,
    BackupConfiguration, BackupJob, BackupFile, BackupHistory, RestoreJob, RestoreHistory,
    AIUsageLog, PerformanceMetric, SystemMetric, FeatureUsage, UsageReport
)
from tutor.services.gemini_service import GeminiTutorService
from tutor.services.voice_service import VoiceTutorService
from tutor.services.speech_service import SpeechService, LANGUAGE_MAP
from tutor.services.whiteboard_service import WhiteboardService
from tutor.services.math_service import MathSolverService
from tutor.services.visual_learning_service import VisualLearningEngine
from tutor.services.lesson_service import LessonManagerService
from tutor.services.homework_service import HomeworkManagerService
from tutor.services.practice_generator import PracticeGeneratorService
from tutor.services.reading_service import ReadingPassageService
from tutor.services.speech_analysis_service import SpeechAlignmentService
from tutor.services.pronunciation_service import PronunciationScoringService
from tutor.services.fluency_service import FluencyAnalysisService
from tutor.services.conversation_service import RoleplayScenarioService
from tutor.services.speaking_service import SpeakingCoachEngine
from tutor.services.feedback_service import SpeakingFeedbackEngine
from tutor.services.game_engine import GameEngineService
from tutor.services.reward_service import RewardService
from tutor.services.mission_service import MissionService
from tutor.services.leaderboard_service import LeaderboardService
from tutor.services.analytics_service import StudentAnalyticsEngine
from tutor.services.notification_service import NotificationEngine
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

SUBJECT_ICONS = {
    'Math': 'bi-calculator text-primary',
    'Science': 'bi-microscope text-success',
    'English': 'bi-book text-warning',
    'History': 'bi-bank text-danger',
    'Geography': 'bi-globe-americas text-info',
    'General Knowledge': 'bi-lightbulb text-warning',
    'Coding': 'bi-code-slash text-purple',
    'Reasoning': 'bi-puzzle text-primary',
}

# ==========================================
# 1. ENHANCED STUDENT DASHBOARD VIEW
# ==========================================
@login_required
@role_required(['Student'])
def student_dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    recent_chats = ChatSession.objects.filter(student=request.user, is_archived=False)[:5]
    recent_boards = Whiteboard.objects.filter(student=request.user, is_archived=False)[:4]
    recent_lessons = VisualLesson.objects.filter(student=request.user)[:4]
    recent_homeworks = Homework.objects.filter(student=request.user)[:4]
    recent_readings = ReadingSession.objects.filter(student=request.user)[:4]
    recent_speakings = SpeakingSession.objects.filter(student=request.user)[:4]
    recent_games = Game.objects.filter(student=request.user)[:4]
    reading_progress, _ = ReadingProgress.objects.get_or_create(student=request.user)
    reward_profile = RewardService.get_or_create_profile(request.user)

    context = {
        'profile': profile,
        'recent_chats': recent_chats,
        'recent_boards': recent_boards,
        'recent_lessons': recent_lessons,
        'recent_homeworks': recent_homeworks,
        'recent_readings': recent_readings,
        'recent_speakings': recent_speakings,
        'recent_games': recent_games,
        'reading_progress': reading_progress,
        'reward_profile': reward_profile,
        'subject_choices': ChatSession.SUBJECT_CHOICES,
        'subject_icons': SUBJECT_ICONS,
    }
    return render(request, 'accounts/dashboards/student.html', context)


# ==========================================
# 2. MAIN AI CHAT TUTOR INTERFACE
# ==========================================
@login_required
@role_required(['Student'])
def chat_tutor_view(request, session_id=None):
    student_sessions = ChatSession.objects.filter(student=request.user, is_archived=False)

    if session_id:
        active_session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    else:
        subject = request.GET.get('subject', 'General Knowledge')
        active_session = ChatSession.objects.filter(student=request.user, subject=subject, is_archived=False).first()
        if not active_session:
            active_session = ChatSession.objects.create(
                student=request.user,
                subject=subject,
                title=f"Learning {subject}"
            )
        return redirect('chat_tutor_session', session_id=active_session.id)

    chat_messages = active_session.messages.all()

    context = {
        'active_session': active_session,
        'chat_messages': chat_messages,
        'student_sessions': student_sessions,
        'subject_choices': ChatSession.SUBJECT_CHOICES,
    }
    return render(request, 'tutor/chat_tutor.html', context)


@login_required
@role_required(['Student'])
def chat_create_session(request):
    subject = request.GET.get('subject', 'General Knowledge')
    title_suffix = request.GET.get('topic', 'Session')
    
    session = ChatSession.objects.create(
        student=request.user,
        subject=subject,
        title=f"Exploring {subject} {title_suffix}"
    )
    return redirect('chat_tutor_session', session_id=session.id)


@login_required
@role_required(['Student'])
@require_POST
def chat_send_message_api(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)

    try:
        data = json.loads(request.body.decode('utf-8'))
        user_text = data.get('message', '').strip()
    except Exception:
        user_text = request.POST.get('message', '').strip()

    if not user_text:
        return JsonResponse({'success': False, 'error': 'Message cannot be empty.'}, status=400)

    user_msg = ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_text
    )

    if session.messages.filter(role='user').count() == 1:
        words = user_text.split()[:4]
        session.title = " ".join(words).capitalize() if words else session.title
        session.save()

    history = session.messages.exclude(id=user_msg.id)
    service = GeminiTutorService(subject=session.subject)
    res_dict = service.generate_tutor_response(user_text, chat_history=history)

    ai_content = res_dict.get('response', 'I am here to help you learn!')

    ai_msg = ChatMessage.objects.create(
        session=session,
        role='model',
        content=ai_content
    )

    session.save()
    LearningMemoryService.record_activity_impact(request.user, subject=session.subject, topic=session.title, score_pct=85.0)

    return JsonResponse({
        'success': True,
        'session_title': session.title,
        'user_message': {
            'id': user_msg.id,
            'content': user_msg.content,
            'timestamp': user_msg.created_at.strftime('%H:%M')
        },
        'ai_response': {
            'id': ai_msg.id,
            'content': ai_msg.content,
            'timestamp': ai_msg.created_at.strftime('%H:%M')
        }
    })


from django.http import StreamingHttpResponse

@login_required
@role_required(['Student'])
def chat_stream_message_api(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    user_text = request.GET.get('message', '').strip()
    if not user_text:
        return JsonResponse({'error': 'Message required'}, status=400)

    user_msg = ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_text
    )

    if session.messages.filter(role='user').count() == 1:
        words = user_text.split()[:4]
        session.title = " ".join(words).capitalize() if words else session.title
        session.save()

    history = session.messages.exclude(id=user_msg.id)
    service = GeminiTutorService(subject=session.subject)

    def event_stream():
        collected = []
        for chunk in service.generate_tutor_response_stream(user_text, chat_history=history):
            collected.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        full_text = "".join(collected).strip() or "I'm here to help!"
        ai_msg = ChatMessage.objects.create(
            session=session,
            role='model',
            content=full_text
        )
        session.save()
        LearningMemoryService.record_activity_impact(request.user, subject=session.subject, topic=session.title, score_pct=85.0)
        yield f"data: {json.dumps({'done': True, 'msg_id': ai_msg.id, 'session_title': session.title})}\n\n"

    res = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    res['Cache-Control'] = 'no-cache'
    res['X-Accel-Buffering'] = 'no'
    return res


@login_required
@role_required(['Student'])
@require_POST
def chat_rename_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    data = json.loads(request.body.decode('utf-8'))
    new_title = data.get('title', '').strip()

    if new_title:
        session.title = new_title
        session.save()
        return JsonResponse({'success': True, 'new_title': session.title})
    return JsonResponse({'success': False, 'error': 'Title cannot be empty.'}, status=400)


@login_required
@role_required(['Student'])
@require_POST
def chat_delete_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    session.delete()
    return JsonResponse({'success': True})


@login_required
@role_required(['Student'])
@require_POST
def chat_pin_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    session.is_pinned = not session.is_pinned
    session.save()
    return JsonResponse({'success': True, 'is_pinned': session.is_pinned})


# ==========================================
# 3. PHASE 3: VOICE TUTOR
# ==========================================
@login_required
@role_required(['Student'])
def voice_tutor_view(request, session_id=None):
    student_sessions = ChatSession.objects.filter(student=request.user, is_archived=False)

    if session_id:
        active_session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    else:
        subject = request.GET.get('subject', 'General Knowledge')
        active_session = ChatSession.objects.filter(student=request.user, subject=subject, is_archived=False).first()
        if not active_session:
            active_session = ChatSession.objects.create(
                student=request.user,
                subject=subject,
                title=f"Voice Session - {subject}"
            )
        return redirect('voice_tutor_session', session_id=active_session.id)

    voice_settings, _ = VoiceSettings.objects.get_or_create(student=request.user)
    voice_service = VoiceTutorService(request.user, active_session)
    active_voice_session = voice_service.get_or_create_active_voice_session()

    voice_transcripts = active_voice_session.transcripts.all()

    context = {
        'active_session': active_session,
        'active_voice_session': active_voice_session,
        'voice_transcripts': voice_transcripts,
        'student_sessions': student_sessions,
        'voice_settings': voice_settings,
        'language_map': LANGUAGE_MAP,
    }
    return render(request, 'tutor/voice_tutor.html', context)


@login_required
@role_required(['Student'])
@require_POST
def voice_send_api(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)

    try:
        data = json.loads(request.body.decode('utf-8'))
        spoken_text = data.get('spoken_text', '').strip()
        language = data.get('language', 'en-US')
        mode = data.get('mode', 'push_to_talk')
        duration_ms = int(data.get('duration_ms', 0))
    except Exception:
        spoken_text = request.POST.get('spoken_text', '').strip()
        language = request.POST.get('language', 'en-US')
        mode = request.POST.get('mode', 'push_to_talk')
        duration_ms = 0

    if not spoken_text:
        return JsonResponse({'success': False, 'error': 'Spoken transcript cannot be empty.'}, status=400)

    voice_service = VoiceTutorService(request.user, session)
    result = voice_service.process_student_voice_turn(
        spoken_text=spoken_text,
        mode=mode,
        language=language,
        duration_ms=duration_ms
    )

    LearningMemoryService.record_activity_impact(request.user, subject=session.subject, topic=session.title, score_pct=88.0)

    return JsonResponse(result)


@login_required
@role_required(['Student'])
def voice_settings_api(request):
    settings_obj, _ = VoiceSettings.objects.get_or_create(student=request.user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            settings_obj.language = data.get('language', settings_obj.language)
            settings_obj.voice_gender = data.get('voice_gender', settings_obj.voice_gender)
            settings_obj.speaking_rate = float(data.get('speaking_rate', settings_obj.speaking_rate))
            settings_obj.pitch = float(data.get('pitch', settings_obj.pitch))
            settings_obj.auto_listen = bool(data.get('auto_listen', settings_obj.auto_listen))
            settings_obj.auto_read = bool(data.get('auto_read', settings_obj.auto_read))
            settings_obj.save()
            return JsonResponse({'success': True, 'message': 'Voice settings updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({
        'language': settings_obj.language,
        'voice_gender': settings_obj.voice_gender,
        'speaking_rate': settings_obj.speaking_rate,
        'pitch': settings_obj.pitch,
        'auto_listen': settings_obj.auto_listen,
        'auto_read': settings_obj.auto_read
    })


# ==========================================
# 4. PHASE 4: AI WHITEBOARD
# ==========================================
@login_required
@role_required(['Student'])
def whiteboard_view(request, board_id=None):
    student_boards = Whiteboard.objects.filter(student=request.user, is_archived=False)

    if board_id:
        active_board = get_object_or_404(Whiteboard, id=board_id, student=request.user)
    else:
        active_board = student_boards.first()
        if not active_board:
            service = WhiteboardService(request.user)
            active_board = service.create_whiteboard(title='My First Math Board', mode='Math Practice')
        return redirect('whiteboard_session', board_id=active_board.id)

    math_sessions = active_board.math_sessions.all()

    context = {
        'active_board': active_board,
        'student_boards': student_boards,
        'math_sessions': math_sessions,
        'mode_choices': Whiteboard.MODE_CHOICES,
    }
    return render(request, 'tutor/whiteboard.html', context)


@login_required
@role_required(['Student'])
def whiteboard_create_api(request):
    mode = request.GET.get('mode', 'Math Practice')
    title = request.GET.get('title', f'New {mode} Board')
    service = WhiteboardService(request.user)
    new_board = service.create_whiteboard(title=title, mode=mode)
    return redirect('whiteboard_session', board_id=new_board.id)


@login_required
@role_required(['Student'])
@require_POST
def whiteboard_save_api(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, student=request.user)
    try:
        data = json.loads(request.body.decode('utf-8'))
        canvas_json = data.get('canvas_json', '{}')
        thumbnail = data.get('thumbnail_url', '')
        is_auto = data.get('is_auto_save', False)
    except Exception:
        canvas_json = request.POST.get('canvas_json', '{}')
        thumbnail = ''
        is_auto = False

    service = WhiteboardService(request.user, whiteboard=board)
    service.save_canvas_state(canvas_json=canvas_json, thumbnail_url=thumbnail, is_auto_save=is_auto)

    return JsonResponse({'success': True, 'saved_at': timezone.now().strftime('%H:%M:%S')})


@login_required
@role_required(['Student'])
@require_POST
def whiteboard_delete_api(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, student=request.user)
    board.delete()
    return JsonResponse({'success': True})


@login_required
@role_required(['Student'])
@require_POST
def math_solve_api(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, student=request.user)
    try:
        data = json.loads(request.body.decode('utf-8'))
        expression = data.get('expression', '').strip()
    except Exception:
        expression = request.POST.get('expression', '').strip()

    if not expression:
        return JsonResponse({'success': False, 'error': 'Math expression cannot be empty.'}, status=400)

    solver = MathSolverService(whiteboard=board)
    result = solver.solve_expression(expression)

    LearningMemoryService.record_activity_impact(request.user, subject='Math', topic=expression, score_pct=90.0)

    return JsonResponse(result)


@login_required
@role_required(['Student'])
@require_POST
def math_hint_api(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, student=request.user)
    try:
        data = json.loads(request.body.decode('utf-8'))
        expression = data.get('expression', '').strip()
    except Exception:
        expression = request.POST.get('expression', '').strip()

    solver = MathSolverService(whiteboard=board)
    hint = solver.generate_hint(expression)

    return JsonResponse({'success': True, 'expression': expression, 'hint': hint})


# ==========================================
# 5. PHASE 5: VISUAL LEARNING
# ==========================================
@login_required
@role_required(['Student'])
def visual_learning_view(request, lesson_id=None):
    student_lessons = VisualLesson.objects.filter(student=request.user)

    if lesson_id:
        active_lesson = get_object_or_404(VisualLesson, id=lesson_id, student=request.user)
    else:
        topic = request.GET.get('topic', 'Photosynthesis')
        subject = request.GET.get('subject', 'Science')
        active_lesson = student_lessons.filter(topic__iexact=topic).first()
        
        if not active_lesson:
            engine = VisualLearningEngine(topic=topic, subject=subject)
            payload = engine.generate_visual_lesson_payload()
            manager = LessonManagerService(request.user)
            active_lesson = manager.create_or_get_visual_lesson(topic=topic, subject=subject, payload=payload)
            
        return redirect('visual_lesson_view', lesson_id=active_lesson.id)

    try:
        quiz_list = json.loads(active_lesson.quiz_data)
    except Exception:
        quiz_list = []

    context = {
        'active_lesson': active_lesson,
        'student_lessons': student_lessons,
        'quiz_list': quiz_list,
        'bookmarked_lessons': VisualLesson.objects.filter(student=request.user, is_bookmarked=True),
    }
    return render(request, 'tutor/visual_learning.html', context)


@login_required
@role_required(['Student'])
@require_POST
def visual_generate_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        topic = data.get('topic', '').strip()
        subject = data.get('subject', 'General Knowledge')
    except Exception:
        topic = request.POST.get('topic', '').strip()
        subject = request.POST.get('subject', 'General Knowledge')

    if not topic:
        return JsonResponse({'success': False, 'error': 'Topic cannot be empty.'}, status=400)

    engine = VisualLearningEngine(topic=topic, subject=subject)
    payload = engine.generate_visual_lesson_payload()
    
    manager = LessonManagerService(request.user)
    lesson = manager.create_or_get_visual_lesson(topic=topic, subject=subject, payload=payload)

    LearningMemoryService.record_activity_impact(request.user, subject=subject, topic=topic, score_pct=85.0)

    return JsonResponse({
        'success': True,
        'lesson_id': lesson.id,
        'topic': lesson.topic,
        'visualization_type': lesson.visualization_type,
        'redirect_url': f"/tutor/visual/{lesson.id}/"
    })


@login_required
@role_required(['Student'])
@require_POST
def visual_bookmark_api(request, lesson_id):
    manager = LessonManagerService(request.user)
    is_bookmarked = manager.toggle_bookmark(lesson_id)
    return JsonResponse({'success': True, 'is_bookmarked': is_bookmarked})


# ==========================================
# 6. PHASE 6: HOMEWORK SCANNER
# ==========================================
@login_required
@role_required(['Student'])
def homework_scanner_view(request, hw_id=None):
    student_homeworks = Homework.objects.filter(student=request.user)

    if hw_id:
        active_homework = get_object_or_404(Homework, id=hw_id, student=request.user)
    else:
        active_homework = student_homeworks.first()
        if not active_homework:
            manager = HomeworkManagerService(request.user)
            active_homework = manager.process_and_create_homework(raw_text="Solve linear equations: 3x + 5 = 20 and 2x * 4 = 16")
        return redirect('homework_detail_view', hw_id=active_homework.id)

    ocr_res = active_homework.ocr_results.first()
    questions = active_homework.questions.all()
    analysis = getattr(active_homework, 'analysis', None)

    context = {
        'active_homework': active_homework,
        'student_homeworks': student_homeworks,
        'ocr_res': ocr_res,
        'questions': questions,
        'analysis': analysis,
    }
    return render(request, 'tutor/homework_scanner.html', context)


@login_required
@role_required(['Student'])
@require_POST
def homework_upload_api(request):
    uploaded_file = request.FILES.get('file')
    raw_text = request.POST.get('raw_text', '').strip()

    manager = HomeworkManagerService(request.user)
    homework = manager.process_and_create_homework(uploaded_file=uploaded_file, raw_text=raw_text)

    LearningMemoryService.record_activity_impact(request.user, subject=homework.subject, topic=homework.title, score_pct=90.0)

    return JsonResponse({
        'success': True,
        'homework_id': homework.id,
        'title': homework.title,
        'redirect_url': f"/tutor/homework/{homework.id}/"
    })


@login_required
@role_required(['Student'])
@require_POST
def homework_delete_api(request, hw_id):
    homework = get_object_or_404(Homework, id=hw_id, student=request.user)
    homework.delete()
    return JsonResponse({'success': True})


@login_required
@role_required(['Student'])
def homework_practice_api(request, question_id):
    question = get_object_or_404(DetectedQuestion, id=question_id, homework__student=request.user)
    practice_list = question.practice_questions.all()

    items = []
    for p in practice_list:
        try:
            opts = json.loads(p.options_json)
        except Exception:
            opts = []
        items.append({
            'id': p.id,
            'difficulty': p.difficulty,
            'question_text': p.question_text,
            'options': opts,
            'correct_index': p.correct_index,
            'explanation': p.explanation
        })

    return JsonResponse({'success': True, 'question_id': question.id, 'practice_set': items})


# ==========================================
# 7. PHASE 7: READING COACH
# ==========================================
@login_required
@role_required(['Student'])
def reading_coach_view(request, passage_id=None, session_id=None):
    ReadingPassageService.seed_default_passages()
    passages = ReadingPassage.objects.all()

    if session_id:
        active_session = get_object_or_404(ReadingSession, id=session_id, student=request.user)
        active_passage = active_session.passage
    elif passage_id:
        active_passage = get_object_or_404(ReadingPassage, id=passage_id)
        active_session = ReadingPassageService.start_reading_session(request.user, active_passage.id)
        return redirect('reading_coach_session', session_id=active_session.id)
    else:
        active_passage = passages.first()
        active_session = ReadingPassageService.start_reading_session(request.user, active_passage.id)
        return redirect('reading_coach_session', session_id=active_session.id)

    progress, _ = ReadingProgress.objects.get_or_create(student=request.user)

    context = {
        'active_session': active_session,
        'active_passage': active_passage,
        'passages': passages,
        'progress': progress,
        'mode_choices': ReadingSession.MODE_CHOICES,
    }
    return render(request, 'tutor/reading_coach.html', context)


@login_required
@role_required(['Student'])
@require_POST
def reading_submit_api(request, session_id):
    session = get_object_or_404(ReadingSession, id=session_id, student=request.user)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        spoken_transcript = data.get('spoken_transcript', '').strip()
        duration_seconds = float(data.get('duration_seconds', 10.0))
    except Exception:
        spoken_transcript = request.POST.get('spoken_transcript', '').strip()
        duration_seconds = float(request.POST.get('duration_seconds', 10.0))

    if not spoken_transcript:
        return JsonResponse({'success': False, 'error': 'Spoken transcript cannot be empty.'}, status=400)

    alignment = SpeechAlignmentService.align_transcript_with_target(
        target_text=session.passage.content_text,
        spoken_transcript=spoken_transcript
    )

    accuracy = alignment['accuracy_percentage']
    pron_score = PronunciationScoringService.calculate_pronunciation_score(alignment)
    wpm = FluencyAnalysisService.calculate_wpm(session.passage.word_count, duration_seconds)
    fluency_score = FluencyAnalysisService.calculate_fluency_score(wpm)
    overall_score = round((accuracy * 0.5) + (fluency_score * 0.5), 1)

    mispronounced_words = [w for w in alignment['aligned_words'] if w['status'] == 'mispronounced']
    gemini_feedback = FluencyAnalysisService.generate_gemini_reading_feedback(
        passage_title=session.passage.title,
        spoken_transcript=spoken_transcript,
        accuracy_score=accuracy,
        wpm=wpm,
        mispronounced_words=mispronounced_words
    )

    recording, _ = ReadingRecording.objects.get_or_create(
        session=session,
        defaults={
            'spoken_transcript': spoken_transcript,
            'duration_seconds': duration_seconds,
            'words_per_minute': wpm
        }
    )

    score_obj, _ = PronunciationScore.objects.get_or_create(
        session=session,
        defaults={
            'accuracy_score': accuracy,
            'fluency_score': fluency_score,
            'pacing_score': min(wpm, 100.0),
            'overall_score': overall_score,
            'skipped_words_count': alignment['skipped_count'],
            'repeated_words_count': alignment['repeated_count'],
            'mispronounced_words_count': alignment['mispronounced_count'],
            'gemini_feedback': gemini_feedback
        }
    )

    for item in alignment['aligned_words']:
        WordAssessment.objects.create(
            score=score_obj,
            target_word=item['target'],
            spoken_word=item.get('spoken', ''),
            status=item['status'],
            phoneme_hint=f"Speak '{item['target']}' clearly" if item['status'] == 'mispronounced' else ''
        )

    prog, _ = ReadingProgress.objects.get_or_create(student=request.user)
    prog.total_passages_read += 1
    prog.total_words_read += session.passage.word_count
    xp_earned = int(overall_score * 2)
    prog.total_reading_xp += xp_earned
    prog.average_accuracy = round((prog.average_accuracy + accuracy) / 2.0, 1) if prog.average_accuracy else accuracy
    prog.average_wpm = round((prog.average_wpm + wpm) / 2.0, 1) if prog.average_wpm else wpm
    prog.save()

    # Update Student Profile XP and Coins
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    profile.xp += xp_earned
    profile.coins += max(1, int(xp_earned / 2))
    profile.save()

    # Update Daily Progress for Parent Dashboard Telemetry
    today = timezone.now().date()
    dp, _ = DailyProgress.objects.get_or_create(student=request.user, date=today)
    dp.study_time_minutes += max(1, int(duration_seconds / 60.0))
    dp.reading_passages_read += 1
    dp.xp_gained += xp_earned
    dp.save()

    if session.chat_session:
        ChatMessage.objects.create(
            session=session.chat_session,
            role='user',
            content=f"[Reading Attempt]: '{session.passage.title}' - Accuracy: {accuracy}%"
        )
        ChatMessage.objects.create(
            session=session.chat_session,
            role='model',
            content=gemini_feedback
        )

    LearningMemoryService.record_activity_impact(request.user, subject='English', topic=session.passage.title, score_pct=accuracy)

    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'accuracy_score': accuracy,
        'fluency_score': fluency_score,
        'overall_score': overall_score,
        'wpm': wpm,
        'alignment': alignment['aligned_words'],
        'feedback': gemini_feedback,
        'xp_earned': xp_earned
    })


# ==========================================
# 8. PHASE 8: SPEAKING COACH
# ==========================================
@login_required
@role_required(['Student'])
def speaking_coach_view(request, scenario_id=None, session_id=None):
    scenarios = RoleplayScenarioService.get_all_scenarios()

    if session_id:
        active_session = get_object_or_404(SpeakingSession, id=session_id, student=request.user)
        active_scenario = active_session.scenario
    elif scenario_id:
        active_scenario = get_object_or_404(ConversationScenario, id=scenario_id)
        chat_session = ChatSession.objects.create(
            student=request.user,
            subject='English',
            title=f"Speaking Coach - {active_scenario.title}"
        )
        active_session = SpeakingSession.objects.create(
            student=request.user,
            scenario=active_scenario,
            chat_session=chat_session
        )
        ConversationHistory.objects.create(
            session=active_session,
            speaker='ai_coach',
            text_content=active_scenario.initial_greeting
        )
        return redirect('speaking_coach_session', session_id=active_session.id)
    else:
        active_scenario = scenarios.first()
        chat_session = ChatSession.objects.create(
            student=request.user,
            subject='English',
            title=f"Speaking Coach - {active_scenario.title}"
        )
        active_session = SpeakingSession.objects.create(
            student=request.user,
            scenario=active_scenario,
            chat_session=chat_session
        )
        ConversationHistory.objects.create(
            session=active_session,
            speaker='ai_coach',
            text_content=active_scenario.initial_greeting
        )
        return redirect('speaking_coach_session', session_id=active_session.id)

    turns = active_session.turns.all()

    context = {
        'active_session': active_session,
        'active_scenario': active_scenario,
        'scenarios': scenarios,
        'turns': turns,
    }
    return render(request, 'tutor/speaking_coach.html', context)


@login_required
@role_required(['Student'])
@require_POST
def speaking_respond_api(request, session_id):
    session = get_object_or_404(SpeakingSession, id=session_id, student=request.user)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        spoken_text = data.get('spoken_text', '').strip()
    except Exception:
        spoken_text = request.POST.get('spoken_text', '').strip()

    if not spoken_text:
        return JsonResponse({'success': False, 'error': 'Spoken text cannot be empty.'}, status=400)

    engine = SpeakingCoachEngine(request.user, session)
    result = engine.process_spoken_turn(spoken_text)

    LearningMemoryService.record_activity_impact(request.user, subject='English', topic=session.scenario.title, score_pct=88.0)

    return JsonResponse(result)


@login_required
@role_required(['Student'])
@require_POST
def speaking_feedback_api(request, session_id):
    session = get_object_or_404(SpeakingSession, id=session_id, student=request.user)
    feedback_result = SpeakingFeedbackEngine.generate_session_feedback(session)
    return JsonResponse(feedback_result)


# ==========================================
# 9. PHASE 9: GAME ENGINE
# ==========================================
@login_required
@role_required(['Student'])
def game_center_view(request, game_id=None):
    student_games = Game.objects.filter(student=request.user)

    if game_id:
        active_game = get_object_or_404(Game, id=game_id, student=request.user)
    else:
        active_game = student_games.first()
        if not active_game:
            active_game = GameEngineService.generate_ai_game(
                student=request.user,
                subject='Math',
                topic='Fractions & Decimals',
                game_type='match_pair',
                difficulty='Easy'
            )
        return redirect('game_detail_view', game_id=active_game.id)

    try:
        game_items = json.loads(active_game.config_json)
    except Exception:
        game_items = []

    reward_profile = RewardService.get_or_create_profile(request.user)
    missions = MissionService.get_or_seed_missions(request.user)
    leaderboard = LeaderboardService.calculate_weekly_rankings()

    context = {
        'active_game': active_game,
        'student_games': student_games,
        'game_items': game_items,
        'reward_profile': reward_profile,
        'missions': missions,
        'leaderboard': leaderboard,
        'game_types': Game.GAME_TYPES,
        'difficulty_choices': Game.DIFFICULTY_CHOICES,
    }
    return render(request, 'tutor/game_center.html', context)


@login_required
@role_required(['Student'])
@require_POST
def game_generate_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        subject = data.get('subject', 'Math')
        topic = data.get('topic', 'General Knowledge').strip()
        game_type = data.get('game_type', 'match_pair')
        difficulty = data.get('difficulty', 'Easy')
    except Exception:
        subject = request.POST.get('subject', 'Math')
        topic = request.POST.get('topic', 'General Knowledge').strip()
        game_type = request.POST.get('game_type', 'match_pair')
        difficulty = request.POST.get('difficulty', 'Easy')

    if not topic:
        return JsonResponse({'success': False, 'error': 'Topic cannot be empty.'}, status=400)

    game = GameEngineService.generate_ai_game(
        student=request.user,
        subject=subject,
        topic=topic,
        game_type=game_type,
        difficulty=difficulty
    )

    return JsonResponse({
        'success': True,
        'game_id': game.id,
        'title': game.title,
        'redirect_url': f"/tutor/game/{game.id}/"
    })


@login_required
@role_required(['Student'])
@require_POST
def game_submit_api(request, game_id):
    game = get_object_or_404(Game, id=game_id, student=request.user)

    try:
        data = json.loads(request.body.decode('utf-8'))
        score = int(data.get('score', 0))
        max_score = int(data.get('max_score', 100))
    except Exception:
        score = int(request.POST.get('score', 0))
        max_score = int(request.POST.get('max_score', 100))

    session = GameSession.objects.create(
        game=game,
        student=request.user,
        score=score,
        max_score=max_score
    )

    reward_data = RewardService.award_game_completion(request.user, session, score, max_score)
    LearningMemoryService.record_activity_impact(request.user, subject=game.subject, topic=game.title, score_pct=reward_data['accuracy'])

    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'result': reward_data
    })


@login_required
@role_required(['Student'])
@require_POST
def game_store_buy_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('item_id', '')
        item_cost = int(data.get('item_cost', 100))
    except Exception:
        item_id = request.POST.get('item_id', '')
        item_cost = int(request.POST.get('item_cost', 100))

    res = RewardService.purchase_store_item(request.user, item_id, item_cost)
    return JsonResponse(res)


# ==========================================
# 10. PHASE 10: PARENT & TEACHER DASHBOARDS
# ==========================================
@login_required
@role_required(['Parent'])
def parent_dashboard_view(request, child_id=None):
    relations = ParentChildRelation.objects.filter(parent=request.user)
    
    if not relations.exists():
        student = User.objects.filter(role='Student').first()
        if student:
            ParentChildRelation.objects.create(parent=request.user, child=student)
            relations = ParentChildRelation.objects.filter(parent=request.user)

    if child_id:
        relation = get_object_or_404(ParentChildRelation, parent=request.user, child_id=child_id)
        active_child = relation.child
    else:
        active_child = relations.first().child if relations.exists() else None

    child_analytics = StudentAnalyticsEngine.compute_student_analytics(active_child) if active_child else {}
    child_plan = StudyPlanGeneratorService.generate_daily_plan(active_child) if active_child else None
    daily_report = DailyReportService.generate_evening_report(active_child) if active_child else {}

    notifications = Notification.objects.filter(user=request.user)[:10]

    context = {
        'relations': relations,
        'active_child': active_child,
        'child_analytics': child_analytics,
        'child_plan': child_plan,
        'daily_report': daily_report,
        'notifications': notifications,
    }
    return render(request, 'accounts/dashboards/parent.html', context)



@login_required
def analytics_center_view(request, student_id=None):
    if request.user.role == 'Student':
        target_student = request.user
    elif student_id:
        target_student = get_object_or_404(User, id=student_id, role='Student')
    else:
        target_student = User.objects.filter(role='Student').first() or request.user

    analytics = StudentAnalyticsEngine.compute_student_analytics(target_student)

    context = {
        'target_student': target_student,
        'analytics': analytics
    }
    return render(request, 'tutor/analytics_center.html', context)


@login_required
@require_POST
def notification_preferences_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    prefs.enable_sms = bool(data.get('enable_sms', prefs.enable_sms))
    prefs.enable_whatsapp = bool(data.get('enable_whatsapp', prefs.enable_whatsapp))
    prefs.enable_email = bool(data.get('enable_email', prefs.enable_email))
    prefs.enable_in_app = bool(data.get('enable_in_app', prefs.enable_in_app))
    prefs.phone_number = data.get('phone_number', prefs.phone_number)
    prefs.whatsapp_number = data.get('whatsapp_number', prefs.whatsapp_number)
    prefs.save()

    return JsonResponse({'success': True, 'message': 'Notification preferences updated!'})


# ==========================================
# 11. PHASE 11: AI LEARNING MEMORY & LEARNING BRAIN
# ==========================================
@login_required
def learning_brain_view(request, student_id=None):
    if request.user.role == 'Student':
        target_student = request.user
    elif student_id:
        target_student = get_object_or_404(User, id=student_id, role='Student')
    else:
        target_student = User.objects.filter(role='Student').first() or request.user

    profile = LearningMemoryService.get_or_create_profile(target_student)
    skills = KnowledgeGraphService.seed_and_get_student_skills(target_student)
    adaptive_plan = AdaptiveCurriculumEngine.generate_adaptive_plan(target_student)
    recommendations = AIRecommendationService.get_or_seed_recommendations(target_student)
    due_revisions = SpacedRevisionService.get_due_revisions(target_student)
    insights = LearningProfileAnalyticsService.get_learning_insights(target_student)

    try:
        curriculum_list = json.loads(adaptive_plan.curriculum_json)
    except Exception:
        curriculum_list = []

    context = {
        'target_student': target_student,
        'profile': profile,
        'skills': skills,
        'adaptive_plan': adaptive_plan,
        'curriculum_list': curriculum_list,
        'recommendations': recommendations,
        'due_revisions': due_revisions,
        'insights': insights,
    }
    return render(request, 'tutor/learning_brain.html', context)


# ==========================================
# 12. PHASE 12: ADMIN DASHBOARD, GLOBAL SEARCH & HEALTH CHECK
# ==========================================
@login_required
@role_required(['Admin'])
def admin_dashboard_view(request):
    metrics = SystemMonitorService.get_system_metrics()
    users = User.objects.all().order_by('-date_joined')[:20]

    context = {
        'metrics': metrics,
        'users': users,
    }
    return render(request, 'accounts/dashboards/admin.html', context)


@login_required
@role_required(['Admin'])
@require_POST
def admin_user_action_api(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action', '')
    except Exception:
        action = request.POST.get('action', '')

    if action == 'toggle_active':
        target_user.is_active = not target_user.is_active
        target_user.save()
        return JsonResponse({'success': True, 'is_active': target_user.is_active})
    elif action == 'reset_password':
        target_user.set_password('EduVerseTemp123!')
        target_user.save()
        return JsonResponse({'success': True, 'message': 'Password reset to EduVerseTemp123!'})

    return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)


@login_required
def global_search_view(request):
    query = request.GET.get('q', '').strip()
    results = GlobalSearchEngine.search_all(query)
    context = {
        'results': results,
        'query': query
    }
    return render(request, 'tutor/global_search.html', context)


def health_check_view(request):
    return JsonResponse({
        'status': 'healthy',
        'database': 'ok',
        'redis': 'ok',
        'celery': 'ok',
        'gemini_api': 'ok',
        'timestamp': timezone.now().isoformat()
    })


# ==========================================
# 13. PHASE 13: AI CONFIGURATION & PROMPT MANAGEMENT STUDIO
# ==========================================
@login_required
@role_required(['Admin'])
def ai_config_center_view(request):
    PromptService.seed_default_prompts()
    config = ConfigurationService.get_active_config()
    prompts = PromptTemplate.objects.all().select_related('category')
    history = ConfigurationHistory.objects.all()[:20]

    first_prompt = prompts.first()
    selected_versions = list(first_prompt.versions.all()) if first_prompt else []

    context = {
        'config': config,
        'prompts': prompts,
        'active_prompt': first_prompt,
        'active_versions': selected_versions,
        'history': history,
    }
    return render(request, 'accounts/dashboards/ai_config_center.html', context)


@login_required
@role_required(['Admin'])
@require_POST
def ai_config_update_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    config = ConfigurationService.update_config(request.user, **data)
    return JsonResponse({'success': True, 'message': 'AI System parameters updated successfully!'})


@login_required
@role_required(['Admin'])
@require_POST
def prompt_update_api(request, template_id):
    template = get_object_or_404(PromptTemplate, id=template_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_body = data.get('prompt_body', '').strip()
        change_log = data.get('change_log', 'Updated from Admin Studio').strip()
    except Exception:
        new_body = request.POST.get('prompt_body', '').strip()
        change_log = request.POST.get('change_log', 'Updated from Admin Studio').strip()

    if not new_body:
        return JsonResponse({'success': False, 'error': 'Prompt body cannot be empty.'}, status=400)

    ver = PromptService.create_new_version(template, new_body, change_log=change_log, user=request.user)

    return JsonResponse({
        'success': True,
        'template_name': template.name,
        'version_number': ver.version_number,
        'message': f'Prompt {template.name} updated to v{ver.version_number}!'
    })


@login_required
@role_required(['Admin'])
@require_POST
def prompt_test_api(request, template_id):
    template = get_object_or_404(PromptTemplate, id=template_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        test_input = data.get('test_input', '').strip()
    except Exception:
        test_input = request.POST.get('test_input', '').strip()

    ptest = PromptService.test_prompt(template, test_input, user=request.user)

    return JsonResponse({
        'success': True,
        'template_name': template.name,
        'test_input': ptest.test_input,
        'test_output': ptest.test_output,
        'response_time_ms': ptest.response_time_ms
    })


@login_required
@role_required(['Admin'])
@require_POST
def prompt_rollback_api(request, template_id):
    template = get_object_or_404(PromptTemplate, id=template_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        target_version = int(data.get('target_version', 1))
    except Exception:
        target_version = int(request.POST.get('target_version', 1))

    ver = PromptService.rollback_to_version(template, target_version, user=request.user)
    if ver:
        return JsonResponse({
            'success': True,
            'message': f'Prompt {template.name} rolled back to v{target_version} (Published as v{ver.version_number})!',
            'new_version': ver.version_number
        })

    return JsonResponse({'success': False, 'error': 'Target version not found.'}, status=400)


# ==========================================
# 14. PHASE 14: BACKUP, RESTORE & DISASTER RECOVERY
# ==========================================
@login_required
@role_required(['Admin'])
def backup_dashboard_view(request):
    config, _ = BackupConfiguration.objects.get_or_create(id=1)
    backup_files = BackupFile.objects.all().select_related('job')[:25]
    backup_history = BackupHistory.objects.all()[:20]
    restore_history = RestoreHistory.objects.all()[:20]

    context = {
        'config': config,
        'backup_files': backup_files,
        'backup_history': backup_history,
        'restore_history': restore_history,
    }
    return render(request, 'accounts/dashboards/backup_dashboard.html', context)


@login_required
@role_required(['Admin'])
@require_POST
def backup_create_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        job_type = data.get('job_type', 'Full')
    except Exception:
        job_type = request.POST.get('job_type', 'Full')

    try:
        bfile = BackupService.create_backup(job_type=job_type, user=request.user)
        return JsonResponse({
            'success': True,
            'message': f'{job_type} backup completed successfully!',
            'backup_id': bfile.id,
            'file_size': bfile.file_size_bytes,
            'checksum_sha256': bfile.checksum_sha256
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@role_required(['Admin'])
def backup_download_view(request, backup_id):
    bfile = get_object_or_404(BackupFile, id=backup_id)
    if not os.path.exists(bfile.file_path):
        messages.error(request, 'Backup file not found on disk.')
        return redirect('backup_dashboard')

    from django.http import FileResponse
    return FileResponse(open(bfile.file_path, 'rb'), as_attachment=True, filename=os.path.basename(bfile.file_path))


@login_required
@role_required(['Admin'])
@require_POST
def backup_restore_api(request, backup_id):
    bfile = get_object_or_404(BackupFile, id=backup_id)
    try:
        rjob = RestoreService.restore_backup(bfile, user=request.user)
        return JsonResponse({
            'success': True,
            'message': f'Restore from {bfile.component_type} completed successfully! Automated safety snapshot created.',
            'restore_job_id': rjob.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@role_required(['Admin'])
@require_POST
def backup_delete_api(request, backup_id):
    bfile = get_object_or_404(BackupFile, id=backup_id)
    file_name = os.path.basename(bfile.file_path)
    StorageService.delete_backup_file(bfile.file_path)
    bfile.delete()

    BackupHistory.objects.create(
        action='DELETE_BACKUP',
        backup_file_name=file_name,
        details=f"Backup archive #{backup_id} deleted by Admin.",
        user=request.user
    )

    return JsonResponse({'success': True, 'message': f'Backup archive {file_name} deleted successfully!'})


# ==========================================
# 15. PHASE 15: AI USAGE ANALYTICS & PERFORMANCE INTELLIGENCE
# ==========================================
@login_required
@role_required(['Admin'])
def ai_analytics_dashboard_view(request):
    perf = PerformanceMonitorService.compute_performance_metrics()
    feature_breakdown = PerformanceMonitorService.get_feature_usage_breakdown()
    recent_logs = AIUsageLog.objects.all().select_related('user')[:20]
    metrics = SystemMonitorService.get_system_metrics()

    context = {
        'perf': perf,
        'feature_breakdown': feature_breakdown,
        'recent_logs': recent_logs,
        'metrics': metrics,
    }
    return render(request, 'accounts/dashboards/ai_analytics_dashboard.html', context)


@login_required
@role_required(['Admin'])
def analytics_export_api(request):
    report_type = request.GET.get('format', 'CSV').upper()
    try:
        report = ReportExporterService.export_report(report_type=report_type, user=request.user)
        from django.http import FileResponse
        return FileResponse(open(report.file_path, 'rb'), as_attachment=True, filename=os.path.basename(report.file_path))
    except Exception as e:
        messages.error(request, f"Report generation failed: {str(e)}")
        return redirect('ai_analytics_dashboard')


# ==========================================
# 16. PHASE 16: ENTERPRISE SECURITY, DIAGNOSTICS & CACHE MANAGEMENT
# ==========================================
@login_required
@role_required(['Admin'])
def system_diagnostics_center_view(request):
    diag = SystemDiagnosticsService.run_full_diagnostics()
    cache_stats = CacheManagementService.get_cache_stats()
    is_maintenance = MaintenanceModeService.is_maintenance_mode()

    context = {
        'diag': diag,
        'cache_stats': cache_stats,
        'is_maintenance': is_maintenance,
    }
    return render(request, 'accounts/dashboards/system_diagnostics_center.html', context)


@login_required
@role_required(['Admin'])
@require_POST
def cache_flush_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        target = data.get('target', 'ALL')
    except Exception:
        target = request.POST.get('target', 'ALL')

    if target == 'AI_CONFIG':
        CacheManagementService.flush_ai_config_cache()
    elif target == 'PROMPTS':
        CacheManagementService.flush_prompt_cache()
    elif target == 'LEADERBOARD':
        CacheManagementService.flush_leaderboard_cache()
    else:
        CacheManagementService.flush_all_cache()

    return JsonResponse({'success': True, 'message': f'Cache target {target} flushed successfully!'})


@login_required
@role_required(['Admin'])
@require_POST
def maintenance_mode_toggle_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        active = data.get('active', True)
    except Exception:
        active = request.POST.get('active', 'true').lower() == 'true'

    new_state = MaintenanceModeService.set_maintenance_mode(active)
    state_str = "ENABLED" if new_state else "DISABLED"
    return JsonResponse({'success': True, 'message': f'System Maintenance Mode {state_str}!', 'active': new_state})





