import './StatsCard.css';

function StatsCard({ title, value, icon, trend }) {
    return (
        <div className="stats-card-v2">
            <div className="stats-info">
                <p className="stats-title">{title}</p>
                <div className="stats-main">
                    <h2 className="stats-value">{value}</h2>
                    {trend && (
                        <span className={`stats-trend ${trend > 0 ? 'up' : 'down'}`}>
                            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                        </span>
                    )}
                </div>
            </div>
            <div className="stats-icon-wrapper">
                <svg className="stats-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {icon}
                </svg>
            </div>
        </div>
    );
}

export default StatsCard;
