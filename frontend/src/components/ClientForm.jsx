import { useState } from 'react';
import Modal from './Modal';
import './ClientForm.css';

const API_URL = 'http://localhost:8000';

function ClientForm({ onClientCreated }) {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [alert, setAlert] = useState(null);
    const [showModal, setShowModal] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setAlert(null);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/clients/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name, email })
            });

            const data = await response.json();

            if (response.ok) {
                setName('');
                setEmail('');
                setShowModal(true);
                onClientCreated();
            } else {
                setAlert({ type: 'error', message: data.detail || 'Failed to send credentials' });
            }
        } catch (error) {
            setAlert({ type: 'error', message: 'Connection error. Please ensure the backend is running.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="card">
                <h3>
                    <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Send Client Credentials
                </h3>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="clientName">Client Name</label>
                        <input
                            type="text"
                            id="clientName"
                            className="form-control"
                            placeholder="John Doe"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="clientEmail">Client Email</label>
                        <input
                            type="email"
                            id="clientEmail"
                            className="form-control"
                            placeholder="client@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    {alert && (
                        <div className={`alert alert-${alert.type}`}>
                            <span>{alert.type === 'success' ? '✓' : '⚠'}</span>
                            <span>{alert.message}</span>
                        </div>
                    )}

                    <button type="submit" className="btn btn-success" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                <span>Sending...</span>
                            </>
                        ) : (
                            <span>Send Credentials via Email</span>
                        )}
                    </button>
                </form>
            </div>

            <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
                <h3>Credentials Sent Successfully!</h3>
                <div className="alert alert-success">
                    <span>✓</span>
                    <span>Login credentials have been sent to the client's email address.</span>
                </div>
                <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>
                    The client can now log in using the credentials sent to their email.
                </p>
            </Modal>
        </>
    );
}

export default ClientForm;
