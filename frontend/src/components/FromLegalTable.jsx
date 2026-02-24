import './FromLegalTable.css';

const API_URL = 'http://localhost:8000';

function FromLegalTable({ contracts, loading, onAccept }) {
    const formatFileSize = (bytes) => {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    const getStatusBadge = (status) => {
        if (status === 'accepted' || status === 'reviewed') {
            return { cls: 'badge-success', text: 'Accepted' };
        }
        return { cls: 'badge-pending', text: 'Pending Review' };
    };

    const handleDownload = async (contractId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/contracts/download/${contractId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.download_url) {
                window.open(data.download_url, '_blank');
            } else if (res.ok) {
                // Fetch as blob for browser download
                const blobRes = await fetch(`${API_URL}/api/contracts/download/${contractId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const blob = await blobRes.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', ''); // filename will be inferred or set by browser
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);
            } else {
                alert('Download failed: ' + (data.detail || 'Unknown error'));
            }
        } catch (err) {
            console.error('Download error:', err);
            alert('Download failed');
        }
    };

    const tableHead = (
        <thead>
            <tr>
                <th>Document Name</th>
                <th>Type</th>
                <th>Shared Date</th>
                <th>Status</th>
                <th>Size</th>
                <th>Actions</th>
            </tr>
        </thead>
    );

    if (loading) {
        return (
            <table className="table">
                {tableHead}
                <tbody>
                    <tr>
                        <td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            Loading contracts...
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

    if (!contracts || contracts.length === 0) {
        return (
            <table className="table">
                {tableHead}
                <tbody>
                    <tr>
                        <td colSpan="6" className="fl-empty-cell">
                            <div className="fl-empty">
                                <span className="fl-empty-icon">📂</span>
                                <p>No contracts shared by the legal team yet.</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

    return (
        <table className="table">
            {tableHead}
            <tbody>
                {contracts.map((contract) => {
                    const { cls, text } = getStatusBadge(contract.status);
                    return (
                        <tr key={contract.id}>
                            <td className="fl-filename">{contract.filename}</td>
                            <td>
                                <span className="fl-type-badge">
                                    {contract.document_type || 'PDF'}
                                </span>
                            </td>
                            <td>{new Date(contract.shared_at).toLocaleDateString()}</td>
                            <td>
                                <span className={`badge ${cls}`}>{text}</span>
                            </td>
                            <td>{formatFileSize(contract.size)}</td>
                            <td>
                                <div className="fl-actions">
                                    <button
                                        className="btn-action btn-download"
                                        onClick={() => handleDownload(contract.id)}
                                        title="Download Contract"
                                    >
                                        ⬇ Download
                                    </button>
                                    {contract.status === 'pending_review' && (
                                        <button
                                            className="btn-action btn-approve"
                                            onClick={() => onAccept && onAccept(contract.id)}
                                            style={{ backgroundColor: '#10b981' }}
                                            title="Accept Contract"
                                        >
                                            ✅ Accept
                                        </button>
                                    )}
                                </div>
                            </td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}

export default FromLegalTable;
