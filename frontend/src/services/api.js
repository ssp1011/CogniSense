// CogniSense — API Service
// Axios wrapper for backend communication
// TODO: Implement in Phase 6

import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
    headers: { "Content-Type": "application/json" },
});

// ── Capture ─────────────────────────────────────────
export const startCapture = (config) => api.post("/capture/start", config);
export const stopCapture = (sessionId) => api.post("/capture/stop", { session_id: sessionId });

// ── Live Load ───────────────────────────────────────
export const getLiveLoad = () => api.get("/load/live");
export const getLoadHistory = (limit = 100) => api.get(`/load/history?limit=${limit}`);

// ── Analysis ────────────────────────────────────────
export const analyzeInterview = () => api.post("/interview/analyze");
export const analyzeExam = () => api.post("/exam/analyze");

export default api;
