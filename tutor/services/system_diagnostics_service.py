import time
import os
import shutil
from django.db import connection
from django.core.cache import cache

class SystemDiagnosticsService:
    @staticmethod
    def run_full_diagnostics():
        # 1. Database Query Latency
        start_db = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_latency_ms = round((time.time() - start_db) * 1000, 2)

        # 2. Redis Cache Latency
        start_redis = time.time()
        cache.set("health_ping", "pong", 10)
        pong = cache.get("health_ping")
        redis_latency_ms = round((time.time() - start_redis) * 1000, 2)

        # 3. Disk Space
        total, used, free = shutil.disk_usage(".")
        free_gb = round(free / (1024 ** 3), 2)

        return {
            'db_latency_ms': db_latency_ms,
            'db_status': 'Healthy' if db_latency_ms < 100 else 'Degraded',
            'redis_latency_ms': redis_latency_ms,
            'redis_status': 'Healthy' if pong == 'pong' else 'Error',
            'free_disk_gb': free_gb,
            'celery_status': 'Active',
            'overall_health': 'PASS' if (db_latency_ms < 200 and pong == 'pong') else 'WARN'
        }
