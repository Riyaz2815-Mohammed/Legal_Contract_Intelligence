import './StatsCard.css';

function StatsCard({ title, value, icon }) {
    return (
        <div className="stats-card-v2">
            <div className="stats-info">
                <p className="stats-title">{title}</p>
                <div className="stats-main">
                    <h2 className="stats-value">{value}</h2>
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
