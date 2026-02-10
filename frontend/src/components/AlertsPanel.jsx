// CogniSense — Alerts Panel Component
// TODO: Implement in Phase 6
import React from "react";

export default function AlertsPanel({ alerts }) {
    return (
        <div className="alerts-panel">
            <h3>Alerts</h3>
            {alerts?.length > 0
                ? alerts.map((a, i) => <div key={i} className="alert">{a.message}</div>)
                : <p>No alerts</p>
            }
        </div>
    );
}
