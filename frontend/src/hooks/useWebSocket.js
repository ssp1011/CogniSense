// CogniSense — WebSocket Hook for Live Scores
// TODO: Implement in Phase 6
import { useState, useEffect, useRef } from "react";

export default function useWebSocket(url) {
    const [data, setData] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        if (!url) return;
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => setIsConnected(true);
        ws.onmessage = (event) => setData(JSON.parse(event.data));
        ws.onclose = () => setIsConnected(false);
        ws.onerror = () => setIsConnected(false);

        return () => ws.close();
    }, [url]);

    return { data, isConnected };
}
