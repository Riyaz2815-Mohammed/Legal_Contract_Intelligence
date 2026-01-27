import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import UploadArea from '../components/UploadArea';
import DocumentsTable from '../components/DocumentsTable';
import Modal from '../components/Modal';
import './Upload.css';

const API_URL = 'http://localhost:8000';

function Upload({ user, onLogout }) {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [shareModal, setShareModal] = useState({ open: false, document: null });
    const [clients, setClients] = useState([]);

    const loadDocuments = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/documents/list`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();
            if (response.ok) {
                setDocuments(data.documents);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadClients = async () => {
        if (user.role === 'admin') {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_URL}/api/clients/list`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                const data = await response.json();
                if (response.ok) {
                    setClients(data.clients);
                }
            } catch (error) {
                console.error('Error loading clients:', error);
            }
        }
    };

    useEffect(() => {
        loadDocuments();
        loadClients();
    }, []);

    const handleUploadComplete = () => {
        loadDocuments();
    };

    const handleApprove = async (documentId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/documents/approve/${documentId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                loadDocuments();
            }
        } catch (error) {
            console.error('Error approving document:', error);
        }
    };

    const handleShare = (document) => {
        setShareModal({ open: true, document });
    };

    const handleShareSubmit = async (clientId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/documents/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    document_id: shareModal.document.id,
                    share_with: clientId
                })
            });

            if (response.ok) {
                setShareModal({ open: false, document: null });
                loadDocuments();
            }
        } catch (error) {
            console.error('Error sharing document:', error);
        }
    };

    return (
        <div className="upload-page">
            <Navbar user={user} onLogout={onLogout} title={user.role === 'admin' ? 'Document Management' : 'Document Upload'} />

            <div className="upload-container">
                <div className="glass-container">
                    <h1>{user.role === 'admin' ? 'Upload & Manage Documents' : 'Upload Contract Documents'}</h1>
                    <p className="subtitle">
                        {user.role === 'admin'
                            ? 'Upload documents and share them with clients. Approve client NDAs to enable further uploads.'
                            : 'Upload your legal contract documents. NDA must be uploaded and approved first before uploading other documents.'}
                    </p>

                    <UploadArea onUploadComplete={handleUploadComplete} />
                </div>

                <div className="glass-container">
                    <h3>
                        <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {user.role === 'admin' ? 'All Documents' : 'Your Uploaded Documents'}
                    </h3>
                    <DocumentsTable
                        documents={documents}
                        loading={loading}
                        onApprove={handleApprove}
                        onShare={handleShare}
                        currentUser={user}
                    />
                </div>
            </div>

            {/* Share Modal */}
            <Modal isOpen={shareModal.open} onClose={() => setShareModal({ open: false, document: null })}>
                <h3>Share Document</h3>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                    Share "{shareModal.document?.filename}" with:
                </p>

                {user.role === 'admin' && (
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                            Select Client:
                        </label>
                        <select
                            className="form-control"
                            onChange={(e) => e.target.value && handleShareSubmit(e.target.value)}
                        >
                            <option value="">Choose a client...</option>
                            {clients.map(client => (
                                <option key={client.id} value={client.id}>
                                    {client.name} ({client.email})
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </Modal>
        </div>
    );
}

export default Upload;
