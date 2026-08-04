import logging
from tutor.models import AIUsageLog, FeatureUsage

logger = logging.getLogger(__name__)

class AnalyticsLoggingService:
    @staticmethod
    def log_ai_request(module_name, model_name='gemini-2.0-flash', tokens_used=0, response_time_ms=0, status_code=200, is_success=True, user=None):
        try:
            AIUsageLog.objects.create(
                module_name=module_name,
                model_name=model_name,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                status_code=status_code,
                is_success=is_success,
                user=user if (user and getattr(user, 'is_authenticated', False)) else None
            )

            feat, _ = FeatureUsage.objects.get_or_create(feature_name=module_name)
            feat.total_usage_count += 1
            feat.save()
        except Exception as e:
            logger.error(f"[ANALYTICS LOGGING ERROR]: {e}")
