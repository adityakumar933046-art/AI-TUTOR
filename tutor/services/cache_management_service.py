from django.core.cache import cache

class CacheManagementService:
    @staticmethod
    def flush_all_cache():
        cache.clear()
        return True

    @staticmethod
    def flush_ai_config_cache():
        cache.delete("active_ai_configuration")
        return True

    @staticmethod
    def flush_prompt_cache(template_name=None):
        if template_name:
            cache.delete(f"active_prompt_{template_name}")
        else:
            cache.clear()
        return True

    @staticmethod
    def flush_leaderboard_cache():
        cache.delete("global_leaderboard_cache")
        return True

    @staticmethod
    def get_cache_stats():
        return {
            'backend': cache.__class__.__name__,
            'status': 'Operational'
        }
