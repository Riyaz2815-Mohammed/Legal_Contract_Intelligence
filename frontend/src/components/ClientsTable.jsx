import './ClientsTable.css';
import StatusBadge from './StatusBadge';
import { API_URL } from '../config';


function ClientsTable({ clients, loading, onDelete, onOpenWorkspace }) {
    if (loading) {
        return (
            <div className="table-loading">
                <div className="spinner"></div>
                <span>Loading clients...</span>
            </div>
        );
    }

    if (clients.length === 0) {
        return (
            <div className="table-empty">
                <p>No clients yet. Create one above!</p>
            </div>
        );
    }

    return (
        <div className="table-wrapper">
            <table className="custom-table">
                <thead>
                    <tr>
                        <th>Client Info</th>
                        <th>Status</th>
                        <th>Documents</th>
                        <th>Pending</th>
                        <th>Actions</th>
                        <th>Finalized Document</th>
                    </tr>
                </thead>
                <tbody>
                    {clients.map((client) => (
                        <tr key={client.id}>
                            <td>
                                <div className="client-info-cell">
                                    <div className="client-avatar">
                                        {client.name.charAt(0)}
                                    </div>
                                    <div className="client-details">
                                        <span className="client-name">{client.name}</span>
                                        <span className="client-email">{client.email}</span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <StatusBadge status="Active" />
                            </td>
                            <td>
                                <span className="doc-count">{client.totalDocs || 0}</span>
                            </td>
                            <td>
                                <span className="doc-count pending">{client.pendingDocs || 0}</span>
                            </td>
                            <td>
                                <div className="action-buttons">
                                    <button
                                        className="btn-workspace"
                                        onClick={() => onOpenWorkspace(client)}
                                        title="Open Workspace"
                                    >
                                        Open Workspace
                                    </button>
                                    <button
                                        className="btn-icon-delete"
                                        onClick={() => onDelete(client)}
                                        title="Delete Client"
                                    >
                                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </td>
                            <td>
                                {client.finalizedDocs && client.finalizedDocs.length > 0 ? (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                                        {client.finalizedDocs.map((doc) => {
                                            const token = localStorage.getItem('token');
                                            const downloadUrl = `${API_URL}/api/documents/download/${doc.id}`;
                                            
                                            // Handle click to download via direct S3 URL fetch
                                            const handleClick = async (e) => {
                                                e.preventDefault();
                                                try {
                                                    const res = await fetch(downloadUrl, {
                                                        headers: { 'Authorization': `Bearer ${token}` }
                                                    });
                                                    const data = await res.json();
                                                    if (data.download_url) {
                                                        window.open(data.download_url, '_blank');
                                                    } else {
                                                        alert('Download failed');
                                                    }
                                                } catch (err) {
                                                    console.error('Download error:', err);
                                                    alert('Download error');
                                                }
                                            };

                                            return (
                                                <a
                                                    key={doc.id}
                                                    href="#"
                                                    onClick={handleClick}
                                                    className="finalized-doc-link"
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '0.4rem',
                                                        padding: '0.3rem 0.6rem',
                                                        background: 'rgba(16, 185, 129, 0.1)',
                                                        color: '#059669',
                                                        borderRadius: '12px',
                                                        fontSize: '0.75rem',
                                                        fontWeight: '600',
                                                        textDecoration: 'none',
                                                        whiteSpace: 'nowrap',
                                                        transition: 'all 0.2s ease'
                                                    }}
                                                >
                                                    <span></span>
                                                    {doc.type === 'RA' ? 'Referral' : doc.type} Final

                                                </a>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontStyle: 'italic' }}>No finalized doc</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ClientsTable;
