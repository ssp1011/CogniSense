// CogniSense — Cognitive Load Meter Component
// TODO: Implement in Phase 6
import React from "react";

export default function CognitiveLoadMeter({ level, confidence }) {
    return (
        <div className="load-meter">
            <h3>Cognitive Load</h3>
            <p>Level: {level || "—"}</p>
            <p>Confidence: {confidence ? `${(confidence * 100).toFixed(1)}%` : "—"}</p>
        </div>
    );
}
