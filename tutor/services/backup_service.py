import os
import zipfile
import shutil
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from tutor.models import BackupJob, BackupFile, BackupHistory, PromptTemplate, PromptVersion
from tutor.services.storage_service import StorageService

class BackupService:
    @staticmethod
    def create_backup(job_type='Full', user=None):
        job = BackupJob.objects.create(
            job_type=job_type,
            status='Running',
            created_by=user if (user and getattr(user, 'is_authenticated', False)) else None
        )

        try:
            backup_dir = StorageService.get_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"eduverse_backup_{job_type.lower()}_{timestamp}.zip"
            archive_path = os.path.join(backup_dir, archive_name)

            db_path = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', 'db.sqlite3')
            media_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. Database Dump
                if job_type in ['Full', 'Database'] and os.path.exists(db_path):
                    zipf.write(db_path, arcname="database/db.sqlite3")

                # 2. Media Assets
                if job_type in ['Full', 'Media'] and os.path.exists(media_dir):
                    for root, dirs, files in os.walk(media_dir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, media_dir)
                            zipf.write(full_path, arcname=os.path.join("media", rel_path))

                # 3. AI Prompts Export
                if job_type in ['Full', 'Prompts']:
                    prompts_data = []
                    for tpl in PromptTemplate.objects.all():
                        ver = PromptVersion.objects.filter(template=tpl, version_number=tpl.current_version_number).first()
                        if ver:
                            prompts_data.append(f"=== [{tpl.category.name}] {tpl.name} (v{ver.version_number}) ===\n{ver.prompt_body}\n\n")
                    zipf.writestr("prompts/prompts_export.txt", "".join(prompts_data))

            file_size = os.path.getsize(archive_path)
            checksum = StorageService.compute_sha256(archive_path)

            backup_file = BackupFile.objects.create(
                job=job,
                component_type=job_type,
                file_path=archive_path,
                file_size_bytes=file_size,
                checksum_sha256=checksum
            )

            job.status = 'Completed'
            job.completed_at = timezone.now()
            job.save()

            BackupHistory.objects.create(
                action='CREATE_BACKUP',
                backup_file_name=archive_name,
                details=f"Job #{job.id} [{job_type}] completed ({file_size} bytes). SHA256: {checksum[:8]}...",
                user=user if (user and getattr(user, 'is_authenticated', False)) else None
            )

            return backup_file

        except Exception as e:
            job.status = 'Failed'
            job.error_message = str(e)
            job.save()

            BackupHistory.objects.create(
                action='BACKUP_FAILED',
                backup_file_name=job_type,
                details=f"Job #{job.id} failed: {str(e)}",
                user=user if (user and getattr(user, 'is_authenticated', False)) else None
            )
            raise e
