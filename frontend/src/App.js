// CogniSense — Main App Component
import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import SessionHistory from "./pages/SessionHistory";
import Settings from "./pages/Settings";
import useCaptureSession from "./hooks/useCaptureSession";

function App() {
    const [activePage, setActivePage] = useState("dashboard");
    const capture = useCaptureSession();

    // Check for existing active session on mount
    useEffect(() => {
        capture.checkStatus();
    }, []); // check once on mount

    const handleStart = async (scenario) => {
        try {
            await capture.start(scenario);
        } catch {
            // error is set in hook
        }
    };

    const handleStop = async () => {
        try {
            await capture.stop();
        } catch {
            // error is set in hook
        }
    };

    const renderPage = () => {
        switch (activePage) {
            case "dashboard":
                return (
                    <Dashboard
                        isActive={capture.isActive}
                        session={capture.session}
                        onStart={handleStart}
                        onStop={handleStop}
                        loading={capture.loading}
                    />
                );
            case "history":
                return <SessionHistory />;
            case "settings":
                return <Settings />;
            default:
                return <Dashboard />;
        }
    };

    return (
        <div className="app-layout">
            <Navbar
                activePage={activePage}
                onNavigate={setActivePage}
                isActive={capture.isActive}
                sessionId={capture.session?.session_id}
            />
            <main className="main-content">
                {capture.error && (
                    <div className="alert-item danger" style={{
                        marginBottom: 16,
                        borderRadius: "var(--radius-sm)",
                    }}>
                        ❌ {capture.error}
                    </div>
                )}
                {renderPage()}
            </main>
        </div>
    );
}

export default App;
