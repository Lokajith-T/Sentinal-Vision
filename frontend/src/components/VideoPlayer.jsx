import React from 'react';

const VideoPlayer = ({ url }) => {
    return (
        <div className="video-wrapper">
            <div className="video-overlay">LIVE :: CAM-01</div>
            <img
                src={url}
                alt="Live Surveillance Feed"
                className="video-feed"
                onError={(e) => {
                    e.target.style.display = 'none';
                }}
            />
            {/* Fallback loader when video stream is not active */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: -1 }}>
                <div className="loader"></div>
                <p style={{ marginTop: '10px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Waiting for stream...</p>
            </div>
        </div>
    );
};

export default VideoPlayer;
