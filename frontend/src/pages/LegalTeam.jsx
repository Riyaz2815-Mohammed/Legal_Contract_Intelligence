import { useState, useEffect } from 'react';
import Layout from '../layouts/Layout';
import LegalTeamForm from '../components/LegalTeamForm';
import LegalTeamTable from '../components/LegalTeamTable';
import Modal from '../components/Modal';
import './Dashboard.css';

import { API_URL } from '../config';

function LegalTeam({ user, onLogout }) {
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showInviteModal, setShowInviteModal] = useState(false);

    const loadMembers = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/legal/list`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await response.json();
            if (response.ok) {
                setMembers(data.members || []);
            }
        } catch (error) {
            console.error('Error loading legal team members:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMembers();
    }, []);

    const handleMemberCreated = () => {
        loadMembers();
        setShowInviteModal(false);
    };

    const handleMemberDelete = async (member) => {
        if (!window.confirm(`Are you sure you want to delete ${member.name}?`)) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/legal/delete/${member.id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                loadMembers();
            } else {
                const data = await response.json();
                alert(data.detail || 'Failed to delete member');
            }
        } catch (error) {
            console.error('Error deleting member:', error);
        }
    };

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Legal Team">
            <div className="dashboard-content-v2">
                <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2>Legal Team Management</h2>
                        <p>Invite and manage your legal team members</p>
                    </div>
                    <button
                        className="btn-create"
                        onClick={() => setShowInviteModal(true)}
                        style={{ padding: '0.875rem 1.5rem', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Add Team Member
                    </button>
                </div>

                <div className="section-header" style={{ marginTop: '2.5rem' }}>
                    <h3>Active Legal Team Members</h3>
                </div>

                <div style={{ marginTop: '1rem' }}>
                    <LegalTeamTable
                        members={members}
                        loading={loading}
                        onDelete={handleMemberDelete}
                    />
                </div>
            </div>

            <Modal isOpen={showInviteModal} onClose={() => setShowInviteModal(false)}>
                <div style={{ padding: '0.5rem' }}>
                    <LegalTeamForm onMemberCreated={handleMemberCreated} />
                </div>
            </Modal>
        </Layout>
    );
}

export default LegalTeam;
