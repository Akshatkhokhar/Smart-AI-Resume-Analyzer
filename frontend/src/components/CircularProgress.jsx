import React from 'react';

const CircularProgress = ({ score, size = 150, strokeWidth = 12 }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;

    // Determine color based on score
    let color = '#ef4444'; // Red for low score (<40)
    let status = 'Poor';

    if (score >= 80) {
        color = '#22c55e'; // Green for high
        status = 'Excellent';
    } else if (score >= 60) {
        color = '#f97316'; // Orange for medium
        status = 'Good';
    } else if (score >= 40) {
        color = '#eab308'; // Yellow for low-medium
        status = 'Moderate';
    }

    return (
        <div className="relative flex items-center justify-center p-4 bg-white rounded-xl shadow-sm border border-gray-100" style={{ width: size + 40, height: size + 40 }}>
            <svg className="transform -rotate-90 w-full h-full" style={{ width: size, height: size }}>
                {/* Background Circle */}
                <circle
                    className="text-gray-100"
                    strokeWidth={strokeWidth}
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
                {/* Progress Circle */}
                <circle
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                    className="transition-all duration-1000 ease-out"
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold" style={{ color }}>{score}%</span>
                <span className="text-sm font-medium text-gray-500 mt-1">{status}</span>
            </div>
        </div>
    );
};

export default CircularProgress;
