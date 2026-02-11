// CogniSense — API Service
// Axios wrapper for backend communication

import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
    headers: { "Content-Type": "application/json" },
});

// ── Capture ─────────────────────────────────────────
export const startCapture = (scenario = "general", notes = "") =>
    api.post("/capture/start", { scenario, notes });

export const stopCapture = (sessionId) =>
    api.post("/capture/stop", { session_id: sessionId });

export const getSessionStatus = () => api.get("/capture/status");

// ── Live Load ───────────────────────────────────────
export const getLiveLoad = () => api.get("/load/live");

export const getLoadHistory = (sessionId, limit = 100) =>
    api.get(`/load/history?session_id=${sessionId}&limit=${limit}`);

// ── Analysis ────────────────────────────────────────
export const analyzeInterview = (sessionId) =>
    api.post(`/interview/analyze?session_id=${sessionId}`);

export const analyzeExam = (sessionId) =>
    api.post(`/exam/analyze?session_id=${sessionId}`);

export default api;
