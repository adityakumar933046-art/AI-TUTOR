import json
import re
import logging
from tutor.services.gemini_service import GeminiTutorService
from tutor.services.diagram_service import DiagramBuilderService

logger = logging.getLogger(__name__)

VISUAL_SYSTEM_INSTRUCTION = (
    "You are Sparky, an expert AI Visual Learning Architect for EduVerse AI Kids. "
    "Analyze the student topic and choose the single best visualization type: "
    "['Flowchart', 'Mind Map', 'Timeline', 'Cycle Diagram', 'Interactive Cards']. "
    "Provide a JSON object containing: "
    "1. 'visualization_type': string "
    "2. 'explanation': simple 2-paragraph concept breakdown for a child "
    "3. 'analogy': a fun real-world analogy "
    "4. 'mermaid_script': valid Mermaid.js script (e.g. 'graph TD\\n A[Sunlight] --> B[Leaf]...') "
    "5. 'quiz': array of 3 objects with 'question', 'options' (4 choices), 'correct_index' (0-3), and 'explanation' "
    "6. 'summary': 3 key takeaways"
)

class VisualLearningEngine:
    def __init__(self, topic, subject='General Knowledge'):
        self.topic = topic
        self.subject = subject

    def generate_visual_lesson_payload(self):
        gemini_service = GeminiTutorService(subject=self.subject)
        
        prompt = (
            f"Generate a rich visual learning lesson for the topic: '{self.topic}'. Subject: '{self.subject}'.\n"
            f"{VISUAL_SYSTEM_INSTRUCTION}\nReturn ONLY valid JSON format."
        )

        res = gemini_service.generate_tutor_response(prompt, chat_history=[])
        raw_text = res.get('response', '')

        # Parse JSON from response
        parsed_data = self._clean_and_parse_json(raw_text)

        # Fallback values if parsing fails
        if not parsed_data:
            parsed_data = self._generate_fallback_payload()

        return parsed_data

    def _clean_and_parse_json(self, raw_text):
        try:
            # Extract JSON block if wrapped in ```json ... ```
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
            json_str = match.group(1) if match else raw_text.strip()
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse Gemini Visual JSON: {e}")
            return None

    def _generate_fallback_payload(self):
        mermaid_script = (
            f"graph TD\n"
            f"    A[\"🚀 Start Learning: {self.topic}\"] --> B[\"💡 Core Concept\"]\n"
            f"    B --> C[\"🌟 Real-World Application\"]\n"
            f"    C --> D[\"🏆 Mastered!\"]"
        )
        return {
            "visualization_type": "Flowchart",
            "explanation": f"Let's explore {self.topic}! It is an exciting concept in {self.subject} that helps us understand how the world works.",
            "analogy": f"Think of {self.topic} like building with colorful LEGO blocks where each piece connects to create something amazing!",
            "mermaid_script": mermaid_script,
            "quiz": [
                {
                    "question": f"What is the main idea behind {self.topic}?",
                    "options": [f"Understanding {self.topic}", "Sleeping all day", "Flying to space", "Doing nothing"],
                    "correct_index": 0,
                    "explanation": f"Correct! {self.topic} helps us understand key principles!"
                },
                {
                    "question": "Which of these is a great way to learn new topics?",
                    "options": ["Asking questions & exploring visuals", "Ignoring the lesson", "Never practicing", "Guessing randomly"],
                    "correct_index": 0,
                    "explanation": "Asking questions and using visual diagrams makes learning easy!"
                },
                {
                    "question": "How do visual diagrams help our brain?",
                    "options": ["They help us see relationships clearly", "They make us confused", "They delete memories", "They don't help"],
                    "correct_index": 0,
                    "explanation": "Visuals help us connect concepts and remember them longer!"
                }
            ],
            "summary": [
                f"{self.topic} is an essential concept in {self.subject}.",
                "Visual diagrams help break down complex steps into simple parts.",
                "Practicing with quizzes locks in your learning superpowers!"
            ]
        }
