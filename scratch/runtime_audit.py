import os, sys
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverse_project.settings')
import django
django.setup()

from django.conf import settings
from django.urls import get_resolver, reverse, resolve, NoReverseMatch
from django.contrib.auth import get_user_model
from django.test import RequestFactory

print("========================================================")
print("             DJANGO RUNTIME DIAGNOSTIC AUDIT            ")
print("========================================================\n")

# 1 & 11. Settings module check
print(f"1. DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"   settings.SETTINGS_MODULE: {getattr(settings, 'SETTINGS_MODULE', 'N/A')}")

# 2. Active ROOT_URLCONF
print(f"2. Active ROOT_URLCONF: {settings.ROOT_URLCONF}")

# 3, 4, 6. URL patterns & namespaces
resolver = get_resolver()
print(f"3 & 4 & 6. Resolver URL Patterns count: {len(resolver.url_patterns)}")
print("   URL Namespaces in Resolver:")
for ns, val in resolver.namespace_dict.items():
    print(f"     - Namespace '{ns}': {val}")

print("\n   Loaded Global URL Names:")
all_names = list(resolver.reverse_dict.keys())
string_names = [n for n in all_names if isinstance(n, str)]
for name in sorted(string_names):
    print(f"     - {name}")

print(f"\n   Is 'learning_brain' in reverse_dict? {'learning_brain' in resolver.reverse_dict}")
print(f"   Is 'game_center' in reverse_dict? {'game_center' in resolver.reverse_dict}")
print(f"   Is 'reading_coach' in reverse_dict? {'reading_coach' in resolver.reverse_dict}")

# 5. INSTALLED_APPS
print("\n5. INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    print(f"     - {app}")

# 7, 8, 9. Middleware audit
print("\n7, 8, 9. MIDDLEWARE Stack:")
for mw in settings.MIDDLEWARE:
    print(f"     - {mw}")

# 10. Duplicate settings check
print("\n10. Checking for settings.py files in codebase:")
for root, dirs, files in os.walk('.'):
    if 'settings.py' in files and '.git' not in root:
        print(f"     - Found: {os.path.join(root, 'settings.py')}")

# 16 & 17 & 18. Programmatic reverse in student_dashboard view context
print("\n16 & 17 & 18. Testing reverse() inside student_dashboard view environment:")
factory = RequestFactory()
request = factory.get('/accounts/dashboard/student/')

User = get_user_model()
student_user, _ = User.objects.get_or_create(
    username='diag_student',
    defaults={
        'email': 'diag_student@eduverse.ai',
        'role': 'Student',
        'email_verified': True,
        'is_profile_complete': True
    }
)
request.user = student_user

print(f"   Testing reverse('learning_brain') with request.urlconf={getattr(request, 'urlconf', None)}:")
try:
    rev_url = reverse('learning_brain', urlconf=getattr(request, 'urlconf', None))
    print(f"   [SUCCESS] reverse('learning_brain') resolved to: {rev_url}")
except Exception as e:
    print(f"   [FAIL] reverse('learning_brain') failed: {type(e).__name__}: {e}")

# Render student.html directly
from django.template import loader
print("\n   Rendering 'accounts/dashboards/student.html' with template loader:")
try:
    t = loader.get_template('accounts/dashboards/student.html')
    rendered = t.render({'user': student_user, 'profile': getattr(student_user, 'student_profile', None)}, request)
    print(f"   [SUCCESS] Template rendered cleanly ({len(rendered)} bytes)!")
except Exception as e:
    print(f"   [FAIL] Template rendering failed: {type(e).__name__}: {e}")

print("\n========================================================")
