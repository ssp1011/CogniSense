// CogniSense — WebSocket Hook
// Real-time cognitive load streaming

import { useState, useEffect, useRef, useCallback } from "react";

const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/api/v1/ws/load";

export default function useWebSocket(autoConnect = false) {
    const [data, setData] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [history, setHistory] = useState([]);
    const wsRef = useRef(null);
    const reconnectRef = useRef(null);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            setIsConnected(true);
            console.log("[WS] Connected");
        };

        ws.onmessage = (event) => {
            try {
                const parsed = JSON.parse(event.data);
                if (parsed.load_level) {
                    setData(parsed);
                    setHistory((prev) => [...prev.slice(-59), parsed]);
                }
            } catch (e) {
                // ignore non-JSON
            }
        };

        ws.onclose = () => {
            setIsConnected(false);
            console.log("[WS] Disconnected");
            // Auto-reconnect after 3s
            reconnectRef.current = setTimeout(() => connect(), 3000);
        };

        ws.onerror = () => {
            ws.close();
        };

        wsRef.current = ws;
    }, []);

    const disconnect = useCallback(() => {
        clearTimeout(reconnectRef.current);
        wsRef.current?.close();
        wsRef.current = null;
        setIsConnected(false);
    }, []);

    const sendCommand = useCallback((action) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action }));
        }
    }, []);

    useEffect(() => {
        if (autoConnect) connect();
        return () => disconnect();
    }, [autoConnect, connect, disconnect]);

    return { data, isConnected, history, connect, disconnect, sendCommand };
}
