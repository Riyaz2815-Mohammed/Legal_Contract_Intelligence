import './StatsCard.css';

function StatsCard({ title, value, icon }) {
    return (
        <div className="card stats-card">
            <h3>
                <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {icon}
                </svg>
                {title}
            </h3>
            <div className="stats-value">{value}</div>
        </div>
    );
}

export default StatsCard;
