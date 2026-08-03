/**
 * EduVerse AI Kids — Modular Application Frontend
 * Connected to Express Backend Server & 21-Stage AI Orchestrator
 */

// ==========================================
// 1. GLOBAL STATE & MEMORY ENGINE
// ==========================================
const EduVerseState = {
    user: null, // Logged in user account
    token: localStorage.getItem('eduverse_jwt_token') || null,
    student: {
        id: "std_1001",
        name: "Alex Johnson",
        age: 8,
        grade: "Grade 3",
        ageBracket: "7-9",
        xp: 250,
        coins: 45,
        streakDays: 3,
        confidenceScore: 0.65,
        masteryScores: { math: 75, science: 90, english: 82, reading: 88, space: 95 }
    },
    activeTab: 'learn',
    activeSubject: "math",
    activeProvider: "gemini", // gemini | groq | openrouter | ollama | openai
    hintLevel: 1,
    quizScore: 0,
    activeStoryTheme: "space",
    voiceModalInstance: null,
    authModalInstance: null,
    isListening: false,
    synth: window.speechSynthesis || null,
    recognition: null,
    currentAuthMode: 'login'
};

// ==========================================
// 2. SPECIALIZED AI AGENTS REGISTRY
// ==========================================
const AIAgentsRegistry = {
    math: { name: "Math Socratic Agent", icon: "🧮", desc: "Specialized in visual math steps, Socratic hints, and non-answer problem solving." },
    science: { name: "Science Explorer Agent", icon: "🔬", desc: "Specialized in nature, physics experiments, animals, and curious analogies." },
    english: { name: "English Grammar Coach", icon: "📝", desc: "Specialized in vocabulary, sentence structure, and word games." },
    reading: { name: "Reading & Phonics Coach", icon: "📖", desc: "Specialized in phonics sounds, pronunciation, and reading fluency." },
    space: { name: "Cosmic Space Voyager", icon: "🚀", desc: "Specialized in astronomy, planets, gravity, and cosmic mysteries." }
};

// ==========================================
// 3. API CLIENT SERVICE LAYER
// ==========================================
class APIClient {
    static async request(endpoint, options = {}) {
        const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
        if (EduVerseState.token) {
            headers['Authorization'] = `Bearer ${EduVerseState.token}`;
        }

        try {
            const res = await fetch(endpoint, { ...options, headers });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || `HTTP ${res.status}`);
            }
            return data;
        } catch (err) {
            console.warn(`[APIClient] Fetch to ${endpoint} failed, fallback triggered:`, err.message);
            throw err;
        }
    }
}

// ==========================================
// 4. INITIALIZATION & TAB SWITCHING
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('[EduVerse AI Kids] Application initializing...');
    
    // Check local session
    checkUserSession();

    // Initialize Chart.js
    initParentAnalyticsChart();

    // Setup Voice Recognition
    initSpeechRecognition();
});

function switchTab(tabName) {
    EduVerseState.activeTab = tabName;

    document.querySelectorAll('.app-view').forEach(view => view.classList.remove('active'));
    document.querySelectorAll('.nav-pills-custom .nav-link').forEach(btn => btn.classList.remove('active'));

    const targetView = document.getElementById(`view-${tabName}`);
    if (targetView) targetView.classList.add('active');

    const targetTabBtn = document.getElementById(`tab-${tabName}`);
    if (targetTabBtn) targetTabBtn.classList.add('active');

    if (tabName === 'parent') {
        loadParentAnalytics();
    } else if (tabName === 'teacher') {
        loadTeacherRoster();
    }
}

function setSubject(subjectKey) {
    EduVerseState.activeSubject = subjectKey;
    const agent = AIAgentsRegistry[subjectKey] || AIAgentsRegistry.math;

    // Update buttons UI
    const container = document.getElementById('subject-selector-buttons');
    if (container) {
        container.querySelectorAll('.btn-subject').forEach(btn => btn.classList.remove('active'));
        const activeBtn = Array.from(container.querySelectorAll('.btn-subject')).find(b => b.getAttribute('onclick')?.includes(subjectKey));
        if (activeBtn) activeBtn.classList.add('active');
    }

    // Update Agent Card
    document.getElementById('active-agent-icon').textContent = agent.icon;
    document.getElementById('active-agent-name').textContent = agent.name;
    document.getElementById('active-agent-desc').textContent = agent.desc;
    document.getElementById('chat-header-subject').textContent = `${agent.name} Session`;

    // Append subject switch banner in chat
    appendChatMessage('ai', `Switched subject to <strong>${agent.name} ${agent.icon}</strong>! Ask me any question!`, agent.name, 'Just now');
}

