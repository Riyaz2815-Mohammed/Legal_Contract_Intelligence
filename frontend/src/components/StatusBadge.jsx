import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status }) => {
    const getStatusClass = () => {
        switch (status?.toLowerCase()) {
            case 'approved':
            case 'active':
                return 'status-approved';
            case 'pending':
            case 'uploaded':
                return 'status-pending';
            case 'rejected':
            case 'error':
                return 'status-rejected';
            default:
                return 'status-default';
        }
    };

    return (
        <span className={`status-badge ${getStatusClass()}`}>
            {status || 'Unknown'}
        </span>
    );
};

export default StatusBadge;
