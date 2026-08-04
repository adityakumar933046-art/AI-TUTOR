import os, shutil

deleted_dirs = 0
deleted_files = 0

for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        shutil.rmtree(pycache_path, ignore_errors=True)
        deleted_dirs += 1
    for f in files:
        if f.endswith('.pyc') or f.endswith('.pyo'):
            os.remove(os.path.join(root, f))
            deleted_files += 1

print(f"Deleted {deleted_dirs} __pycache__ directories and {deleted_files} compiled .pyc/.pyo files.")
