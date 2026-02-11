// CogniSense — Dashboard Page
import React, { useEffect, useState } from "react";
import CognitiveLoadMeter from "../components/CognitiveLoadMeter";
import ModalityChart from "../components/ModalityChart";
import StressTimeline from "../components/StressTimeline";
import AlertsPanel from "../components/AlertsPanel";
import useWebSocket from "../hooks/useWebSocket";
import { formatDuration } from "../utils/formatters";

export default function Dashboard({ isActive, session, onStart, onStop, loading }) {
    const [scenario, setScenario] = useState("general");
    const [elapsed, setElapsed] = useState(0);
    const ws = useWebSocket(isActive);

    // Timer
    useEffect(() => {
        if (!isActive) { setElapsed(0); return; }
        const start = Date.now();
        const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);
        return () => clearInterval(timer);
    }, [isActive]);

    // Connect/disconnect websocket with session
    useEffect(() => {
        if (isActive) ws.connect();
        else ws.disconnect();
    }, [isActive]); // connect/disconnect with session state

    const currentData = ws.data || {
        load_level: "low",
        confidence: 0,
        modality_scores: { visual: 0, behavioral: 0, audio: 0 },
        probabilities: { low: 0.33, medium: 0.34, high: 0.33 },
    };

    const recommendations = [];
    if (currentData.load_level === "high") {
        recommendations.push("⚠️ High cognitive load detected — consider taking a short break.");
    }
    if (currentData.modality_scores?.visual > 0.5) {
        recommendations.push("👁️ Visual stress is elevated — reduce screen brightness.");
    }
    if (currentData.modality_scores?.audio > 0.5) {
        recommendations.push("🎤 Voice stress detected — slow down your speech.");
    }
    if (currentData.load_level === "low" && isActive) {
        recommendations.push("✅ Cognitive load is healthy — performance is sustainable.");
    }
    if (!isActive) {
        recommendations.push("📊 Start a capture session to receive real-time recommendations.");
    }

    return (
        <div className="fade-in">
            {/* Header + Controls */}
            <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                    <h2>Dashboard</h2>
                    <p>Real-time cognitive load monitoring</p>
                </div>
                <div className="session-controls">
                    {!isActive && (
                        <select
                            className="scenario-select"
                            value={scenario}
                            onChange={(e) => setScenario(e.target.value)}
                        >
                            <option value="general">General</option>
                            <option value="coding">Coding</option>
                            <option value="exam">Exam</option>
                            <option value="interview">Interview</option>
                        </select>
                    )}

                    {isActive ? (
                        <button className="btn btn-danger" onClick={onStop} disabled={loading}>
                            ⏹ Stop Session
                        </button>
                    ) : (
                        <button
                            className="btn btn-primary"
                            onClick={() => onStart(scenario)}
                            disabled={loading}
                        >
                            ▶ Start Session
                        </button>
                    )}
                </div>
            </div>

            {/* Metrics Row */}
            <div className="metrics-grid">
                <div className="glass-card metric-card">
                    <div className="metric-label">Status</div>
                    <div className="metric-value" style={{ fontSize: 24, color: isActive ? "var(--accent-green)" : "var(--text-tertiary)" }}>
                        {isActive ? "Recording" : "Idle"}
                    </div>
                    <div className="metric-sub">
                        {isActive ? `Scenario: ${scenario}` : "No active session"}
                    </div>
                </div>
                <div className="glass-card metric-card">
                    <div className="metric-label">Duration</div>
                    <div className="metric-value">{formatDuration(elapsed)}</div>
                    <div className="metric-sub">Elapsed time</div>
                </div>
                <div className="glass-card metric-card">
                    <div className="metric-label">Predictions</div>
                    <div className="metric-value">{ws.history.length}</div>
                    <div className="metric-sub">Total readings</div>
                </div>
                <div className="glass-card metric-card">
                    <div className="metric-label">WebSocket</div>
                    <div className="metric-value" style={{ fontSize: 24, color: ws.isConnected ? "var(--accent-green)" : "var(--text-tertiary)" }}>
                        {ws.isConnected ? "Connected" : "Offline"}
                    </div>
                    <div className="metric-sub">1 Hz stream</div>
                </div>
            </div>

            {/* Main Grid */}
            <div className="charts-grid">
                <CognitiveLoadMeter
                    loadLevel={currentData.load_level}
                    confidence={currentData.confidence}
                />
                <ModalityChart scores={currentData.modality_scores} />
            </div>

            {/* Timeline */}
            <StressTimeline history={ws.history} />

            {/* Alerts */}
            <div style={{ marginTop: 16 }}>
                <AlertsPanel recommendations={recommendations} />
            </div>
        </div>
    );
}
