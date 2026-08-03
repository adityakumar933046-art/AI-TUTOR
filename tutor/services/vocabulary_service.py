class VocabularyBuilderService:
    SYNONYM_MAP = {
        'good': 'fantastic / wonderful',
        'bad': 'unfortunate / challenging',
        'big': 'enormous / colossal',
        'happy': 'delighted / ecstatic',
        'sad': 'melancholy / gloomy',
        'like': 'admire / appreciate'
    }

    @staticmethod
    def analyze_session_vocabulary(turns):
        student_turns = [t.text_content.lower() for t in turns if t.speaker == 'student']
        words_found = []

        for text in student_turns:
            for simple_word, better_syn in VocabularyBuilderService.SYNONYM_MAP.items():
                if f" {simple_word} " in f" {text} ":
                    words_found.append({
                        'word': simple_word,
                        'better_synonym': better_syn
                    })

        vocab_score = min(100.0, 75.0 + (len(words_found) * 5.0))
        return {
            'vocabulary_score': round(vocab_score, 1),
            'upgrades': words_found[:5]
        }
