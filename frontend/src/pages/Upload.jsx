import { useState, useEffect } from 'react';
import Layout from '../layouts/Layout';
import UploadArea from '../components/UploadArea';
import DocumentsTable from '../components/DocumentsTable';
import Modal from '../components/Modal';
import './Dashboard.css';
import { apiFetch } from '../utils/api';

function Upload({ user, onLogout }) {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [shareModal, setShareModal] = useState({ open: false, document: null });
    const [clients, setClients] = useState([]);
    const [showUploadModal, setShowUploadModal] = useState(false);

    const loadDocuments = async () => {
        try {
            const response = await apiFetch('/api/documents/list');
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

    const isLegal = user.role === 'admin' || user.role === 'legal_team';

    const loadClients = async () => {
        if (isLegal) {
            try {
                const response = await apiFetch('/api/clients/list');
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
        setShowUploadModal(false);
    };

    const handleApprove = async (documentId) => {
        try {
            const response = await apiFetch('/api/documents/approve/${documentId}', {
                method: 'POST',
            });
            if (response.ok) loadDocuments();
        } catch (error) {
            console.error('Error approving document:', error);
        }
    };

    const handleShare = (document) => {
        setShareModal({ open: true, document });
    };

    const handleShareSubmit = async (clientId) => {
        try {
            const response = await apiFetch('/api/documents/share', {
                method: 'POST',
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
        <Layout user={user} onLogout={onLogout} pageTitle="Documents">
            <div className="dashboard-content-v2">
                <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2>{isLegal ? 'Document Management' : 'Document Upload'}</h2>
                        <p>{isLegal
                            ? 'Manage all legal records and share them with clients.'
                            : 'Upload and track your contract documents.'}</p>
                    </div>
                    <button
                        className="btn-create"
                        onClick={() => setShowUploadModal(true)}
                        style={{ padding: '0.875rem 1.5rem', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Upload Document
                    </button>
                </div>

                <div className="section-header" style={{ marginTop: '2.5rem' }}>
                    <h3>{isLegal ? 'Repository' : 'Your History'}</h3>
                </div>

                <div className="table-wrapper">
                    <DocumentsTable
                        documents={documents}
                        loading={loading}
                        onApprove={handleApprove}
                        onShare={handleShare}
                        currentUser={user}
                    />
                </div>
            </div>

            <Modal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)}>
                <div className="client-form-container" style={{ minWidth: '400px' }}>
                    <div className="form-header">
                        <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <h3>Quick Upload</h3>
                    </div>
                    <UploadArea onUploadComplete={handleUploadComplete} />
                </div>
            </Modal>

            <Modal isOpen={shareModal.open} onClose={() => setShareModal({ open: false, document: null })}>
                <h3 style={{ color: '#1e293b', marginBottom: '1rem' }}>Share Document</h3>
                <p style={{ color: '#64748b', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
                    Send "{shareModal.document?.filename}" to:
                </p>
                {isLegal && (
                    <div className="form-group">
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: '#64748b', fontSize: '0.8125rem', fontWeight: '600' }}>
                            Target Client
                        </label>
                        <select
                            className="form-control"
                            style={{ width: '100%', padding: '0.75rem', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', color: '#1e293b' }}
                            onChange={(e) => e.target.value && handleShareSubmit(e.target.value)}
                        >
                            <option value="">Select a client...</option>
                            {clients.map(client => (
                                <option key={client.id} value={client.id}>
                                    {client.name} ({client.email})
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </Modal>
        </Layout>
    );
}

export default Upload;