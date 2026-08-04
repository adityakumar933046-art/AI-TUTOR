from django.urls import path
from tutor import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.student_dashboard, name='student_hub'),
    
    # Phase 2: AI Chat Tutor
    path('chat/', views.chat_tutor_view, name='chat_tutor'),
    path('chat/<int:session_id>/', views.chat_tutor_view, name='chat_tutor_session'),
    path('chat/new/', views.chat_create_session, name='chat_create'),
    path('chat/<int:session_id>/send/', views.chat_send_message_api, name='chat_send_api'),
    path('chat/<int:session_id>/stream/', views.chat_stream_message_api, name='chat_stream_api'),
    path('chat/<int:session_id>/rename/', views.chat_rename_session, name='chat_rename_api'),
    path('chat/<int:session_id>/delete/', views.chat_delete_session, name='chat_delete_api'),
    path('chat/<int:session_id>/pin/', views.chat_pin_session, name='chat_pin_api'),

    # Phase 3: Human Voice AI Tutor
    path('voice/', views.voice_tutor_view, name='voice_tutor'),
    path('voice/<int:session_id>/', views.voice_tutor_view, name='voice_tutor_session'),
    path('voice/<int:session_id>/send/', views.voice_send_api, name='voice_send_api'),
    path('voice/settings/', views.voice_settings_api, name='voice_settings_api'),

    # Phase 4: AI Whiteboard & Smart Math Workspace
    path('whiteboard/', views.whiteboard_view, name='whiteboard'),
    path('whiteboard/<int:board_id>/', views.whiteboard_view, name='whiteboard_session'),
    path('whiteboard/new/', views.whiteboard_create_api, name='whiteboard_create'),
    path('whiteboard/<int:board_id>/save/', views.whiteboard_save_api, name='whiteboard_save_api'),
    path('whiteboard/<int:board_id>/delete/', views.whiteboard_delete_api, name='whiteboard_delete_api'),
    path('math/<int:board_id>/solve/', views.math_solve_api, name='math_solve_api'),
    path('math/<int:board_id>/hint/', views.math_hint_api, name='math_hint_api'),

    # Phase 5: AI Visual Learning Engine
    path('visual/', views.visual_learning_view, name='visual_learning'),
    path('visual/<int:lesson_id>/', views.visual_learning_view, name='visual_lesson_view'),
    path('visual/generate/', views.visual_generate_api, name='visual_generate_api'),
    path('visual/<int:lesson_id>/bookmark/', views.visual_bookmark_api, name='visual_bookmark_api'),

    # Phase 6: AI Homework Scanner & Document Intelligence Engine
    path('homework/', views.homework_scanner_view, name='homework_scanner'),
    path('homework/<int:hw_id>/', views.homework_scanner_view, name='homework_detail_view'),
    path('homework/upload/', views.homework_upload_api, name='homework_upload_api'),
    path('homework/<int:hw_id>/delete/', views.homework_delete_api, name='homework_delete_api'),
    path('homework/question/<int:question_id>/practice/', views.homework_practice_api, name='homework_practice_api'),

    # Phase 7: AI Reading Coach & Pronunciation Assessment Engine
    path('reading/', views.reading_coach_view, name='reading_coach'),
    path('reading/passage/<int:passage_id>/', views.reading_coach_view, name='reading_passage_view'),
    path('reading/session/<int:session_id>/', views.reading_coach_view, name='reading_coach_session'),
    path('reading/session/<int:session_id>/submit/', views.reading_submit_api, name='reading_submit_api'),

    # Phase 8: AI Speaking Coach & Conversation Simulator
    path('speaking/', views.speaking_coach_view, name='speaking_coach'),
    path('speaking/scenario/<int:scenario_id>/', views.speaking_coach_view, name='speaking_scenario_view'),
    path('speaking/session/<int:session_id>/', views.speaking_coach_view, name='speaking_coach_session'),
    path('speaking/session/<int:session_id>/respond/', views.speaking_respond_api, name='speaking_respond_api'),
    path('speaking/session/<int:session_id>/feedback/', views.speaking_feedback_api, name='speaking_feedback_api'),

    # Phase 9: AI Game Engine & Gamification Platform
    path('game/', views.game_center_view, name='game_center'),
    path('game/<int:game_id>/', views.game_center_view, name='game_detail_view'),
    path('game/generate/', views.game_generate_api, name='game_generate_api'),
    path('game/<int:game_id>/submit/', views.game_submit_api, name='game_submit_api'),
    path('game/store/buy/', views.game_store_buy_api, name='game_store_buy_api'),

    # Phase 10: Parent Dashboard, Teacher Dashboard, AI Analytics & Smart Notifications
    path('parent/', views.parent_dashboard_view, name='parent_dashboard'),
    path('parent/child/<int:child_id>/', views.parent_dashboard_view, name='parent_child_dashboard'),
    path('analytics/', views.analytics_center_view, name='analytics_center'),
    path('notifications/prefs/', views.notification_preferences_api, name='notification_prefs_api'),

    # Phase 11: AI Learning Memory, Adaptive Curriculum & Personal Learning Brain
    path('brain/', views.learning_brain_view, name='learning_brain'),
    path('brain/<int:student_id>/', views.learning_brain_view, name='learning_brain_student'),

    # Phase 12: Admin Dashboard, Global Search, Health & API v1
    path('admin-hub/', views.admin_dashboard_view, name='admin_hub'),
    path('admin-hub/user/<int:user_id>/action/', views.admin_user_action_api, name='admin_user_action_api'),
    path('search/', views.global_search_view, name='global_search'),
    path('health/', views.health_check_view, name='health_check'),
    path('api/v1/health/', views.health_check_view, name='api_v1_health'),

    # Phase 13: AI Configuration Center & Prompt Management Studio
    path('admin-hub/ai-config/', views.ai_config_center_view, name='ai_config_center'),
    path('admin-hub/ai-config/update/', views.ai_config_update_api, name='ai_config_update_api'),
    path('admin-hub/prompt/<int:template_id>/update/', views.prompt_update_api, name='prompt_update_api'),
    path('admin-hub/prompt/<int:template_id>/test/', views.prompt_test_api, name='prompt_test_api'),
    path('admin-hub/prompt/<int:template_id>/rollback/', views.prompt_rollback_api, name='prompt_rollback_api'),

    # Phase 14: Backup, Restore & Disaster Recovery Center
    path('admin-hub/backup/', views.backup_dashboard_view, name='backup_dashboard'),
    path('admin-hub/backup/create/', views.backup_create_api, name='backup_create_api'),
    path('admin-hub/backup/<int:backup_id>/download/', views.backup_download_view, name='backup_download_view'),
    path('admin-hub/backup/<int:backup_id>/restore/', views.backup_restore_api, name='backup_restore_api'),
    path('admin-hub/backup/<int:backup_id>/delete/', views.backup_delete_api, name='backup_delete_api'),

    # Phase 15: AI Usage Analytics & Performance Intelligence
    path('admin-hub/analytics/', views.ai_analytics_dashboard_view, name='ai_analytics_dashboard'),
    path('admin-hub/analytics/export/', views.analytics_export_api, name='analytics_export_api'),

    # Phase 16: Enterprise Security, System Diagnostics & Cache Center
    path('admin-hub/diagnostics/', views.system_diagnostics_center_view, name='system_diagnostics_center'),
    path('admin-hub/cache/flush/', views.cache_flush_api, name='cache_flush_api'),
    path('admin-hub/maintenance/toggle/', views.maintenance_mode_toggle_api, name='maintenance_mode_toggle_api'),
]
