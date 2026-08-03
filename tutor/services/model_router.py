from tutor.services.configuration_service import ConfigurationService
from tutor.services.prompt_service import PromptService

MODULE_PROMPT_MAP = {
    'AI Chat': 'default_chat_prompt',
    'Voice Tutor': 'default_voice_prompt',
    'Homework Scanner': 'default_ocr_prompt',
    'Reading Coach': 'default_reading_prompt',
    'Speaking Coach': 'default_speaking_prompt',
    'Visual Learning': 'default_visual_prompt',
    'Game Engine': 'default_game_prompt',
}

class ModelRouter:
    @staticmethod
    def get_dynamic_prompt(module_name):
        template_name = MODULE_PROMPT_MAP.get(module_name, 'default_chat_prompt')
        return PromptService.get_published_prompt(template_name)

    @staticmethod
    def get_dynamic_model_kwargs():
        config = ConfigurationService.get_active_config()
        return {
            'model_name': config.model_name,
            'temperature': config.temperature,
            'top_p': config.top_p,
            'top_k': config.top_k,
            'max_output_tokens': config.max_tokens,
        }
