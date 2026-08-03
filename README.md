# EduVerse AI Kids 🚀🧠
### Next-Generation AI-Powered Learning Platform for Children (K-8)

**EduVerse AI Kids** is a production-ready, full-stack AI educational technology platform built to transform learning into an interactive, gamified, and highly adaptive experience. Powered by the **Gemini 1.5 API**, Django 5.x, and FastAPI, EduVerse AI Kids integrates multi-modal tutoring across voice, text, interactive whiteboards, visual diagrams, homework scanning OCR, speech pronunciation, roleplay conversations, and AI game generation.

---

## 🌟 Key Features Across All 12 Phases

1. **Authentication & RBAC System (Phase 1)**:
   - Role-Based Access Control supporting **Student**, **Parent**, and **Admin** roles.
   - Dual-login (Username or Email), Remember Me session persistence, email verification, Google OAuth, and audit logging.

2. **AI Chat Tutor (Phase 2)**:
   - Subject-tuned Socratic AI Tutor powered by Gemini API across Math, Science, English, History, Geography, Coding, and Reasoning.

3. **Human Voice AI Tutor (Phase 3)**:
   - Voice-to-voice interactive speech tutor supporting Push-to-Talk, Hold-to-Talk, and Continuous Mode with multi-lingual STT/TTS (English, Hindi, Hinglish).

4. **AI Whiteboard & Smart Math Workspace (Phase 4)**:
   - Interactive HTML5 canvas with freehand drawing, geometry tools, step-by-step math solver, and Socratic hint engine.

5. **AI Visual Learning Engine (Phase 5)**:
   - Dynamic visual lesson generator rendering Mermaid.js flowcharts, mind maps, cycle diagrams, and mini-quizzes.

6. **AI Homework Scanner & Document Intelligence (Phase 6)**:
   - Drag-and-drop OCR image scanner detecting questions, producing step-by-step solutions, and generating targeted practice worksheets.

7. **AI Reading Coach & Pronunciation Assessment (Phase 7)**:
   - Real-time speech alignment engine evaluating Words Per Minute (WPM), accuracy %, fluency %, mispronounced words, and phoneme hints.

8. **AI Speaking Coach & Conversation Simulator (Phase 8)**:
   - Roleplay scenario engine (Restaurant, Doctor, School, Airport) providing real-time grammar, vocabulary, and confidence feedback.

9. **AI Game Engine & Gamification Platform (Phase 9)**:
   - Dynamically generated learning games (Match-Pair, Memory Cards, Drag-and-Drop Bins) with XP, Coins, Badges, Store, Missions, and Leaderboards.

10. **Parent Dashboard & Smart Notification Engine (Phase 10)**:
    - Comprehensive parental oversight with daily study plans, subject progress breakdowns, and multi-channel notifications (In-App, SMS, WhatsApp, Email).

11. **AI Learning Memory & Personal Learning Brain (Phase 11)**:
    - Persistent student memory profile tracking skill trees, concept node mastery (`not_started`, `learning`, `practicing`, `mastered`, `revision_needed`), SuperMemo spaced repetition (1, 3, 7, 14, 30 days), and adaptive curriculum sequences.

12. **Admin Dashboard, System Monitoring & Infrastructure (Phase 12)**:
    - Full system oversight (Total Students, Parents, CPU, RAM, DB, Redis, Gemini API status), User Management (Suspend/Activate, Reset Password), Content Management, Global Search Engine, `/health/` status endpoints, Docker multi-stage build, and Nginx reverse proxy.

---

## 🏗️ System Architecture

```
                                +-----------------------------------+
                                |     Nginx Reverse Proxy (:80)     |
                                +-----------------+-----------------+
                                                  |
                        +-------------------------+-------------------------+
                        |                                                   |
                        v                                                   v
        +---------------+---------------+                   +---------------+---------------+
        |    Django Web Server (:8000)   |                   |    FastAPI Microservice (:8001)|
        |  - Auth & RBAC (Student/Parent)|                   |  - AI Engine Endpoints        |
        |  - Tutor Services & Views     |                   |  - Analytics & Dashboard APIs |
        |  - Admin Dashboard & Search   |                   |  - System Health Checks       |
        +---------------+---------------+                   +---------------+---------------+
                        |                                                   |
                        +-------------------------+-------------------------+
                                                  |
                                                  v
                                +-----------------+-----------------+
                                |        Gemini 1.5 Flash API       |
                                +-----------------------------------+
```

---

## 🚀 Quick Start Guide (Local Development)

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/eduverse/eduverse_ai_kids.git
cd eduverse_ai_kids
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
DEBUG=1
SECRET_KEY=your_development_secret_key
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Database Migrations & Initial Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Local Servers
- **Django Application**:
  ```bash
  python manage.py runserver 8000
  ```
- **FastAPI Microservice**:
  ```bash
  uvicorn ai_service.main:app --port 8001 --reload
  ```

Visit `http://127.0.0.1:8000/` in your browser!

---

## 🐳 Docker Production Deployment

To run the entire stack (Django, FastAPI, PostgreSQL, Redis, Celery, Nginx) using Docker Compose:

```bash
docker-compose up -d --build
```

Access the application at `http://localhost/` and the health check at `http://localhost/health/`.

---

## 🧪 Running Unit & Integration Tests

```bash
# Run Tutor & AI Engine Unit Tests (48 Tests)
python manage.py test tutor

# Run Accounts & Auth Tests (9 Tests)
python manage.py test accounts
```

Total Test Suite: **57 out of 57 Unit Tests Passing Cleanly (`OK`)**.

---

## 📜 License & Acknowledgments

Built for portfolio demonstrations, hackathons, and real-world educational technology deployment. Powered by Google DeepMind's **Gemini API**.
