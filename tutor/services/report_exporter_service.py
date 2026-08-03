import os
import csv
import json
from datetime import datetime
from django.conf import settings
from tutor.models import AIUsageLog, UsageReport
from tutor.services.storage_service import StorageService

class ReportExporterService:
    @staticmethod
    def export_report(report_type='CSV', user=None):
        backup_dir = StorageService.get_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"ai_usage_analytics_{timestamp}.{report_type.lower()}"
        file_path = os.path.join(backup_dir, file_name)

        logs = AIUsageLog.objects.all().select_related('user')[:500]

        if report_type.upper() == 'CSV':
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Module', 'Model', 'Tokens', 'Latency MS', 'Status', 'Success', 'User', 'Timestamp'])
                for l in logs:
                    username = l.user.username if l.user else 'Anonymous'
                    writer.writerow([l.id, l.module_name, l.model_name, l.tokens_used, l.response_time_ms, l.status_code, l.is_success, username, l.timestamp])
        else: # JSON
            data = []
            for l in logs:
                data.append({
                    'id': l.id,
                    'module_name': l.module_name,
                    'model_name': l.model_name,
                    'tokens_used': l.tokens_used,
                    'response_time_ms': l.response_time_ms,
                    'status_code': l.status_code,
                    'is_success': l.is_success,
                    'user': l.user.username if l.user else 'Anonymous',
                    'timestamp': l.timestamp.isoformat()
                })
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        file_size = os.path.getsize(file_path)

        report = UsageReport.objects.create(
            report_type=report_type.upper(),
            file_path=file_path,
            file_size_bytes=file_size,
            generated_by=user if (user and getattr(user, 'is_authenticated', False)) else None
        )

        return report
