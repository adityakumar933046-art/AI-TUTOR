import json
from tutor.models import (
    Homework, HomeworkFile, OCRResult, DetectedQuestion,
    HomeworkAnalysis, PracticeQuestion, HomeworkHistory, ChatSession, ChatMessage
)
from tutor.services.ocr_service import OCRVisionService
from tutor.services.document_service import DocumentParserService
from tutor.services.practice_generator import PracticeGeneratorService

class HomeworkManagerService:
    def __init__(self, student):
        self.student = student

    def process_and_create_homework(self, uploaded_file=None, raw_text=""):
        chat_session = ChatSession.objects.filter(student=self.student).first()
        if not chat_session:
            chat_session = ChatSession.objects.create(
                student=self.student,
                subject='General Knowledge',
                title="Homework Discussion"
            )

        homework = Homework.objects.create(
            student=self.student,
            chat_session=chat_session,
            title=uploaded_file.name if uploaded_file else "Scanned Homework Document",
            status='processing'
        )

        if uploaded_file:
            HomeworkFile.objects.create(
                homework=homework,
                file_obj=uploaded_file,
                file_type='pdf' if uploaded_file.name.endswith('.pdf') else 'image',
                original_filename=uploaded_file.name
            )

        # Step 1: Perform Vision OCR & Cleaning
        ocr_service = OCRVisionService(raw_text_or_prompt=raw_text or (uploaded_file.name if uploaded_file else "Worksheet"))
        ocr_data = ocr_service.extract_and_clean_text()

        OCRResult.objects.create(
            homework=homework,
            extracted_text=ocr_data['raw_text'],
            cleaned_text=ocr_data['cleaned_text'],
            confidence_score=ocr_data['confidence_score']
        )

        # Step 2: Document Parsing & Question Detection
        doc_parser = DocumentParserService(cleaned_ocr_text=ocr_data['cleaned_text'])
        parsed_doc = doc_parser.parse_document_questions()

        homework.subject = parsed_doc.get('subject', 'General Knowledge')
        homework.difficulty_level = parsed_doc.get('overall_difficulty', 'Medium')
        homework.status = 'analyzed'
        homework.save()

        HomeworkAnalysis.objects.create(
            homework=homework,
            summary_overview=parsed_doc.get('summary_overview', 'Scanned homework parsed successfully.')
        )

        # Step 3: Create Detected Question records & Practice Questions
        for q_item in parsed_doc.get('questions', []):
            q_obj = DetectedQuestion.objects.create(
                homework=homework,
                question_number=q_item.get('number', 1),
                question_text=q_item.get('question_text', ''),
                subject_tag=q_item.get('subject_tag', homework.subject),
                difficulty=q_item.get('difficulty', 'Medium'),
                step_by_step_solution=q_item.get('solution_explanation', ''),
                hint_text=q_item.get('hint_text', '')
            )

            # Generate similar practice set for each question
            pg_service = PracticeGeneratorService(question_text=q_obj.question_text, subject=q_obj.subject_tag)
            practice_list = pg_service.generate_practice_set()

            for p_item in practice_list:
                PracticeQuestion.objects.create(
                    question=q_obj,
                    difficulty=p_item.get('difficulty', 'Medium'),
                    question_text=p_item.get('question_text', ''),
                    options_json=json.dumps(p_item.get('options', [])),
                    correct_index=p_item.get('correct_index', 0),
                    explanation=p_item.get('explanation', '')
                )

        HomeworkHistory.objects.create(
            student=self.student,
            homework=homework
        )

        # Log to shared ChatMessage history
        ChatMessage.objects.create(
            session=chat_session,
            role='user',
            content=f"[Scanned Homework Uploaded]: {homework.title}"
        )
        ChatMessage.objects.create(
            session=chat_session,
            role='model',
            content=f"I analyzed your homework on {homework.subject}! Detected {homework.questions.count()} questions with step-by-step solutions and practice problems."
        )

        return homework
