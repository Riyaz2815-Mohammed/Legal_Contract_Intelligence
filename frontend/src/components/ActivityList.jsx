import './ActivityList.css';

function ActivityList({ activities, loading }) {
    if (loading) {
        return <div className="activity-loading">Loading activities...</div>;
    }

    if (!activities || activities.length === 0) {
        return (
            <div className="activity-empty">
                <p>No recent activity found.</p>
            </div>
        );
    }

    const getActionIcon = (action) => {
        if (action.includes('Approved')) return '✅';
        if (action.includes('Rejected')) return '❌';
        if (action.includes('Shared')) return '📤';
        if (action.includes('Accepted')) return '🤝';
        if (action.includes('Uploaded')) return '📄';
        return '🔹';
    };

    const formatTime = (isoString) => {
        const date = new Date(isoString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';

        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;

        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) return `${diffInHours}h ago`;

        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="activity-list">
            {activities.map((activity) => (
                <div key={activity.id} className="activity-item">
                    <div className="activity-icon-container">
                        <span className="activity-icon">{getActionIcon(activity.action)}</span>
                    </div>
                    <div className="activity-details">
                        <div className="activity-header">
                            <span className="activity-action">{activity.action}</span>
                            <span className="activity-time">{formatTime(activity.timestamp)}</span>
                        </div>
                        {activity.details && (
                            <p className="activity-desc">{activity.details}</p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ActivityList;
