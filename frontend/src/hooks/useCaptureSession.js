// CogniSense — Capture Session Hook
// Manages session lifecycle

import { useState, useCallback } from "react";
import { startCapture, stopCapture, getSessionStatus } from "../services/api";

export default function useCaptureSession() {
    const [session, setSession] = useState(null);
    const [isActive, setIsActive] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const start = useCallback(async (scenario = "general", notes = "") => {
        setLoading(true);
        setError(null);
        try {
            const res = await startCapture(scenario, notes);
            setSession(res.data);
            setIsActive(true);
            return res.data;
        } catch (err) {
            const msg = err.response?.data?.detail || "Failed to start session";
            setError(msg);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const stop = useCallback(async () => {
        if (!session?.session_id) return;
        setLoading(true);
        setError(null);
        try {
            const res = await stopCapture(session.session_id);
            setSession(res.data);
            setIsActive(false);
            return res.data;
        } catch (err) {
            const msg = err.response?.data?.detail || "Failed to stop session";
            setError(msg);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [session]);

    const checkStatus = useCallback(async () => {
        try {
            const res = await getSessionStatus();
            if (res.data.active) {
                setIsActive(true);
                setSession(res.data);
            } else {
                setIsActive(false);
            }
            return res.data;
        } catch {
            // Server not available
        }
    }, []);

    return { session, isActive, loading, error, start, stop, checkStatus };
}
