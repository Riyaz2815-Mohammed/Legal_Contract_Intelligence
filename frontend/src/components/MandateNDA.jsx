import React, { useState, useEffect } from 'react';
import './MandateNDA.css';

import { API_URL } from '../config';

const MandateNDA = ({ onAccepted }) => {
    const [template, setTemplate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accepting, setAccepting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchLatestNDA = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_URL}/api/templates/latest-nda`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    setTemplate(data);
                } else {
                    setError('Mandatory NDA template not found. Please contact legal team.');
                }
            } catch (err) {
                console.error('Error fetching latest NDA:', err);
                setError('Failed to load NDA. Please check your connection.');
            } finally {
                setLoading(false);
            }
        };

        fetchLatestNDA();
    }, []);

    const handleAccept = async () => {
        setAccepting(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/contracts/accept-mandate`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                // Update local storage user data
                const userData = JSON.parse(localStorage.getItem('user'));
                userData.nda_accepted = true;
                localStorage.setItem('user', JSON.stringify(userData));
                onAccepted(userData);
            } else {
                alert('Failed to accept NDA. Please try again.');
            }
        } catch (err) {
            console.error('Error accepting NDA:', err);
            alert('A connection error occurred.');
        } finally {
            setAccepting(false);
        }
    };

    const handleView = async () => {
        if (!template) return;
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/templates/download/${template.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.download_url) {
                window.open(data.download_url, '_blank');
            } else {
                alert('Failed to open document.');
            }
        } catch (err) {
            console.error('Download error:', err);
        }
    };

    if (loading) {
        return (
            <div className="mandate-overlay">
                <div className="mandate-card">
                    <div className="mandate-loader">
                        <div className="spinner-large"></div>
                        <p>Preparing Mandatory Documents...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="mandate-overlay">
            <div className="mandate-card">
                <div className="mandate-header">
                    <div className="mandate-icon"></div>
                    <h2>Mandatory Legal Agreement</h2>
                    <p>Before proceeding to the portal, you must review and accept the Non-Disclosure Agreement updated by our legal team.</p>
                </div>

                {error ? (
                    <div className="mandate-error">
                        <p>{error}</p>
                        <button className="btn-retry" onClick={() => window.location.reload()}>Retry</button>
                    </div>
                ) : (
                    <div className="mandate-content">
                        <div className="document-preview-box">
                            <div className="doc-info">
                                <svg className="doc-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <div className="doc-details">
                                    <span className="doc-label">Standard Template</span>
                                    <span className="doc-name">{template?.filename}</span>
                                </div>
                            </div>
                            <button className="btn-view-doc" onClick={handleView}>
                                View Document
                            </button>
                        </div>

                        <div className="mandate-notice">
                            <p>By clicking "Accept NDA", you agree to the terms and conditions outlined in the document above. This is required for portal access.</p>
                        </div>

                        <div className="mandate-actions">
                            <button
                                className="btn-decline"
                                onClick={() => {
                                    if (confirm('Rejecting the NDA will sign you out. You cannot access the portal without accepting. Proceed?')) {
                                        window.location.reload(); // Simple way to reset state if rejected
                                    }
                                }}
                            >
                                Decline
                            </button>
                            <button
                                className={`btn-accept ${accepting ? 'loading' : ''}`}
                                onClick={handleAccept}
                                disabled={accepting}
                            >
                                {accepting ? 'Processing...' : 'Accept NDA'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MandateNDA;
