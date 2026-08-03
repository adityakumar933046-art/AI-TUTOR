import time
import logging
from django.core.cache import cache
from tutor.models import PromptCategory, PromptTemplate, PromptVersion, PromptTest

logger = logging.getLogger(__name__)

DEFAULT_MODULE_PROMPTS = [
    {
        "category": "AI Chat",
        "name": "default_chat_prompt",
        "body": "You are Sparky, an encouraging, patient, and highly engaging AI Tutor for children. Use age-appropriate analogies, ask guiding questions (Socratic method), and keep explanations fun."
    },
    {
        "category": "Voice Tutor",
        "name": "default_voice_prompt",
        "body": "You are Sparky, a conversational Voice AI Tutor. Keep your spoken responses concise, enthusiastic, and easy to pronounce for voice synthesis."
    },
    {
        "category": "Homework Scanner",
        "name": "default_ocr_prompt",
        "body": "You are an expert Document OCR Assistant. Clean up scanned homework text, identify question numbers, and generate clear step-by-step solutions with encouraging hints."
    },
    {
        "category": "Reading Coach",
        "name": "default_reading_prompt",
        "body": "You are a Reading Coach. Analyze the child's reading attempt, assess accuracy, fluency, pacing, and provide warm, constructive phoneme feedback."
    },
    {
        "category": "Speaking Coach",
        "name": "default_speaking_prompt",
        "body": "You are a Speaking Coach simulating immersive real-world roleplay scenarios. Encourage full sentence responses and gently correct grammar and vocabulary."
    },
    {
        "category": "Visual Learning",
        "name": "default_visual_prompt",
        "body": "You are a Visual Learning Generator. Structure complex topics into Mermaid.js flowcharts, mind maps, analogies, and mini-quizzes."
    },
    {
        "category": "Game Engine",
        "name": "default_game_prompt",
        "body": "You are an AI Game Generator. Create fun educational match-pair cards, memory flip games, and drag-and-drop sorting questions for kids."
    }
]

class PromptService:
    @staticmethod
    def seed_default_prompts():
        for item in DEFAULT_MODULE_PROMPTS:
            cat, _ = PromptCategory.objects.get_or_create(name=item['category'])
            tpl, created = PromptTemplate.objects.get_or_create(
                category=cat,
                name=item['name'],
                defaults={'status': 'Published', 'current_version_number': 1}
            )
            if created:
                PromptVersion.objects.create(
                    template=tpl,
                    version_number=1,
                    prompt_body=item['body'],
                    change_log='Initial default prompt release'
                )

    @staticmethod
    def get_published_prompt(template_name):
        cache_key = f"active_prompt_{template_name}"
        cached_body = cache.get(cache_key)
        if cached_body:
            return cached_body

        PromptService.seed_default_prompts()
        tpl = PromptTemplate.objects.filter(name=template_name, status='Published').first()
        if not tpl:
            tpl = PromptTemplate.objects.filter(name=template_name).first()

        if tpl:
            ver = PromptVersion.objects.filter(template=tpl, version_number=tpl.current_version_number).first()
            if ver:
                cache.set(cache_key, ver.prompt_body, 3600)
                return ver.prompt_body

        return "You are an encouraging AI Tutor for children."

    @staticmethod
    def create_new_version(template, new_body, change_log='', user=None):
        new_ver_num = template.current_version_number + 1
        ver = PromptVersion.objects.create(
            template=template,
            version_number=new_ver_num,
            prompt_body=new_body,
            change_log=change_log,
            created_by=user if (user and getattr(user, 'is_authenticated', False)) else None
        )
        template.current_version_number = new_ver_num
        template.status = 'Published'
        template.save()

        cache.delete(f"active_prompt_{template.name}")
        return ver

    @staticmethod
    def rollback_to_version(template, target_version_num, user=None):
        ver = PromptVersion.objects.filter(template=template, version_number=target_version_num).first()
        if ver:
            return PromptService.create_new_version(
                template=template,
                new_body=ver.prompt_body,
                change_log=f"Rollback to version v{target_version_num}",
                user=user
            )
        return None

    @staticmethod
    def test_prompt(template, test_input, user=None):
        from tutor.services.gemini_service import GeminiTutorService
        ver = PromptVersion.objects.filter(template=template, version_number=template.current_version_number).first()
        body = ver.prompt_body if ver else "You are an AI Tutor."

        service = GeminiTutorService(subject='General Knowledge')
        start_time = time.time()
        res = service.generate_tutor_response(f"System Context: {body}\n\nTest Student Input: {test_input}", chat_history=[])
        duration_ms = int((time.time() - start_time) * 1000)

        output_text = res.get('response', '')

        ptest = PromptTest.objects.create(
            template=template,
            test_input=test_input,
            test_output=output_text,
            response_time_ms=duration_ms,
            tested_by=user if (user and getattr(user, 'is_authenticated', False)) else None
        )

        return ptest
