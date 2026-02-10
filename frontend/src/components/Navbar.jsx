// CogniSense — Navigation Bar
// TODO: Implement in Phase 6
import React from "react";

export default function Navbar() {
    return (
        <nav className="navbar">
            <span className="brand">🧠 CogniSense</span>
            <div className="nav-links">
                <a href="/">Dashboard</a>
                <a href="/history">History</a>
                <a href="/settings">Settings</a>
            </div>
        </nav>
    );
}
