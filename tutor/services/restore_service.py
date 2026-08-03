import os
import zipfile
import shutil
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from tutor.models import RestoreJob, RestoreHistory
from tutor.services.storage_service import StorageService
from tutor.services.backup_service import BackupService

class RestoreService:
    @staticmethod
    def restore_backup(backup_file, user=None):
        # 1. Verify Checksum & Integrity
        if not os.path.exists(backup_file.file_path):
            raise FileNotFoundError(f"Backup file not found at path: {backup_file.file_path}")

        if not StorageService.verify_file_integrity(backup_file.file_path, backup_file.checksum_sha256):
            raise ValueError("SHA256 checksum verification failed! The backup file is corrupted or tampered.")

        # 2. Automated Pre-Restore Safety Snapshot
        safety_file = BackupService.create_backup(job_type='Full', user=user)

        job = RestoreJob.objects.create(
            backup_file=backup_file,
            component_type=backup_file.component_type,
            status='Restoring',
            safety_backup_path=safety_file.file_path,
            restored_by=user if (user and getattr(user, 'is_authenticated', False)) else None
        )

        try:
            db_path = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', 'db.sqlite3')
            media_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))

            with zipfile.ZipFile(backup_file.file_path, 'r') as zipf:
                file_list = zipf.namelist()

                # Restore Database if present
                if "database/db.sqlite3" in file_list and os.path.exists(db_path):
                    db_temp = f"{db_path}.restore_temp"
                    with zipf.open("database/db.sqlite3") as source, open(db_temp, "wb") as target:
                        shutil.copyfileobj(source, target)
                    shutil.move(db_temp, db_path)

                # Restore Media Assets if present
                for member in file_list:
                    if member.startswith("media/") and not member.endswith("/"):
                        rel_path = member[len("media/"):]
                        target_file = os.path.join(media_dir, rel_path)
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                        with zipf.open(member) as source, open(target_file, "wb") as target:
                            shutil.copyfileobj(source, target)

            job.status = 'Completed'
            job.completed_at = timezone.now()
            job.save()

            RestoreHistory.objects.create(
                action='RESTORE_COMPLETED',
                details=f"Restored backup {backup_file.component_type} (Job #{job.id}). Safety backup: {safety_file.file_path}",
                user=user if (user and getattr(user, 'is_authenticated', False)) else None
            )

            return job

        except Exception as e:
            job.status = 'Failed'
            job.error_message = str(e)
            job.save()

            RestoreHistory.objects.create(
                action='RESTORE_FAILED',
                details=f"Restore Job #{job.id} failed: {str(e)}. Safety backup preserved.",
                user=user if (user and getattr(user, 'is_authenticated', False)) else None
            )
            raise e
