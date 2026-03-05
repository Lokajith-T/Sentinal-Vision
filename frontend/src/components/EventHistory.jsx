import React, { useState, useEffect } from 'react';

const EventHistory = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    // Poll for events every 3 seconds
    useEffect(() => {
        const fetchEvents = () => {
            fetch('http://localhost:8001/events?limit=10')
                .then(res => res.json())
                .then(data => {
                    if (data.events) setEvents(data.events);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Could not fetch events", err);
                    setLoading(false);
                });
        };

        fetchEvents();
        const intervalId = setInterval(fetchEvents, 3000);
        return () => clearInterval(intervalId);
    }, []);

    if (loading) {
        return <div className="loader" style={{ margin: '20px auto' }}></div>;
    }

    return (
        <div className="list-container" style={{ maxHeight: '160px' }}>
            <table className="event-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>Source</th>
                        <th>Detected Object</th>
                        <th>Threat Level</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
                    {events.length === 0 ? (
                        <tr><td colSpan="6" style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>No events recorded yet.</td></tr>
                    ) : events.map(ev => (
                        <tr key={ev.id}>
                            <td>#{ev.id}</td>
                            <td>{new Date(ev.timestamp).toLocaleString()}</td>
                            <td>{ev.camera_source}</td>
                            <td style={{ textTransform: 'capitalize' }}>{ev.detected_object}</td>
                            <td>
                                <span className={`alert-badge badge-${ev.threat_level === 'none' ? 'medium' : ev.threat_level}`}>
                                    {ev.threat_level}
                                </span>
                            </td>
                            <td style={{ fontFamily: 'monospace' }}>
                                {ev.location_x !== null ? `[${ev.location_x}, ${ev.location_y}]` : 'N/A'}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default EventHistory;
