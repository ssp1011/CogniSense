// CogniSense — Sidebar Navigation (macOS style)
import React from "react";

const navItems = [
    { id: "dashboard", icon: "📊", label: "Dashboard" },
    { id: "history", icon: "🕐", label: "Session History" },
    { id: "settings", icon: "⚙️", label: "Settings" },
];

export default function Navbar({ activePage, onNavigate, isActive, sessionId }) {
    return (
        <nav className="sidebar">
            <div className="sidebar-brand">
                <div className="brand-icon">🧠</div>
                <h1>CogniSense</h1>
            </div>

            <div className="sidebar-nav">
                <div className="nav-section">Main</div>
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        className={`nav-item ${activePage === item.id ? "active" : ""}`}
                        onClick={() => onNavigate(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </button>
                ))}
            </div>

            <div className="sidebar-status">
                <div className="status-label">Session</div>
                <div className="status-indicator">
                    <span className={`status-dot ${isActive ? "live" : "idle"}`} />
                    <span style={{ color: isActive ? "var(--accent-green)" : "var(--text-tertiary)" }}>
                        {isActive ? "Recording" : "Idle"}
                    </span>
                </div>
                {isActive && sessionId && (
                    <div style={{
                        fontSize: 11,
                        color: "var(--text-tertiary)",
                        marginTop: 4,
                        fontFamily: "monospace"
                    }}>
                        {sessionId.slice(0, 8)}…
                    </div>
                )}
            </div>
        </nav>
    );
}
