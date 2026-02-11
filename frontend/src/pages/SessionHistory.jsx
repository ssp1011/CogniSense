// CogniSense — Session History Page
import React, { useState } from "react";
import { formatDate, formatDuration, formatPercent } from "../utils/formatters";

// Demo data (in production: fetched from API)
const DEMO_SESSIONS = [
    {
        session_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        scenario: "coding",
        started_at: "2026-02-11T10:00:00Z",
        duration_sec: 1800,
        total_predictions: 1800,
        avg_load_score: 0.72,
        peak_load_level: "high",
    },
    {
        session_id: "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        scenario: "interview",
        started_at: "2026-02-10T14:30:00Z",
        duration_sec: 2700,
        total_predictions: 2700,
        avg_load_score: 0.85,
        peak_load_level: "high",
    },
    {
        session_id: "c3d4e5f6-a7b8-9012-cdef-123456789012",
        scenario: "exam",
        started_at: "2026-02-09T09:15:00Z",
        duration_sec: 3600,
        total_predictions: 3600,
        avg_load_score: 0.45,
        peak_load_level: "medium",
    },
];

function LoadBadge({ level }) {
    return (
        <span className={`load-level-badge ${level}`} style={{ fontSize: 11, padding: "3px 10px" }}>
            <span className="dot" style={{ animation: "none" }} />
            {level}
        </span>
    );
}

export default function SessionHistory() {
    const [sessions] = useState(DEMO_SESSIONS);
    const [selected, setSelected] = useState(null);

    return (
        <div className="fade-in">
            <div className="page-header">
                <h2>Session History</h2>
                <p>Review past cognitive load recordings</p>
            </div>

            <div className="glass-card" style={{ padding: 0, overflow: "hidden" }}>
                <table className="history-table">
                    <thead>
                        <tr>
                            <th>Session</th>
                            <th>Scenario</th>
                            <th>Date</th>
                            <th>Duration</th>
                            <th>Avg Load</th>
                            <th>Peak</th>
                            <th>Predictions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sessions.map((s) => (
                            <tr
                                key={s.session_id}
                                onClick={() => setSelected(s.session_id === selected ? null : s.session_id)}
                                style={{ cursor: "pointer", background: s.session_id === selected ? "rgba(10,132,255,0.08)" : undefined }}
                            >
                                <td style={{ fontFamily: "monospace", fontSize: 12 }}>
                                    {s.session_id.slice(0, 8)}…
                                </td>
                                <td style={{ textTransform: "capitalize" }}>{s.scenario}</td>
                                <td>{formatDate(s.started_at)}</td>
                                <td>{formatDuration(s.duration_sec)}</td>
                                <td>{formatPercent(s.avg_load_score)}</td>
                                <td><LoadBadge level={s.peak_load_level} /></td>
                                <td>{s.total_predictions.toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {sessions.length === 0 && (
                <div className="glass-card empty-state" style={{ marginTop: 16 }}>
                    <div className="empty-icon">📭</div>
                    <p>No sessions recorded yet. Start a capture on the Dashboard.</p>
                </div>
            )}

            {selected && (
                <div className="glass-card analysis-result" style={{ marginTop: 16 }}>
                    <div className="result-header">
                        <div>
                            <h3 style={{ fontSize: 16, fontWeight: 600 }}>Session Analysis</h3>
                            <p style={{ fontSize: 12, color: "var(--text-tertiary)", marginTop: 4 }}>
                                {selected.slice(0, 8)}…
                            </p>
                        </div>
                        <button className="btn btn-secondary" onClick={() => setSelected(null)}>
                            Close
                        </button>
                    </div>

                    <div className="time-distribution">
                        <div className="segment low" style={{ width: "30%" }} />
                        <div className="segment medium" style={{ width: "45%" }} />
                        <div className="segment high" style={{ width: "25%" }} />
                    </div>

                    <div style={{ display: "flex", gap: 24, marginTop: 12, fontSize: 12, color: "var(--text-secondary)" }}>
                        <span>🟢 Low 30%</span>
                        <span>🟡 Medium 45%</span>
                        <span>🔴 High 25%</span>
                    </div>

                    <div className="recommendations-list">
                        <div className="recommendation-item">
                            📊 Moderate cognitive load detected. Monitor for extended periods.
                        </div>
                        <div className="recommendation-item">
                            💡 Consider using the Pomodoro technique for longer sessions.
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
