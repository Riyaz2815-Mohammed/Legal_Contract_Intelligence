import { useState } from 'react';
import Modal from './Modal';
import './LegalTeamForm.css';

const API_URL = 'http://localhost:8000';

function LegalTeamForm({ onMemberCreated }) {
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
            const response = await fetch(`${API_URL}/api/legal/create`, {
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
                onMemberCreated();
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
                <div className="form-header">
                    <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    <h3>Add Legal Team Member</h3>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="memberName">Full Name</label>
                        <div className="form-input-wrapper">
                            <input
                                type="text"
                                id="memberName"
                                className="form-control"
                                placeholder="Enter member name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="memberEmail">Email Address</label>
                        <div className="form-input-wrapper">
                            <input
                                type="email"
                                id="memberEmail"
                                className="form-control"
                                placeholder="lawyer@laccis.com"
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

                    <button type="submit" className="btn-submit" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner-small"></span>
                                <span>Processing...</span>
                            </>
                        ) : (
                            <span>Create Access Card</span>
                        )}
                    </button>
                </form>
            </div>

            <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
                <h3>Team Member Added!</h3>
                <div className="alert alert-success">
                    <span>✓</span>
                    <span>Invitation and credentials have been sent via email.</span>
                </div>
            </Modal>
        </>
    );
}

export default LegalTeamForm;
