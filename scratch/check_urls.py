import os
import re
import django

import sys
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverse_project.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

template_dir = 'templates'
accounts_templates = os.path.join('accounts', 'templates')
tutor_templates = os.path.join('tutor', 'templates')

url_pattern = re.compile(r"\{\%\s*url\s+['\"]([^'\"]+)['\"]")

all_urls = set()
broken_urls = []

for root, dirs, files in os.walk('.'):
    if 'templates' in root:
        for f in files:
            if f.endswith('.html'):
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    content = file_obj.read()
                    matches = url_pattern.findall(content)
                    for url_name in matches:
                        all_urls.add((url_name, fpath))

print(f"Found {len(all_urls)} unique URL references across templates.")

for url_name, fpath in all_urls:
    # Try resolving without args first, then with dummy args if needed
    resolved = False
    for test_args in [(), (1,), ('test',)]:
        try:
            reverse(url_name, args=test_args)
            resolved = True
            break
        except NoReverseMatch:
            try:
                # Try prefixed with tutor: or accounts:
                reverse(f"tutor:{url_name}", args=test_args)
                resolved = True
                break
            except NoReverseMatch:
                pass

    if not resolved:
        broken_urls.append((url_name, fpath))

if broken_urls:
    print("\nBROKEN URL REFERENCES FOUND:")
    for url_name, fpath in broken_urls:
        print(f"  - '{url_name}' in {fpath}")
else:
    print("\nALL TEMPLATE URL REFERENCES RESOLVED CLEANLY!")