function selectProvider(providerKey) {
    EduVerseState.activeProvider = providerKey;
    const providerNames = {
        gemini: "Gemini (Free)",
        groq: "Groq (High-Speed)",
        openrouter: "OpenRouter",
        ollama: "Ollama (Offline)",
        openai: "OpenAI GPT-5.5"
    };
    document.getElementById('current-provider-name').textContent = providerNames[providerKey] || providerKey;
}

// ==========================================
// 5. AUTHENTICATION HANDLERS
// ==========================================
function openAuthModal() {
    if (!EduVerseState.authModalInstance) {
        EduVerseState.authModalInstance = new bootstrap.Modal(document.getElementById('authModal'));
    }
    EduVerseState.authModalInstance.show();
}

function switchAuthTab(mode) {
    EduVerseState.currentAuthMode = mode;
    const loginTab = document.getElementById('tab-auth-login');
    const regTab = document.getElementById('tab-auth-register');
    const nameGroup = document.getElementById('auth-name-group');
    const roleGroup = document.getElementById('auth-role-group');
    const submitBtn = document.getElementById('auth-submit-btn');

    if (mode === 'register') {
        loginTab.classList.remove('active');
        regTab.classList.add('active');
        nameGroup.classList.remove('d-none');
        roleGroup.classList.remove('d-none');
        submitBtn.textContent = 'Create EduVerse Account';
    } else {
        regTab.classList.remove('active');
        loginTab.classList.add('active');
        nameGroup.classList.add('d-none');
        roleGroup.classList.add('d-none');
        submitBtn.textContent = 'Sign In to EduVerse';
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;
    const name = document.getElementById('auth-name').value;
    const role = document.getElementById('auth-role').value;

    const endpoint = EduVerseState.currentAuthMode === 'register' ? '/api/auth/register' : '/api/auth/login';
    const payload = EduVerseState.currentAuthMode === 'register' ? { email, password, name, role } : { email, password };

    try {
        const data = await APIClient.request(endpoint, { method: 'POST', body: JSON.stringify(payload) });
        if (data.success) {
            EduVerseState.token = data.token;
            localStorage.setItem('eduverse_jwt_token', data.token);
            EduVerseState.user = data.user;
            
            updateUserNavArea(data.user);
            if (EduVerseState.authModalInstance) EduVerseState.authModalInstance.hide();
            
            alert(`Welcome ${data.user.name}! Logged in successfully as ${data.user.role}.`);
        }
    } catch (err) {
        alert(`Authentication Failed: ${err.message}`);
    }
}

async function quickLogin(email, password) {
    document.getElementById('auth-email').value = email;
    document.getElementById('auth-password').value = password;
    switchAuthTab('login');
    openAuthModal();
    const fakeEvent = { preventDefault: () => {} };
    await handleAuthSubmit(fakeEvent);
}

async function checkUserSession() {
    if (!EduVerseState.token) return;
    try {
        const data = await APIClient.request('/api/auth/me');
        if (data.success) {
            EduVerseState.user = data.user;
            updateUserNavArea(data.user);
        }
    } catch (err) {
        console.log('[Auth] Session check failed, clearing token');
        localStorage.removeItem('eduverse_jwt_token');
        EduVerseState.token = null;
    }
}

function updateUserNavArea(user) {
    const area = document.getElementById('nav-user-area');
    if (!area) return;

    if (user) {
        area.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <span class="badge bg-primary-subtle text-primary rounded-pill px-3 py-2 fw-bold">
                    <i class="fa-solid fa-user-circle me-1"></i> ${user.name} (${user.role})
                </span>
                <button class="btn btn-sm btn-outline-danger rounded-circle p-2" onclick="logoutUser()" title="Logout">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        `;
    } else {
        area.innerHTML = `
            <button class="btn btn-gradient-primary rounded-pill btn-sm px-3 fw-bold" onclick="openAuthModal()">
                <i class="fa-solid fa-user-lock me-1"></i> Login / Register
            </button>
        `;
    }
}

function logoutUser() {
    localStorage.removeItem('eduverse_jwt_token');
    EduVerseState.token = null;
    EduVerseState.user = null;
    updateUserNavArea(null);
    alert('Logged out successfully.');
}

// ==========================================
// 6. SOCRATIC CHAT TUTOR LOGIC
// ==========================================
async function handleChatSubmit(e) {
    e.preventDefault();
    const inputEl = document.getElementById('chat-input');
    const userText = inputEl.value.trim();
    if (!userText) return;

    inputEl.value = '';
    appendChatMessage('user', userText, 'Alex (You)', 'Just now');

    // Show Typing Indicator
    const typingId = appendTypingIndicator();

    try {
        const payload = {
            message: userText,
            subject: EduVerseState.activeSubject,
            hintLevel: EduVerseState.hintLevel,
            provider: EduVerseState.activeProvider
        };

        let data;
        try {
            data = await APIClient.request('/api/ai/chat', { method: 'POST', body: JSON.stringify(payload) });
        } catch (err) {
            // Client-side Socratic Fallback
            data = {
                reply: `That's a super question! 🌟 Let's solve it together step-by-step. What is the very first thing you notice about "${userText}"?`,
                agentName: AIAgentsRegistry[EduVerseState.activeSubject].name,
                hintLevelText: "Level 1 (Concept Explanation)",
                confidenceScore: 70,
                providerUsed: "Client Fallback Socratic Engine"
            };
        }

        removeTypingIndicator(typingId);

        appendChatMessage('ai', data.reply, `${data.agentName} (Sparky)`, 'Just now');

        if (data.hintLevelText) {
            document.getElementById('hint-level-text').textContent = data.hintLevelText;
        }
        if (data.confidenceScore) {
            document.getElementById('confidence-badge').textContent = `Learner Confidence: ${data.confidenceScore}%`;
        }

        // Award XP
        awardXP(5, 1);

    } catch (err) {
        removeTypingIndicator(typingId);
        appendChatMessage('ai', `I am thinking deeply about that! Can you tell me what step you'd like to start with?`, 'Sparky', 'Just now');
    }
}

function appendChatMessage(type, text, senderName, timeStr) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const wrapper = document.createElement('div');
    wrapper.className = `chat-bubble ${type === 'user' ? 'user-bubble ms-auto' : 'ai-bubble'} d-flex gap-3 mb-4`;

    wrapper.innerHTML = `
        <div class="chat-avatar">${type === 'user' ? '👦' : '🤖'}</div>
        <div class="chat-content">
            <div class="chat-sender">${senderName}</div>
            <div class="chat-text">${text}</div>
            <div class="chat-time mt-1">${timeStr}</div>
        </div>
    `;

    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const id = `typing-${Date.now()}`;
    const wrapper = document.createElement('div');
    wrapper.id = id;
    wrapper.className = 'chat-bubble ai-bubble d-flex gap-3 mb-4';
    wrapper.innerHTML = `
        <div class="chat-avatar">🤖</div>
        <div class="chat-content">
            <div class="chat-text"><i class="fa-solid fa-circle-notch fa-spin me-2 text-primary"></i> Sparky is formulating a Socratic hint...</div>
        </div>
    `;
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function clearChatHistory() {
    const container = document.getElementById('chat-messages');
    container.innerHTML = `
        <div class="chat-bubble ai-bubble d-flex gap-3 mb-4">
            <div class="chat-avatar">🤖</div>
            <div class="chat-content">
                <div class="chat-sender">Sparky (Math Agent)</div>
                <div class="chat-text">Session reset! What new question shall we explore today? 🚀</div>
                <div class="chat-time mt-1">Just now</div>
            </div>
        </div>
    `;
}

function quickPractice(topic) {
    switchTab('learn');
    document.getElementById('chat-input').value = `Help me practice ${topic} step-by-step!`;
    const fakeEvent = { preventDefault: () => {} };
    handleChatSubmit(fakeEvent);
}

// ==========================================
// 7. VOICE TUTOR MODAL & SPEECH RECOGNITION
// ==========================================
function toggleVoiceModal() {
    if (!EduVerseState.voiceModalInstance) {
        EduVerseState.voiceModalInstance = new bootstrap.Modal(document.getElementById('voiceModal'));
    }
    EduVerseState.voiceModalInstance.show();
    startVoiceSession();
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        EduVerseState.recognition = new SpeechRecognition();
        EduVerseState.recognition.continuous = false;
        EduVerseState.recognition.interimResults = false;
        EduVerseState.recognition.lang = 'en-US';

        EduVerseState.recognition.onresult = async (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('voice-transcript-text').textContent = `You said: "${transcript}"`;
            document.getElementById('voice-status-text').textContent = "Thinking...";

            try {
                const data = await APIClient.request('/api/ai/voice', {
                    method: 'POST',
                    body: JSON.stringify({ transcript, subject: EduVerseState.activeSubject })
                });

                document.getElementById('voice-status-text').textContent = "Sparky Speaking!";
                document.getElementById('voice-transcript-text').textContent = data.spokenResponse;

                speakText(data.spokenResponse);
            } catch (err) {
                const fallbackReply = `That's great! Let's think about how to solve "${transcript}" together!`;
                document.getElementById('voice-status-text').textContent = "Sparky Speaking!";
                document.getElementById('voice-transcript-text').textContent = fallbackReply;
                speakText(fallbackReply);
            }
        };

        EduVerseState.recognition.onerror = () => {
            document.getElementById('voice-status-text').textContent = "Listening paused.";
        };
    }
}

