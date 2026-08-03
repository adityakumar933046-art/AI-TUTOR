import os
import hashlib
from django.conf import settings

BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

class StorageService:
    @staticmethod
    def get_backup_dir():
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR, exist_ok=True)
        return BACKUP_DIR

    @staticmethod
    def compute_sha256(file_path):
        if not os.path.exists(file_path):
            return ""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_file_integrity(file_path, expected_checksum):
        actual_checksum = StorageService.compute_sha256(file_path)
        return actual_checksum.lower() == expected_checksum.lower()

    @staticmethod
    def delete_backup_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
