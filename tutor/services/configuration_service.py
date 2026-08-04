from django.core.cache import cache
from tutor.models import AIConfiguration, ConfigurationHistory

CACHE_KEY_CONFIG = "active_ai_configuration"

class ConfigurationService:
    @staticmethod
    def get_active_config():
        config = cache.get(CACHE_KEY_CONFIG)
        if not config:
            config, _ = AIConfiguration.objects.get_or_create(
                provider='Gemini',
                defaults={
                    'model_name': 'gemini-2.0-flash',
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_tokens': 2048,
                    'safety_level': 'Balanced',
                    'default_student_tone': 'Friendly'
                }
            )
            cache.set(CACHE_KEY_CONFIG, config, 3600)
        return config

    @staticmethod
    def update_config(user, **kwargs):
        config = ConfigurationService.get_active_config()

        for field, new_val in kwargs.items():
            if hasattr(config, field):
                old_val = getattr(config, field)
                if str(old_val) != str(new_val):
                    setattr(config, field, new_val)
                    ConfigurationHistory.objects.create(
                        field_name=field,
                        old_value=str(old_val),
                        new_value=str(new_val),
                        updated_by=user if (user and getattr(user, 'is_authenticated', False)) else None
                    )

        config.save()
        cache.delete(CACHE_KEY_CONFIG)
        return config
