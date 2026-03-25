import { useState } from 'react';
import Modal from './Modal';
import './ClientForm.css';

import { API_URL } from '../config';

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
            <div className="client-form-container">
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="clientName">Client Name</label>
                        <div className="form-input-wrapper">
                            <input
                                type="text"
                                id="clientName"
                                className="form-control"
                                placeholder="Enter full name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="clientEmail">Client Email</label>
                        <div className="form-input-wrapper">
                            <input
                                type="email"
                                id="clientEmail"
                                className="form-control"
                                placeholder="name@company.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    {alert && (
                        <div className={`form-alert ${alert.type}`}>
                            <span>{alert.type === 'success' ? '✓' : '⚠'}</span>
                            <span>{alert.message}</span>
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '0.875rem', borderRadius: '10px' }} disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner-small"></span>
                                <span>Processing...</span>
                            </>
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                                <span>Send Credentials</span>
                                <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </div>
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
