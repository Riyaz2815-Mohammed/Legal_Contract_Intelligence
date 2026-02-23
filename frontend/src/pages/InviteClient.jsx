import { useNavigate } from 'react-router-dom';
import Layout from '../layouts/Layout';
import ClientForm from '../components/ClientForm';

function InviteClient({ user, onLogout }) {
    const navigate = useNavigate();

    const handleClientCreated = () => {
        // Optional: navigate to dashboard after successful invitation
        // navigate('/dashboard');
    };

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Send Credentials">
            <div className="dashboard-content-v2">
                <div className="section-header">
                    <h2>Send Client Credentials</h2>
                    <p>Invite a new client and provide them with secure access to their dedicated legal workspace.</p>
                </div>

                <div style={{ maxWidth: '600px', margin: '2rem 0' }}>
                    <ClientForm onClientCreated={handleClientCreated} />
                </div>

                <div className="workspace-card" style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                    <h4 style={{ color: '#2563eb', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        What happens next?
                    </h4>
                    <ul style={{ color: '#64748b', fontSize: '0.875rem', paddingLeft: '1.25rem', lineHeight: '1.6' }}>
                        <li>An automated email will be sent to the client with their login credentials.</li>
                        <li>The client will appear in your dashboard list once they are created.</li>
                        <li>You can then start sharing documents and communicating with them via their workspace.</li>
                    </ul>
                </div>
            </div>
        </Layout>
    );
}

export default InviteClient;
