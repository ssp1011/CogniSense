// CogniSense — Stress Timeline Component
// TODO: Implement in Phase 6
import React from "react";

export default function StressTimeline({ data }) {
    return (
        <div className="stress-timeline">
            <h3>Stress Timeline</h3>
            <p>{data?.length || 0} data points</p>
        </div>
    );
}
