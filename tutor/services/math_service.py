import logging
from tutor.models import MathSession, MathSolution, ChatMessage
from tutor.services.gemini_service import GeminiTutorService

logger = logging.getLogger(__name__)

MATH_SYSTEM_INSTRUCTION = (
    "You are Sparky, an encouraging and expert AI Math Tutor for EduVerse AI Kids. "
    "Your goal is to solve mathematical expressions step-by-step with complete transparency. "
    "Never skip intermediate calculation steps. Use clear, formatted LaTeX math ($...$ for inline or $$...$$ for block math). "
    "Structure every solution with: "
    "1. Problem Statement "
    "2. Step-by-Step Breakdown (showing exact multiplication, division, or algebraic moves) "
    "3. Final Answer "
    "Also provide a guiding Socratic hint that helps a child learn how to solve the problem on their own."
)

class MathSolverService:
    def __init__(self, whiteboard):
        self.whiteboard = whiteboard
        self.chat_session = whiteboard.chat_session

    def solve_expression(self, expression_text):
        """
        Solves expression step-by-step using Gemini API and logs to MathSession & shared ChatMessage.
        """
        math_session = MathSession.objects.create(
            whiteboard=self.whiteboard,
            detected_expression=expression_text,
            status='solving'
        )

        gemini_service = GeminiTutorService(subject='Math')
        
        prompt = (
            f"Solve the following mathematical expression step-by-step for a student: '{expression_text}'.\n"
            f"{MATH_SYSTEM_INSTRUCTION}"
        )

        history = self.chat_session.messages.all() if self.chat_session else []
        res = gemini_service.generate_tutor_response(prompt, chat_history=history)
        explanation_text = res.get('response', f"Let's solve {expression_text} step-by-step!")

        # Generate a Socratic Hint
        hint_prompt = f"Give a 1-sentence helpful hint for solving '{expression_text}' without giving away the final number."
        hint_res = gemini_service.generate_tutor_response(hint_prompt, chat_history=[])
        hint_text = hint_res.get('response', "Try breaking down the problem into smaller numbers!")

        math_solution = MathSolution.objects.create(
            math_session=math_session,
            final_answer=expression_text,
            step_by_step_explanation=explanation_text,
            hint_text=hint_text
        )

        math_session.status = 'solved'
        math_session.save()

        # Log to shared ChatMessage history if chat_session exists
        if self.chat_session:
            ChatMessage.objects.create(
                session=self.chat_session,
                role='user',
                content=f"[Whiteboard Math Problem]: {expression_text}"
            )
            ChatMessage.objects.create(
                session=self.chat_session,
                role='model',
                content=explanation_text
            )

        return {
            "success": True,
            "math_session_id": math_session.id,
            "expression": expression_text,
            "solution_html": explanation_text,
            "hint_text": hint_text,
            "timestamp": math_solution.created_at.strftime('%H:%M')
        }

    def generate_hint(self, expression_text):
        gemini_service = GeminiTutorService(subject='Math')
        hint_prompt = (
            f"The student is working on this math problem: '{expression_text}'. "
            f"Provide a gentle guiding hint (Socratic question) to help them take the next step without revealing the final answer."
        )
        res = gemini_service.generate_tutor_response(hint_prompt, chat_history=[])
        return res.get('response', "Look closely at the numbers and try solving the first step!")
