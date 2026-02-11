// CogniSense — Modality Breakdown Chart
// Per-modality contribution bars (Visual / Behavioral / Audio)
import React from "react";

const modalities = [
    { key: "visual", label: "Visual", icon: "👁️", className: "visual" },
    { key: "behavioral", label: "Behavioral", icon: "⌨️", className: "behavioral" },
    { key: "audio", label: "Audio", icon: "🎤", className: "audio" },
];

export default function ModalityChart({ scores }) {
    const data = scores || { visual: 0, behavioral: 0, audio: 0 };

    return (
        <div className="glass-card modality-bars">
            <div className="chart-title">
                <span>📶</span> Modality Breakdown
            </div>

            {modalities.map((m) => {
                const value = Math.round((data[m.key] || 0) * 100);
                return (
                    <div key={m.key} className={`modality-bar ${m.className}`}>
                        <div className="bar-header">
                            <span className="bar-label">
                                <span>{m.icon}</span> {m.label}
                            </span>
                            <span className="bar-value">{value}%</span>
                        </div>
                        <div className="bar-track">
                            <div
                                className="bar-fill"
                                style={{ width: `${value}%` }}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
