// CogniSense — Modality Contribution Chart
// TODO: Implement in Phase 6
import React from "react";

export default function ModalityChart({ scores }) {
    return (
        <div className="modality-chart">
            <h3>Modality Contributions</h3>
            <ul>
                <li>Visual: {scores?.visual?.toFixed(2) || "—"}</li>
                <li>Behavioral: {scores?.behavioral?.toFixed(2) || "—"}</li>
                <li>Audio: {scores?.audio?.toFixed(2) || "—"}</li>
            </ul>
        </div>
    );
}
