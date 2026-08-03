import re

class SpeechAlignmentService:
    @staticmethod
    def align_transcript_with_target(target_text, spoken_transcript):
        target_words = [re.sub(r'[^\w\s]', '', w).lower() for w in target_text.split() if w]
        raw_target_words = target_text.split()
        spoken_words = [re.sub(r'[^\w\s]', '', w).lower() for w in spoken_transcript.split() if w]

        aligned = []
        skipped_count = 0
        mispronounced_count = 0
        repeated_count = 0
        correct_count = 0

        spoken_idx = 0
        for i, target in enumerate(target_words):
            raw_word = raw_target_words[i] if i < len(raw_target_words) else target
            
            if spoken_idx < len(spoken_words):
                spoken = spoken_words[spoken_idx]
                if target == spoken:
                    aligned.append({'target': raw_word, 'spoken': spoken, 'status': 'correct'})
                    correct_count += 1
                    spoken_idx += 1
                elif spoken_idx + 1 < len(spoken_words) and target == spoken_words[spoken_idx + 1]:
                    # Skipped first spoken word or repeated
                    aligned.append({'target': raw_word, 'spoken': spoken, 'status': 'repeated'})
                    repeated_count += 1
                    spoken_idx += 2
                else:
                    # Mispronounced or slight mismatch
                    aligned.append({'target': raw_word, 'spoken': spoken, 'status': 'mispronounced'})
                    mispronounced_count += 1
                    spoken_idx += 1
            else:
                # Skipped remaining words
                aligned.append({'target': raw_word, 'spoken': '', 'status': 'skipped'})
                skipped_count += 1

        total_words = max(len(target_words), 1)
        accuracy = round((correct_count / total_words) * 100, 1)

        return {
            'aligned_words': aligned,
            'correct_count': correct_count,
            'mispronounced_count': mispronounced_count,
            'skipped_count': skipped_count,
            'repeated_count': repeated_count,
            'total_target_words': total_words,
            'accuracy_percentage': accuracy
        }
