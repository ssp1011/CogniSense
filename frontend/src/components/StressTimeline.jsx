// CogniSense — Stress Timeline Chart
// Real-time line chart of cognitive load over time
import React, { useRef, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip);

// Map load level to numeric
function loadToNum(level) {
    switch (level) {
        case "high": return 3;
        case "medium": return 2;
        case "low": return 1;
        default: return 0;
    }
}

export default function StressTimeline({ history = [] }) {
    const chartRef = useRef(null);

    const labels = history.map((_, i) => {
        const secsAgo = history.length - 1 - i;
        return secsAgo === 0 ? "Now" : `-${secsAgo}s`;
    });

    const confidenceData = history.map((h) => Math.round((h.confidence || 0) * 100));
    const loadData = history.map((h) => loadToNum(h.load_level));

    // Dynamic gradient
    useEffect(() => {
        const chart = chartRef.current;
        if (!chart) return;
        const ctx = chart.ctx;
        const area = chart.chartArea;
        if (!area) return;

        const gradient = ctx.createLinearGradient(0, area.top, 0, area.bottom);
        gradient.addColorStop(0, "rgba(10, 132, 255, 0.3)");
        gradient.addColorStop(1, "rgba(10, 132, 255, 0.0)");
        chart.data.datasets[0].backgroundColor = gradient;
        chart.update("none");
    });

    const data = {
        labels,
        datasets: [
            {
                label: "Confidence %",
                data: confidenceData,
                borderColor: "rgba(10, 132, 255, 1)",
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                tension: 0.4,
                fill: true,
                backgroundColor: "rgba(10, 132, 255, 0.1)",
            },
            {
                label: "Load Level",
                data: loadData,
                borderColor: "rgba(191, 90, 242, 0.6)",
                borderWidth: 1.5,
                borderDash: [4, 4],
                pointRadius: 0,
                tension: 0.3,
                fill: false,
                yAxisID: "y1",
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: {
            mode: "index",
            intersect: false,
        },
        plugins: {
            tooltip: {
                backgroundColor: "rgba(28, 28, 30, 0.95)",
                titleColor: "rgba(245, 245, 247, 0.6)",
                bodyColor: "#f5f5f7",
                borderColor: "rgba(255, 255, 255, 0.08)",
                borderWidth: 1,
                cornerRadius: 8,
                padding: 10,
                titleFont: { size: 11, weight: 500 },
                bodyFont: { size: 13, weight: 600 },
            },
        },
        scales: {
            x: {
                display: true,
                grid: { display: false },
                ticks: {
                    color: "rgba(245, 245, 247, 0.3)",
                    font: { size: 10 },
                    maxTicksLimit: 8,
                },
            },
            y: {
                display: true,
                min: 0,
                max: 100,
                grid: {
                    color: "rgba(255, 255, 255, 0.04)",
                },
                ticks: {
                    color: "rgba(245, 245, 247, 0.3)",
                    font: { size: 10 },
                    callback: (v) => `${v}%`,
                },
            },
            y1: {
                display: false,
                min: 0,
                max: 4,
                position: "right",
            },
        },
    };

    return (
        <div className="glass-card chart-card full-width">
            <div className="chart-title">
                <span>📈</span> Stress Timeline
            </div>
            <div className="chart-body">
                {history.length === 0 ? (
                    <div className="empty-state">
                        <p>Start a session to see real-time data</p>
                    </div>
                ) : (
                    <Line ref={chartRef} data={data} options={options} />
                )}
            </div>
        </div>
    );
}
