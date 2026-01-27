import './DocumentsTable.css';

function DocumentsTable({ documents, loading, onApprove, onShare, currentUser }) {
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    const getStatusBadge = (status) => {
        const badges = {
            'pending': { class: 'badge-pending', text: 'Pending Approval' },
            'approved': { class: 'badge-success', text: 'Approved' },
            'rejected': { class: 'badge-danger', text: 'Rejected' },
            'uploaded': { class: 'badge-success', text: 'Uploaded' }
        };
        return badges[status] || badges['uploaded'];
    };

    const getDocumentTypeColor = (type) => {
        const colors = {
            'NDA': '#ef4444',
            'MSA': '#3b82f6',
            'SOW': '#10b981',
            'Redlined': '#f59e0b',
            'Others': '#6366f1'
        };
        return colors[type] || '#6366f1';
    };

    if (loading) {
        return (
            <table className="table">
                <thead>
                    <tr>
                        <th>Document Name</th>
                        <th>Type</th>
                        <th>Upload Date</th>
                        <th>Status</th>
                        <th>Size</th>
                        {currentUser?.role === 'admin' && <th>Actions</th>}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colSpan={currentUser?.role === 'admin' ? "6" : "5"} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            Loading documents...
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

    if (documents.length === 0) {
        return (
            <table className="table">
                <thead>
                    <tr>
                        <th>Document Name</th>
                        <th>Type</th>
                        <th>Upload Date</th>
                        <th>Status</th>
                        <th>Size</th>
                        {currentUser?.role === 'admin' && <th>Actions</th>}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colSpan={currentUser?.role === 'admin' ? "6" : "5"} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            No documents uploaded yet. Upload your first document above!
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

    return (
        <table className="table">
            <thead>
                <tr>
                    <th>Document Name</th>
                    <th>Type</th>
                    <th>Upload Date</th>
                    <th>Status</th>
                    <th>Size</th>
                    {currentUser?.role === 'admin' && <th>Actions</th>}
                </tr>
            </thead>
            <tbody>
                {documents.map((doc) => {
                    const statusBadge = getStatusBadge(doc.status);
                    return (
                        <tr key={doc.id}>
                            <td>{doc.filename}</td>
                            <td>
                                <span style={{
                                    color: getDocumentTypeColor(doc.document_type),
                                    fontWeight: 600,
                                    fontSize: '0.875rem'
                                }}>
                                    {doc.document_type || 'Others'}
                                </span>
                            </td>
                            <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                            <td>
                                <span className={`badge ${statusBadge.class}`}>
                                    {statusBadge.text}
                                </span>
                            </td>
                            <td>{formatFileSize(doc.size)}</td>
                            {currentUser?.role === 'admin' && (
                                <td>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        {doc.status === 'pending' && (
                                            <button
                                                className="btn-action btn-approve"
                                                onClick={() => onApprove(doc.id)}
                                                title="Approve Document"
                                            >
                                                ✓
                                            </button>
                                        )}
                                        <button
                                            className="btn-action btn-share"
                                            onClick={() => onShare(doc)}
                                            title="Share Document"
                                        >
                                            📤
                                        </button>
                                    </div>
                                </td>
                            )}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}

export default DocumentsTable;
