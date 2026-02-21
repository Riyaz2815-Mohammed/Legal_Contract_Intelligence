import './LegalTeamTable.css';
import StatusBadge from './StatusBadge';

function LegalTeamTable({ members, loading, onDelete }) {
    if (loading) {
        return (
            <div className="table-loading">
                <div className="spinner"></div>
                <p>Loading legal team members...</p>
            </div>
        );
    }

    if (members.length === 0) {
        return (
            <div className="table-empty">
                <p>No legal team members yet. Create one above!</p>
            </div>
        );
    }

    return (
        <div className="table-wrapper">
            <table className="custom-table">
                <thead>
                    <tr>
                        <th style={{ width: '60px' }}></th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {members.map((member) => (
                        <tr key={member.id}>
                            <td>
                                <div className="client-avatar">
                                    {member.name.charAt(0)}
                                </div>
                            </td>
                            <td style={{ fontWeight: 600 }}>{member.name}</td>
                            <td style={{ color: '#94a3b8' }}>{member.email}</td>
                            <td><StatusBadge status="Active" /></td>
                            <td style={{ color: '#64748b', fontSize: '0.875rem' }}>
                                {new Date(member.created_at).toLocaleDateString()}
                            </td>
                            <td>
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <button
                                        className="btn-icon-delete"
                                        onClick={() => onDelete(member)}
                                        title="Delete Member"
                                    >
                                        <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default LegalTeamTable;
