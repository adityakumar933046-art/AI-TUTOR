/**
 * EduVerse AI Kids — Automated Integration & Unit Test Suite
 * Powered by Node.js Built-In Test Runner (`node --test`)
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const http = require('http');

let server;
const PORT = 3001;
const BASE_URL = `http://localhost:${PORT}`;

function makeRequest(method, path, body = null, token = null) {
    return new Promise((resolve, reject) => {
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const postData = body ? JSON.stringify(body) : null;
        if (postData) headers['Content-Length'] = Buffer.byteLength(postData);

        const req = http.request(`${BASE_URL}${path}`, { method, headers }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve({ status: res.statusCode, body: parsed });
                } catch (err) {
                    resolve({ status: res.statusCode, raw: data });
                }
            });
        });

        req.on('error', reject);
        if (postData) req.write(postData);
        req.end();
    });
}

describe('EduVerse AI Kids Enterprise Server Test Suite', () => {
    before(() => {
        return new Promise((resolve) => {
            process.env.PORT = PORT;
            const app = require('../server.js');
            server = app.listen(PORT, () => {
                console.log(`[Test Server] Running on ${BASE_URL}`);
                resolve();
            });
        });
    });

    after(() => {
        return new Promise((resolve) => {
            if (server) server.close(resolve);
            else resolve();
        });
    });

    // ----------------------------------------------------
    // 1. AUTHENTICATION & RBAC TESTS
    // ----------------------------------------------------
    describe('Authentication Module', () => {
        let studentToken = '';

        it('should login pre-seeded Demo Student successfully', async () => {
            const res = await makeRequest('POST', '/api/auth/login', {
                email: 'student@eduverse.ai',
                password: 'student123'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.strictEqual(res.body.user.role, 'Student');
            assert.ok(res.body.token);

            studentToken = res.body.token;
        });

        it('should reject login with wrong password', async () => {
            const res = await makeRequest('POST', '/api/auth/login', {
                email: 'student@eduverse.ai',
                password: 'wrongpassword'
            });

            assert.strictEqual(res.status, 401);
            assert.strictEqual(res.body.success, false);
        });

        it('should authenticate user with valid Bearer token', async () => {
            const res = await makeRequest('GET', '/api/auth/me', null, studentToken);

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.strictEqual(res.body.user.email, 'student@eduverse.ai');
        });

        it('should register a new Parent user account', async () => {
            const res = await makeRequest('POST', '/api/auth/register', {
                email: `parent_test_${Date.now()}@eduverse.ai`,
                password: 'parentpass123',
                name: 'Jane Doe',
                role: 'Parent'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.strictEqual(res.body.user.role, 'Parent');
        });
    });

    // ----------------------------------------------------
    // 2. 21-STAGE AI ORCHESTRATOR & SOCRATIC TUTOR TESTS
    // ----------------------------------------------------
    describe('21-Stage AI Orchestrator', () => {
        it('should process Socratic Math question without giving direct numerical answer', async () => {
            const res = await makeRequest('POST', '/api/ai/chat', {
                message: 'What is 7 times 8?',
                subject: 'math',
                hintLevel: 1
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.reply.length > 20);
            assert.strictEqual(res.body.agentName, 'Math Socratic Agent');
            assert.ok(res.body.hintLevelText);
        });

        it('should process Voice Tutor prompt and return SSML and spoken audio text', async () => {
            const res = await makeRequest('POST', '/api/ai/voice', {
                transcript: 'Why is the sky blue?',
                subject: 'science'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.spokenResponse);
            assert.ok(res.body.ssml.includes('<speak>'));
        });
    });

    // ----------------------------------------------------
    // 3. HOMEWORK OCR SCANNER TESTS
    // ----------------------------------------------------
    describe('Homework OCR Vision Scanner', () => {
        it('should extract worksheet problem and generate 3-step Socratic hint ladder', async () => {
            const res = await makeRequest('POST', '/api/ai/homework-scan', {
                filename: 'math_worksheet.png'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.extractedText);
            assert.strictEqual(res.body.socraticSteps.length, 3);
            assert.strictEqual(res.body.socraticSteps[0].level, 1);
        });
    });

    // ----------------------------------------------------
    // 4. STORY STUDIO & QUIZ ARENA TESTS
    // ----------------------------------------------------
    describe('Story Studio & Quiz Engine', () => {
        it('should generate interactive educational story with vocabulary list', async () => {
            const res = await makeRequest('POST', '/api/ai/generate-story', {
                theme: 'space'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.story.title);
            assert.ok(res.body.story.vocabulary.length >= 3);
            assert.ok(res.body.story.options.length >= 2);
        });

        it('should generate adaptive quiz question with explanation', async () => {
            const res = await makeRequest('POST', '/api/ai/generate-quiz', {
                subject: 'science'
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.quiz.question);
            assert.ok(res.body.quiz.options.length === 4);
        });
    });

    // ----------------------------------------------------
    // 5. PARENT & TEACHER DASHBOARD TESTS
    // ----------------------------------------------------
    describe('Parent & Teacher Analytics Modules', () => {
        it('should fetch Parent Analytics report metrics and recommendations', async () => {
            const res = await makeRequest('GET', '/api/parent/analytics');

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.weeklyStudyTimeHours > 0);
            assert.ok(res.body.subjectMastery.math);
            assert.ok(res.body.aiRecommendations.length >= 2);
        });

        it('should generate custom AI printable worksheet for Teachers', async () => {
            const res = await makeRequest('POST', '/api/teacher/worksheets', {
                topic: 'Multiplication',
                count: 5
            });

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.content.includes('EduVerse AI Kids'));
        });

        it('should retrieve Teacher class roster', async () => {
            const res = await makeRequest('GET', '/api/teacher/students');

            assert.strictEqual(res.status, 200);
            assert.strictEqual(res.body.success, true);
            assert.ok(res.body.roster.length >= 2);
        });
    });
});
