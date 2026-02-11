// CogniSense — Cognitive Load Meter (Radial Gauge)
// Apple-style animated ring gauge
import React, { useMemo } from "react";

const RADIUS = 72;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getLoadColor(level) {
    switch (level) {
        case "low": return "var(--load-low)";
        case "medium": return "var(--load-medium)";
        case "high": return "var(--load-high)";
        default: return "var(--text-tertiary)";
    }
}

function getConfidencePercent(confidence) {
    return Math.round((confidence || 0) * 100);
}

export default function CognitiveLoadMeter({ loadLevel = "low", confidence = 0 }) {
    const percent = getConfidencePercent(confidence);
    const color = getLoadColor(loadLevel);
    const dashOffset = useMemo(
        () => CIRCUMFERENCE - (percent / 100) * CIRCUMFERENCE,
        [percent]
    );

    return (
        <div className="glass-card load-meter-container">
            <div className="chart-title" style={{ width: "100%", marginBottom: 16 }}>
                <span>🎯</span> Cognitive Load
            </div>

            <div className="load-meter">
                <svg viewBox="0 0 180 180">
                    <circle className="track" cx="90" cy="90" r={RADIUS} />
                    <circle
                        className="fill"
                        cx="90"
                        cy="90"
                        r={RADIUS}
                        stroke={color}
                        strokeDasharray={CIRCUMFERENCE}
                        strokeDashoffset={dashOffset}
                    />
                </svg>
                <div className="center-text">
                    <span className="load-value" style={{ color }}>
                        {percent}%
                    </span>
                    <span className="load-label">Confidence</span>
                </div>
            </div>

            <div className={`load-level-badge ${loadLevel}`}>
                <span className="dot" />
                {loadLevel.toUpperCase()}
            </div>
        </div>
    );
}
