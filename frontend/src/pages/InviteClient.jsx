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
            <div className="dashboard-content-v2" style={{ gap: 0 }}>
                <div className="section-header">
                    <h2>Send Client Credentials</h2>
                    <p>Invite a new client and provide them with secure access to their dedicated legal workspace.</p>
                </div>

                <div style={{ maxWidth: '640px', margin: '1.5rem auto 0' }}>
                    <div style={{ background: '#ffffff', borderRadius: '24px', border: '1px solid #e2e8f0', boxShadow: '0 12px 32px rgba(0,0,0,0.03)', overflow: 'hidden' }}>

                        <div style={{ padding: '2rem 2.5rem 1rem', borderBottom: '1px solid #f1f5f9' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                                    <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem', fontWeight: 600 }}>Invite new client</h3>
                                    <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>Enter their details to create a secure workspace</p>
                                </div>
                            </div>

                            <div className="client-form-wrapper" style={{ marginTop: '1rem' }}>
                                <ClientForm onClientCreated={handleClientCreated} />
                            </div>
                        </div>

                        <div style={{ padding: '1.25rem 2.5rem', background: '#f8fafc' }}>
                            <h4 style={{ margin: '0 0 0.75rem 0', color: '#475569', fontSize: '0.8125rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                                What happens next
                            </h4>
                            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                                    <div style={{ color: '#8b5cf6', background: '#ede9fe', padding: '0.5rem', borderRadius: '8px' }}>
                                        <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                                    </div>
                                    <span style={{ fontSize: '0.8125rem', color: '#64748b', fontWeight: 500, lineHeight: 1.4 }}>Email invite sent instantly</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                                    <div style={{ color: '#10b981', background: '#d1fae5', padding: '0.5rem', borderRadius: '8px' }}>
                                        <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                                    </div>
                                    <span style={{ fontSize: '0.8125rem', color: '#64748b', fontWeight: 500, lineHeight: 1.4 }}>Secure workspace created</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </Layout>
    );
}

export default InviteClient;
