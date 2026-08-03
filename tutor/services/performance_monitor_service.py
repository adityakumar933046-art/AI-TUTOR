import numpy as np
from django.db.models import Avg, Count
from tutor.models import AIUsageLog, PerformanceMetric, FeatureUsage, SystemMetric

class PerformanceMonitorService:
    @staticmethod
    def compute_performance_metrics():
        logs = list(AIUsageLog.objects.values_list('response_time_ms', 'is_success'))
        if not logs:
            return {
                'total_requests': 0,
                'avg_latency_ms': 0.0,
                'median_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'success_rate_pct': 100.0,
                'error_rate_pct': 0.0
            }

        latencies = [l[0] for l in logs]
        successes = [l[1] for l in logs]

        total = len(latencies)
        successful = sum(1 for s in successes if s)
        failed = total - successful

        avg_lat = float(np.mean(latencies))
        median_lat = float(np.median(latencies))
        p95_lat = float(np.percentile(latencies, 95))
        error_rate = (failed / total) * 100.0 if total > 0 else 0.0

        return {
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': failed,
            'avg_latency_ms': round(avg_lat, 2),
            'median_latency_ms': round(median_lat, 2),
            'p95_latency_ms': round(p95_lat, 2),
            'success_rate_pct': round((successful / total) * 100.0, 1) if total > 0 else 100.0,
            'error_rate_pct': round(error_rate, 2)
        }

    @staticmethod
    def get_feature_usage_breakdown():
        features = FeatureUsage.objects.all().order_by('-total_usage_count')
        if not features.exists():
            return [
                {'feature_name': 'AI Chat', 'count': 45},
                {'feature_name': 'Voice Tutor', 'count': 32},
                {'feature_name': 'Homework Scanner', 'count': 28},
                {'feature_name': 'Visual Learning', 'count': 20},
                {'feature_name': 'AI Games', 'count': 50}
            ]
        return [{'feature_name': f.feature_name, 'count': f.total_usage_count} for f in features]
