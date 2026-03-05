import React, { useState, useEffect } from 'react';
import VideoPlayer from './components/VideoPlayer';
import AlertPanel from './components/AlertPanel';
import EventHistory from './components/EventHistory';
import HeatmapData from './components/HeatmapData';
import { Camera, ShieldAlert } from 'lucide-react';
import './index.css';

function App() {
  const [alerts, setAlerts] = liveAlerts();

  // Custom hook for polling latest alerts
  function liveAlerts() {
    const [data, setData] = useState([]);
    useEffect(() => {
      const intervalId = setInterval(() => {
        fetch('http://localhost:8001/alerts')
          .then(res => res.json())
          .then(data => {
            if (data.alerts) setData(data.alerts);
          })
          .catch(err => console.error("Could not fetch alerts", err));
      }, 1000); // poll every 1 second
      return () => clearInterval(intervalId);
    }, []);
    return [data, setData];
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <ShieldAlert className="brand-icon" size={28} />
          <h1>Sentinel Vision</h1>
        </div>
        <div className="header-status">
          <div className="status-dot"></div>
          <span>System Active</span>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <main className="main-content">

        {/* Cameras Row */}
        <div className="camera-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
          <div className="card">
            <div className="card-header">
              <Camera size={20} />
              Camera 1 (Laptop)
            </div>
            <VideoPlayer url="http://localhost:8001/video-feed/cam1" />
          </div>

          <div className="card">
            <div className="card-header">
              <Camera size={20} />
              Camera 2 (Mobile IP)
            </div>
            <VideoPlayer url="http://localhost:8001/video-feed/cam2" />
          </div>
        </div>

        {/* Analytics Row */}
        <div className="analytics-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', minHeight: '300px' }}>
          <div className="card">
            <div className="card-header">
              <ShieldAlert size={20} />
              Real-Time Alerts (Global)
            </div>
            <AlertPanel alerts={alerts} />
          </div>

          <div className="card">
            <div className="card-header">
              Event Heatmap (Camera 1)
            </div>
            <HeatmapData url="http://localhost:8001/heatmap/cam1" />
          </div>
        </div>

        {/* Full Bottom row: Events History */}
        <div className="card">
          <div className="card-header">
            Logs & Incident History
          </div>
          <EventHistory />
        </div>

      </main>
    </div>
  );
}

export default App;
