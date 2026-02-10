// CogniSense — Capture Session Hook
// TODO: Implement in Phase 6
import { useState } from "react";
import { startCapture, stopCapture } from "../services/api";

export default function useCaptureSession() {
    const [sessionId, setSessionId] = useState(null);
    const [isCapturing, setIsCapturing] = useState(false);
    const [error, setError] = useState(null);

    const start = async (config = {}) => {
        try {
            const res = await startCapture(config);
            setSessionId(res.data.session_id);
            setIsCapturing(true);
            setError(null);
        } catch (err) {
            setError(err.message);
        }
    };

    const stop = async () => {
        try {
            await stopCapture(sessionId);
            setIsCapturing(false);
        } catch (err) {
            setError(err.message);
        }
    };

    return { sessionId, isCapturing, error, start, stop };
}
