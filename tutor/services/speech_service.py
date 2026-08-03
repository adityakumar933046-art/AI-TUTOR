# Speech Helper Service for Language Mapping & Speech Synthesis Config

LANGUAGE_MAP = {
    'en-US': {
        'name': 'English (United States)',
        'bcp47': 'en-US',
        'voice_keyword': 'en'
    },
    'hi-IN': {
        'name': 'Hindi (भारत)',
        'bcp47': 'hi-IN',
        'voice_keyword': 'hi'
    },
    'en-IN': {
        'name': 'Hinglish / Indian English',
        'bcp47': 'en-IN',
        'voice_keyword': 'en-IN'
    }
}

class SpeechService:
    @staticmethod
    def get_speech_config(voice_settings):
        lang_info = LANGUAGE_MAP.get(voice_settings.language, LANGUAGE_MAP['en-US'])
        return {
            "bcp47": lang_info['bcp47'],
            "speaking_rate": voice_settings.speaking_rate,
            "pitch": voice_settings.pitch,
            "voice_gender": voice_settings.voice_gender,
            "auto_listen": voice_settings.auto_listen,
            "auto_read": voice_settings.auto_read
        }

    @staticmethod
    def sanitize_transcript(raw_text):
        if not raw_text:
            return ""
        return raw_text.strip()
