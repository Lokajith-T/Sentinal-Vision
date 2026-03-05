import React, { useState, useEffect } from 'react';

const HeatmapData = ({ url }) => {
    // Add a cache buster parameter to force reload the image periodically
    const [timestamp, setTimestamp] = useState(Date.now());

    useEffect(() => {
        const interval = setInterval(() => {
            setTimestamp(Date.now());
        }, 5000); // refresh heatmap every 5 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ flex: 1, position: 'relative', minHeight: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ position: 'absolute', zIndex: 0 }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Waiting for heatmap data...</p>
            </div>
            <img
                key={timestamp}
                src={`${url}?t=${timestamp}`}
                alt="Activity Heatmap"
                className="heatmap-image"
                style={{ position: 'relative', zIndex: 1, width: '100%', height: '100%', objectFit: 'cover' }}
            />
        </div>
    );
};

export default HeatmapData;
