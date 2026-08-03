from django.core.cache import cache

MAINTENANCE_CACHE_KEY = "system_maintenance_mode"

class MaintenanceModeService:
    @staticmethod
    def is_maintenance_mode():
        return cache.get(MAINTENANCE_CACHE_KEY, False)

    @staticmethod
    def set_maintenance_mode(active=True):
        cache.set(MAINTENANCE_CACHE_KEY, active, 86400)
        return active