function startVoiceSession() {
    if (EduVerseState.recognition) {
        try {
            EduVerseState.recognition.start();
            EduVerseState.isListening = true;
            document.getElementById('voice-status-text').textContent = "Listening to you...";
        } catch (e) {}
    }
}

function stopVoiceSession() {
    if (EduVerseState.recognition) {
        EduVerseState.recognition.stop();
        EduVerseState.isListening = false;
        document.getElementById('voice-status-text').textContent = "Session Paused";
    }
}

function speakText(text) {
    if (EduVerseState.synth) {
        EduVerseState.synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.pitch = 1.2;
        utterance.rate = 0.95;
        EduVerseState.synth.speak(utterance);
    }
}

// ==========================================
// 8. HOMEWORK OCR SCANNER
// ==========================================
function triggerFileInput() {
    document.getElementById('homework-file-input').click();
}

async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const stepsContainer = document.getElementById('socratic-ocr-steps');
    stepsContainer.innerHTML = `<p class="text-primary"><i class="fa-solid fa-spinner fa-spin me-2"></i> Analyzing worksheet with Vision OCR...</p>`;

    try {
        const data = await APIClient.request('/api/ai/homework-scan', {
            method: 'POST',
            body: JSON.stringify({ filename: file.name })
        });

        document.getElementById('ocr-extracted-box').classList.remove('d-none');
        document.getElementById('ocr-text-result').textContent = data.extractedText;

        stepsContainer.innerHTML = data.socraticSteps.map(step => `
            <div class="p-3 bg-light-custom rounded-4 mb-2 border">
                <h6 class="fw-bold text-primary mb-1">Step ${step.level} Hint:</h6>
                <p class="mb-0 fs-7">${step.text}</p>
            </div>
        `).join('');

        awardXP(15, 3);
    } catch (err) {
        stepsContainer.innerHTML = `<p class="text-danger">Failed to scan homework image.</p>`;
    }
}

