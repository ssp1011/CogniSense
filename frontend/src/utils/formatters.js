// CogniSense — Utility Formatters

/**
 * Format a load level string for display.
 * @param {string} level - "low" | "medium" | "high"
 * @returns {string} Capitalized level with emoji
 */
export function formatLoadLevel(level) {
    const map = {
        low: "🟢 Low",
        medium: "🟡 Medium",
        high: "🔴 High",
    };
    return map[level] || "— Unknown";
}

/**
 * Format a confidence score as percentage.
 * @param {number} confidence - 0.0 to 1.0
 * @returns {string}
 */
export function formatConfidence(confidence) {
    if (confidence == null) return "—";
    return `${(confidence * 100).toFixed(1)}%`;
}

/**
 * Format an ISO timestamp for display.
 * @param {string} isoString
 * @returns {string}
 */
export function formatTimestamp(isoString) {
    if (!isoString) return "—";
    return new Date(isoString).toLocaleTimeString();
}
