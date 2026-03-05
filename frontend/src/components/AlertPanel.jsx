import React from 'react';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

const AlertPanel = ({ alerts }) => {
    if (!alerts || alerts.length === 0) {
        return (
            <div className="list-container" style={{ justifyContent: 'center', alignItems: 'center', opacity: 0.5 }}>
                <Info size={32} style={{ marginBottom: '10px' }} />
                <p>No active threats detected.</p>
            </div>
        );
    }

    return (
        <div className="list-container">
            {alerts.map((alert, index) => {
                const time = new Date(alert.timestamp).toLocaleTimeString();
                let Icon = Info;
                let alertClass = '';

                if (alert.level === 'critical') {
                    alertClass = 'critical';
                    Icon = AlertTriangle;
                } else if (alert.level === 'high') {
                    alertClass = 'high';
                    Icon = AlertCircle;
                } else if (alert.level === 'medium') {
                    alertClass = 'medium';
                    Icon = Info;
                }

                return (
                    <div key={`${alert.id}-${index}`} className={`alert-item ${alertClass}`}>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <Icon size={20} className={`badge-${alertClass}`} style={{ background: 'transparent', boxShadow: 'none' }} />
                            <div className="alert-info">
                                <h4>{alert.object.replace('_', ' ')}</h4>
                                <p>{time}</p>
                            </div>
                        </div>
                        <span className={`alert-badge badge-${alertClass}`}>
                            {alert.level}
                        </span>
                    </div>
                );
            })}
        </div>
    );
};

export default AlertPanel;
