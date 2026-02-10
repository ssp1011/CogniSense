// CogniSense — Dashboard Page
// TODO: Implement in Phase 6
import React from "react";
import CognitiveLoadMeter from "../components/CognitiveLoadMeter";
import StressTimeline from "../components/StressTimeline";
import ModalityChart from "../components/ModalityChart";
import AlertsPanel from "../components/AlertsPanel";

export default function Dashboard() {
    return (
        <div className="dashboard">
            <h2>Live Monitoring</h2>
            <div className="dashboard-grid">
                <CognitiveLoadMeter level={null} confidence={null} />
                <StressTimeline data={[]} />
                <ModalityChart scores={null} />
                <AlertsPanel alerts={[]} />
            </div>
        </div>
    );
}
