import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../layouts/Layout';
import ClientsTable from '../components/ClientsTable';
import StatsCard from '../components/StatsCard';
import ClientDashboard from './ClientDashboard';
import './Dashboard.css';

const API_URL = 'http://localhost:8000';

function Dashboard({ user, onLogout }) {
    const navigate = useNavigate();

    // Only actual clients see the client dashboard — admins and legal team see the full dashboard
    if (user.role === 'client') {
        return <ClientDashboard user={user} onLogout={onLogout} />;
    }

    const [clients, setClients] = useState([]);
    const [stats, setStats] = useState({ totalDocs: 0, totalClients: 0, pendingReviews: 0 });
    const [loading, setLoading] = useState(true);

    const loadClientsAndStats = async () => {
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
                const documents = docsData.documents || [];
                let sumTotalDocs = 0;
                let sumPendingReviews = 0;

                const clientList = clientsData.clients.map(client => {
                    const clientDocs = documents.filter(d =>
                        d.user_id === client.id || (Array.isArray(d.shared_with) && d.shared_with.includes(client.id))
                    );
                    const pendingCount = clientDocs.filter(d => d.status === 'pending' || d.status === 'uploaded').length;

                    sumTotalDocs += clientDocs.length;
                    sumPendingReviews += pendingCount;

                    return {
                        ...client,
                        totalDocs: clientDocs.length,
                        pendingDocs: pendingCount
                    };
                });

                setClients(clientList);
                setStats({
                    totalDocs: sumTotalDocs,
                    totalClients: clientList.length,
                    pendingReviews: sumPendingReviews
                });
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadClientsAndStats();
    }, []);

    const handleClientCreated = () => {
        loadClientsAndStats();
    };

    const handleClientDelete = async (client) => {
        if (!window.confirm(`Are you sure you want to delete ${client.name}?`)) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/clients/delete/${client.id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                loadClientsAndStats();
            } else {
                const data = await response.json();
                alert(data.detail || 'Failed to delete client');
            }
        } catch (error) {
            console.error('Error deleting client:', error);
        }
    };

    const handleOpenWorkspace = (client) => {
        navigate(`/workspace/${client.id}`);
    };

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Dashboard">
            <div className="dashboard-content-v2">
                <div className="stats-row">
                    <StatsCard
                        title="Total Documents"
                        value={stats.totalDocs}
                        icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />}
                    />
                    <StatsCard
                        title="Active Clients"
                        value={stats.totalClients}
                        icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 4 0 014 0z" />}
                    />
                    <StatsCard
                        title="Pending Reviews"
                        value={stats.pendingReviews}
                        icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />}
                    />
                </div>

                <div className="section-header" style={{ marginTop: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2>All Clients</h2>
                        <p>Manage and monitor your legal workspaces</p>
                    </div>
                    <button className="btn btn-primary" style={{ width: 'auto', padding: '0.75rem 1.5rem', borderRadius: '8px', boxShadow: '0 4px 12px rgba(37,99,235,0.2)' }} onClick={() => navigate('/invite-client')}>
                        Create New Client
                    </button>
                </div>

                <div style={{ marginTop: '1rem' }}>
                    <ClientsTable
                        clients={clients}
                        loading={loading}
                        onDelete={handleClientDelete}
                        onOpenWorkspace={handleOpenWorkspace}
                    />
                </div>
            </div>
        </Layout>
    );
}

export default Dashboard;