// ==========================================
// 9. STORY STUDIO LOGIC
// ==========================================
function selectStoryTheme(theme) {
    EduVerseState.activeStoryTheme = theme;
    const container = document.getElementById('story-theme-buttons');
    if (container) {
        container.querySelectorAll('.btn-theme').forEach(btn => btn.classList.remove('active'));
        const activeBtn = Array.from(container.querySelectorAll('.btn-theme')).find(b => b.getAttribute('onclick')?.includes(theme));
        if (activeBtn) activeBtn.classList.add('active');
    }
}

async function generateNewStory() {
    try {
        const data = await APIClient.request('/api/ai/generate-story', {
            method: 'POST',
            body: JSON.stringify({ theme: EduVerseState.activeStoryTheme })
        });

        const story = data.story;
        document.getElementById('story-title').textContent = story.title;
        document.getElementById('story-body-text').textContent = story.body;
        document.getElementById('story-vocabulary-count').textContent = `${story.vocabulary.length} Vocab Words`;
        document.getElementById('story-question').textContent = story.question;

        const optionsContainer = document.getElementById('story-options');
        optionsContainer.innerHTML = story.options.map(opt => `
            <button class="btn btn-outline-custom rounded-pill px-3" onclick="checkStoryAnswer(${opt.correct})">${opt.text}</button>
        `).join('');

        awardXP(10, 2);
    } catch (err) {
        alert('Failed to generate story.');
    }
}

function checkStoryAnswer(isCorrect) {
    if (isCorrect) {
        alert('🎉 Correct! Excellent reading comprehension! +20 XP');
        awardXP(20, 5);
    } else {
        alert('💡 Close! Re-read the passage to find the clue!');
    }
}

