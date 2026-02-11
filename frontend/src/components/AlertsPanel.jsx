// CogniSense — Alerts Panel
// Real-time recommendations and alerts
import React from "react";

function classifyAlert(text) {
    if (text.includes("✅")) return "success";
    if (text.includes("🔴") || text.includes("⚠️")) return "danger";
    if (text.includes("👁️") || text.includes("⌨️") || text.includes("🎤") || text.includes("💡") || text.includes("🗣️")) return "warning";
    return "info";
}

export default function AlertsPanel({ recommendations = [] }) {
    if (recommendations.length === 0) {
        return (
            <div className="glass-card alerts-list">
                <div className="chart-title">
                    <span>🔔</span> Recommendations
                </div>
                <div className="empty-state" style={{ padding: "24px 16px" }}>
                    <p>No alerts yet — start a capture session</p>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-card alerts-list">
            <div className="chart-title">
                <span>🔔</span> Recommendations
            </div>
            {recommendations.map((rec, i) => (
                <div key={i} className={`alert-item ${classifyAlert(rec)}`}>
                    {rec}
                </div>
            ))}
        </div>
    );
}
