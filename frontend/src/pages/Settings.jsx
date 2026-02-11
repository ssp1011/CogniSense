// CogniSense — Settings Page
import React, { useState } from "react";

function Toggle({ on, onChange }) {
    return (
        <button className={`toggle ${on ? "on" : ""}`} onClick={() => onChange(!on)}>
            <div className="toggle-knob" />
        </button>
    );
}

export default function Settings() {
    const [settings, setSettings] = useState({
        webcam: true,
        audio: true,
        keystroke: true,
        mouse: true,
        notifications: true,
        autoRecord: false,
        darkMode: true,
    });

    const update = (key) => (val) => setSettings({ ...settings, [key]: val });

    const groups = [
        {
            title: "Capture Sensors",
            items: [
                { key: "webcam", label: "Webcam", desc: "Face mesh & eye tracking" },
                { key: "audio", label: "Audio", desc: "Voice stress analysis" },
                { key: "keystroke", label: "Keystroke", desc: "Typing pattern analysis" },
                { key: "mouse", label: "Mouse", desc: "Movement & click tracking" },
            ],
        },
        {
            title: "Preferences",
            items: [
                { key: "notifications", label: "Notifications", desc: "Alert when load is high" },
                { key: "autoRecord", label: "Auto-Record", desc: "Start recording on app launch" },
                { key: "darkMode", label: "Dark Mode", desc: "macOS dark appearance" },
            ],
        },
    ];

    return (
        <div className="fade-in">
            <div className="page-header">
                <h2>Settings</h2>
                <p>Configure sensors and preferences</p>
            </div>

            {groups.map((group) => (
                <div key={group.title} className="glass-card settings-group" style={{ padding: "16px 24px", marginBottom: 16 }}>
                    <h3>{group.title}</h3>
                    {group.items.map((item) => (
                        <div key={item.key} className="setting-row">
                            <div>
                                <div className="setting-label">{item.label}</div>
                                <div className="setting-desc">{item.desc}</div>
                            </div>
                            <Toggle on={settings[item.key]} onChange={update(item.key)} />
                        </div>
                    ))}
                </div>
            ))}

            {/* API Config */}
            <div className="glass-card" style={{ padding: "16px 24px" }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>API Configuration</h3>
                <div className="setting-row">
                    <div>
                        <div className="setting-label">Backend URL</div>
                        <div className="setting-desc">http://localhost:8000/api/v1</div>
                    </div>
                    <div className="status-indicator">
                        <span className="status-dot live" />
                        <span style={{ color: "var(--accent-green)" }}>Connected</span>
                    </div>
                </div>
                <div className="setting-row" style={{ borderBottom: "none" }}>
                    <div>
                        <div className="setting-label">WebSocket</div>
                        <div className="setting-desc">ws://localhost:8000/api/v1/ws/load</div>
                    </div>
                    <div className="status-indicator">
                        <span className="status-dot live" />
                        <span style={{ color: "var(--accent-green)" }}>Streaming</span>
                    </div>
                </div>
            </div>

            {/* About */}
            <div className="glass-card" style={{ padding: "24px", marginTop: 16, textAlign: "center" }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>🧠</div>
                <div style={{ fontSize: 16, fontWeight: 600 }}>CogniSense</div>
                <div style={{ fontSize: 12, color: "var(--text-tertiary)", marginTop: 4 }}>
                    v0.1.0 — Multimodal Cognitive Load Detection
                </div>
                <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 8 }}>
                    Built with React, FastAPI, scikit-learn, XGBoost
                </div>
            </div>
        </div>
    );
}
