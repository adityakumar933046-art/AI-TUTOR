import re

class GrammarAnalysisService:
    @staticmethod
    def analyze_session_grammar(turns):
        student_turns = [t.text_content for t in turns if t.speaker == 'student']
        corrections = []

        for text in student_turns:
            # Common kid grammar checks (e.g. "i goes", "he do", "me want")
            if re.search(r'\b(i goes|he do|me want|they is)\b', text.lower()):
                fixed = text.replace('i goes', 'I go').replace('he do', 'he does').replace('me want', 'I want').replace('they is', 'they are')
                corrections.append({
                    'original': text,
                    'corrected': fixed,
                    'rule': "Subject-verb agreement: Use 'I go', 'he does', 'they are'."
                })

        score = max(70.0, 100.0 - (len(corrections) * 10.0))
        return {
            'grammar_score': round(score, 1),
            'corrections': corrections
        }
