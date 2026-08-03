class PronunciationScoringService:
    @staticmethod
    def calculate_pronunciation_score(alignment_data):
        accuracy = alignment_data.get('accuracy_percentage', 0.0)
        mispronounced = alignment_data.get('mispronounced_count', 0)
        skipped = alignment_data.get('skipped_count', 0)

        # Pronunciation quality penalty for mispronunciations
        pron_score = max(0.0, accuracy - (mispronounced * 2.5))
        return round(pron_score, 1)

    @staticmethod
    def generate_phoneme_hints(mispronounced_words):
        hints = {}
        for item in mispronounced_words:
            w = item.get('target', '').lower()
            hints[w] = f"Break '{w}' into syllables and speak clearly!"
        return hints