function readStoryAloud() {
    const text = document.getElementById('story-body-text').textContent;
    speakText(text);
}

// ==========================================
// 10. QUIZ ARENA LOGIC
// ==========================================
async function selectQuizAnswer(btn, isCorrect) {
    const feedbackBox = document.getElementById('quiz-feedback');
    feedbackBox.classList.remove('d-none');

    if (isCorrect) {
        btn.classList.add('btn-success');
        feedbackBox.className = 'quiz-feedback-box p-3 rounded-4 bg-success-subtle text-success border border-success mb-3';
        feedbackBox.innerHTML = '<strong>🎉 Fantastic Job!</strong> +15 XP Earned!';
        awardXP(15, 3);
    } else {
        btn.classList.add('btn-danger');
        feedbackBox.className = 'quiz-feedback-box p-3 rounded-4 bg-warning-subtle text-warning border border-warning mb-3';
        feedbackBox.innerHTML = '<strong>💡 Good try!</strong> Remember: Socratic practice helps master it!';
    }

    setTimeout(async () => {
        try {
            const data = await APIClient.request('/api/ai/generate-quiz', {
                method: 'POST',
                body: JSON.stringify({ subject: EduVerseState.activeSubject })
            });
            const q = data.quiz;
            document.getElementById('quiz-question-text').textContent = q.question;
            document.getElementById('quiz-subject-tag').textContent = `Subject: ${q.subject}`;

            const container = document.getElementById('quiz-options-container');
            container.innerHTML = q.options.map(opt => `
                <div class="col-md-6"><button class="btn btn-quiz-option w-100 py-3 rounded-4 fw-bold" onclick="selectQuizAnswer(this, ${opt.correct})">${opt.text}</button></div>
            `).join('');

            feedbackBox.classList.add('d-none');
        } catch (e) {}
    }, 1800);
}

// ==========================================
// 11. PARENT & TEACHER DASHBOARDS
// ==========================================
let masteryChartInstance = null;

function initParentAnalyticsChart() {
    const canvas = document.getElementById('parent-chart-mastery');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    masteryChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Math', 'Science', 'English', 'Reading', 'Space'],
            datasets: [{
                label: 'Mastery Level (%)',
                data: [75, 90, 82, 88, 95],
                backgroundColor: ['#6c5ce7', '#00b894', '#0984e3', '#fd79a8', '#fdcb6e'],
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}

async function loadParentAnalytics() {
    try {
        const data = await APIClient.request('/api/parent/analytics');
        if (data.subjectMastery && masteryChartInstance) {
            masteryChartInstance.data.datasets[0].data = Object.values(data.subjectMastery);
            masteryChartInstance.update();
        }
    } catch (e) {}
}

async function generateWorksheet(e) {
    e.preventDefault();
    const topic = document.getElementById('ws-topic').value;
    const count = document.getElementById('ws-count').value;

    try {
        const data = await APIClient.request('/api/teacher/worksheets', {
            method: 'POST',
            body: JSON.stringify({ topic, count })
        });

        document.getElementById('worksheet-preview-box').classList.remove('d-none');
        document.getElementById('worksheet-text-content').textContent = data.content;
    } catch (err) {
        alert('Worksheet generation failed.');
    }
}

async function loadTeacherRoster() {
    try {
        const data = await APIClient.request('/api/teacher/students');
        const body = document.getElementById('teacher-roster-body');
        if (body && data.roster) {
            body.innerHTML = data.roster.map(std => `
                <tr>
                    <td>👦 ${std.name}</td>
                    <td>${std.grade}</td>
                    <td><span class="badge bg-success">${std.mastery || '85%'}</span></td>
                    <td>🔥 ${std.streakDays} Days</td>
                </tr>
            `).join('');
        }
    } catch (e) {}
}

// ==========================================
// 12. GAMIFICATION HELPER
// ==========================================
function awardXP(amount, coins) {
    EduVerseState.student.xp += amount;
    EduVerseState.student.coins += coins;

    document.getElementById('stat-xp').innerHTML = `<i class="fa-solid fa-star text-warning me-1"></i> ${EduVerseState.student.xp} XP`;
    document.getElementById('stat-coins').innerHTML = `<i class="fa-solid fa-coins text-warning me-1"></i> ${EduVerseState.student.coins} Coins`;
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
}

function exportParentReport() {
    alert('📄 Exporting Alex Johnson\'s Weekly Progress Report PDF...');
}
