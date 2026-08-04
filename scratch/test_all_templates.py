import os, sys
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverse_project.settings')
import django
django.setup()

from django.template import loader, TemplateDoesNotExist, TemplateSyntaxError
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse, NoReverseMatch

User = get_user_model()

print("--- 1. TESTING REVERSE() FOR ALL CORE ROUTES ---")
core_routes = [
    'home', 'login', 'register', 'logout', 'google_oauth', 'complete_profile', 'profile',
    'dashboard_student', 'dashboard_parent', 'dashboard_admin',
    'student_hub', 'chat_tutor', 'voice_tutor', 'whiteboard', 'visual_learning',
    'homework_scanner', 'reading_coach', 'speaking_coach', 'game_center',
    'parent_dashboard', 'analytics_center', 'learning_brain', 'admin_hub',
    'global_search', 'health_check', 'ai_config_center', 'backup_dashboard',
    'ai_analytics_dashboard', 'system_diagnostics_center'
]

reverse_errors = []
for r in core_routes:
    try:
        url = reverse(r)
        print(f"  [OK] reverse('{r}') = {url}")
    except Exception as e:
        print(f"  [FAIL] reverse('{r}') FAILED: {e}")
        reverse_errors.append((r, str(e)))

print("\n--- 2. TESTING TEMPLATE COMPILATION AND RENDERING ---")
factory = RequestFactory()

# Create or get a test user
dummy_user, _ = User.objects.get_or_create(
    username='template_tester',
    defaults={
        'email': 'tester@eduverse.ai',
        'role': 'Student',
        'email_verified': True,
        'is_profile_complete': True
    }
)

request = factory.get('/')
request.user = dummy_user

template_files = []
for root, dirs, files in os.walk('.'):
    if 'templates' in root:
        for f in files:
            if f.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, f), root)
                full_p = os.path.join(root, f).replace('\\', '/')
                if 'accounts/templates/' in full_p:
                    tpl_name = full_p.split('accounts/templates/')[1]
                elif 'tutor/templates/' in full_p:
                    tpl_name = full_p.split('tutor/templates/')[1]
                else:
                    tpl_name = f
                template_files.append((tpl_name, os.path.join(root, f)))

template_errors = []

for tpl_name, full_path in template_files:
    try:
        t = loader.get_template(tpl_name)
        rendered = t.render({'user': dummy_user, 'profile': getattr(dummy_user, 'student_profile', None)}, request)
        print(f"  [OK] Template '{tpl_name}' rendered successfully ({len(rendered)} bytes)")
    except Exception as e:
        print(f"  [FAIL] Template '{tpl_name}' ({full_path}) FAILED: {type(e).__name__}: {e}")
        template_errors.append((tpl_name, full_path, type(e).__name__, str(e)))

if reverse_errors or template_errors:
    print("\n================ ERRORS SUMMARY ================")
    if reverse_errors:
        print(f"REVERSE ERRORS ({len(reverse_errors)}):")
        for r, err in reverse_errors:
            print(f"  - {r}: {err}")
    if template_errors:
        print(f"TEMPLATE ERRORS ({len(template_errors)}):")
        for tpl, path, err_type, err in template_errors:
            print(f"  - [{tpl}] ({path}): {err_type} - {err}")
else:
    print("\n[SUCCESS] ALL CORE ROUTES AND ALL TEMPLATES RENDERED 100% CLEANLY WITH ZERO ERRORS!")
