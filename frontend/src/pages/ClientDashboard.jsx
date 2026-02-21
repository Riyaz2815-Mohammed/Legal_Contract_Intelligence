import { useState, useEffect } from 'react';
import Layout from '../layouts/Layout';
import DocumentsTable from '../components/DocumentsTable';
import UploadArea from '../components/UploadArea';
import Modal from '../components/Modal';
import WorkspaceTabs from '../components/WorkspaceTabs';
import ChatBox from '../components/ChatBox';
import StatusBadge from '../components/StatusBadge';
import './Dashboard.css';
import './ClientWorkspace.css';

const API_URL = 'http://localhost:8000';

function ClientDashboard({ user, onLogout }) {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('documents');
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [uploadType, setUploadType] = useState('Others');
    const [legalTeam, setLegalTeam] = useState([]);
    const [selectedRecipient, setSelectedRecipient] = useState(null);

    // Mock Assigned Contract Data for demo
    const assignedContract = {
        title: "Service Agreement - Q1 2026",
        status: "Pending",
        driveLink: "https://docs.google.com/document/u/0/?tgif=d",
        assignedBy: "Legal Team Admin",
        date: "2026-02-20"
    };

    const loadDocuments = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/documents/list`, {
                headers: { 'Authorization': `Bearer ${token}` }
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

    const loadLegalTeam = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/legal/list`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await response.json();
            if (response.ok) {
                setLegalTeam(data.members || []);
                if (data.members && data.members.length > 0) {
                    setSelectedRecipient(data.members[0]);
                }
            }
        } catch (error) {
            console.error('Error loading legal team:', error);
        }
    };

    useEffect(() => {
        loadDocuments();
        loadLegalTeam();
    }, []);

    const handleUploadClick = (type) => {
        setUploadType(type);
        setShowUploadModal(true);
    };

    const handleUploadComplete = () => {
        setShowUploadModal(false);
        loadDocuments();
        setActiveTab('documents');
    };

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Client Portal">
            <div className="workspace-container">
                <div className="workspace-header">
                    <div className="client-summary-card">
                        <div className="client-overview">
                            <div className="client-avatar-large">{user.name.charAt(0)}</div>
                            <div className="client-info">
                                <h1>Welcome, {user.name}</h1>
                                <p>Client Portal - Manage your legal documents and communication</p>
                                <div className="client-badges">
                                    <StatusBadge status="Active User" />
                                    <span className="info-badge">Portal Access: Enabled</span>
                                </div>
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
                                    <h2>Your Documents</h2>
                                    <div className="header-buttons">
                                        <button className="btn-workspace" onClick={() => handleUploadClick('Redlined')}>
                                            Upload Redlined
                                        </button>
                                        <button className="btn-workspace" onClick={() => handleUploadClick('Others')}>
                                            Upload New
                                        </button>
                                    </div>
                                </div>

                                <div className="assigned-contract-v2 workspace-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                                <h3 style={{ margin: 0, color: 'white' }}>{assignedContract.title}</h3>
                                                <StatusBadge status={assignedContract.status} />
                                            </div>
                                            <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.875rem' }}>
                                                Assigned by {assignedContract.assignedBy} on {assignedContract.date}
                                            </p>
                                        </div>
                                        <button className="btn-drive" onClick={() => window.open(assignedContract.driveLink, '_blank')}>
                                            View in Google Drive
                                        </button>
                                    </div>
                                </div>

                                <div className="workspace-card">
                                    <DocumentsTable
                                        documents={documents}
                                        loading={loading}
                                        currentUser={user}
                                    />
                                </div>
                            </div>
                        )}

                        {activeTab === 'chat' && (
                            <div className="chat-section">
                                <div className="section-actions">
                                    <h2>Legal Support Chat</h2>
                                    <p>Direct communication with your legal advisors</p>
                                </div>
                                <div className="chat-interface-v2">
                                    <div className="contacts-sidebar">
                                        <div className="sidebar-header">
                                            <h3>Contacts</h3>
                                        </div>
                                        <div className="contacts-list">
                                            {legalTeam.map((member) => (
                                                <div
                                                    key={member.id}
                                                    className={`contact-item ${selectedRecipient?.id === member.id ? 'active' : ''}`}
                                                    onClick={() => setSelectedRecipient(member)}
                                                >
                                                    <div className="contact-avatar">{member.name.charAt(0)}</div>
                                                    <div className="contact-info">
                                                        <div className="contact-name">{member.name}</div>
                                                        <div className="contact-role">Legal Team</div>
                                                    </div>
                                                </div>
                                            ))}
                                            {legalTeam.length === 0 && (
                                                <div className="contact-empty">No contacts found</div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="chat-main">
                                        {selectedRecipient ? (
                                            <>
                                                <div className="chat-recipient-header">
                                                    <div className="recipient-avatar">{selectedRecipient.name.charAt(0)}</div>
                                                    <div className="recipient-details">
                                                        <h4>{selectedRecipient.name}</h4>
                                                        <span>Direct Message</span>
                                                    </div>
                                                </div>
                                                <ChatBox currentUser={user} recipientId={selectedRecipient.id} />
                                            </>
                                        ) : (
                                            <div className="chat-placeholder">
                                                <div className="placeholder-icon">💬</div>
                                                <p>Select a contact to start messaging</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'activity' && (
                            <div className="activity-section">
                                <div className="section-actions">
                                    <h2>Activity Timeline</h2>
                                    <p>Track history of uploads and status changes</p>
                                </div>
                                <div className="activity-log workspace-card">
                                    <div className="log-empty">Activity history will appear here.</div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <Modal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)}>
                <h2 style={{ color: 'white', marginBottom: '1.5rem' }}>Upload {uploadType}</h2>
                <UploadArea onUploadComplete={handleUploadComplete} documentType={uploadType} />
            </Modal>
        </Layout>
    );
}

export default ClientDashboard;
