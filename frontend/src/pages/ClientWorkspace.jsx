import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../layouts/Layout';
import WorkspaceTabs from '../components/WorkspaceTabs';
import ChatBox from '../components/ChatBox';
import DocumentsTable from '../components/DocumentsTable';
import StatusBadge from '../components/StatusBadge';
import './ClientWorkspace.css';

const API_URL = 'http://localhost:8000';

const ClientWorkspace = ({ user, onLogout }) => {
    const { clientId } = useParams();
    const navigate = useNavigate();
    const [client, setClient] = useState(null);
    const [activeTab, setActiveTab] = useState('documents');
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        try {
            const token = localStorage.getItem('token');
            const [clientsRes, docsRes] = await Promise.all([
                fetch(`${API_URL}/api/clients/list`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                }),
                fetch(`${API_URL}/api/documents/list`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
            ]);

            const clientsData = await clientsRes.json();
            const docsData = await docsRes.json();

            if (clientsRes.ok && docsRes.ok) {
                const currentClient = clientsData.clients.find(c => c.id === clientId);
                if (!currentClient) {
                    navigate('/dashboard');
                    return;
                }
                setClient(currentClient);
                setDocuments(docsData.documents.filter(d => d.user_id === clientId));
            }
        } catch (error) {
            console.error('Error loading workspace data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [clientId]);

    if (loading || !client) {
        return (
            <Layout user={user} onLogout={onLogout} pageTitle="Client Workspace">
                <div className="loading-workspace">Loading workspace...</div>
            </Layout>
        );
    }

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Client Workspace">
            <div className="workspace-container">
                <div className="workspace-header">
                    <div className="client-summary-card">
                        <div className="client-overview">
                            <div className="client-avatar-large">{client.name.charAt(0)}</div>
                            <div className="client-info">
                                <h1>{client.name}</h1>
                                <p>{client.email}</p>
                                <div className="client-badges">
                                    <StatusBadge status="Active" />
                                    <span className="info-badge">Registered: {new Date(client.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                        <div className="client-stats-mini">
                            <div className="mini-stat">
                                <span className="stat-label">Documents</span>
                                <span className="stat-value">{documents.length}</span>
                            </div>
                            <div className="mini-stat">
                                <span className="stat-label">Pending</span>
                                <span className="stat-value text-warning">
                                    {documents.filter(d => d.status === 'pending' || d.status === 'uploaded').length}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="workspace-main">
                    <WorkspaceTabs activeTab={activeTab} onTabChange={setActiveTab} />

                    <div className="tab-content">
                        {activeTab === 'documents' && (
                            <div className="documents-section">
                                <div className="section-actions">
                                    <h2>Client Documents</h2>
                                    <button className="btn-drive" onClick={() => window.open('https://drive.google.com', '_blank')}>
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                        Google Drive
                                    </button>
                                </div>
                                <div className="workspace-card">
                                    <DocumentsTable
                                        documents={documents}
                                        loading={false}
                                        currentUser={user}
                                        onApprove={() => loadData()}
                                    />
                                </div>
                            </div>
                        )}

                        {activeTab === 'chat' && (
                            <div className="chat-section">
                                <div className="section-actions">
                                    <h2>Direct Messaging</h2>
                                    <p>Real-time updates with {client.name}</p>
                                </div>
                                <ChatBox currentUser={user} recipientId={clientId} />
                            </div>
                        )}

                        {activeTab === 'activity' && (
                            <div className="activity-section">
                                <div className="section-actions">
                                    <h2>Activity Log</h2>
                                    <p>History of all actions in this workspace</p>
                                </div>
                                <div className="activity-log workspace-card">
                                    {/* Activity log logic would go here */}
                                    <div className="log-empty">No recent activity found.</div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default ClientWorkspace;
