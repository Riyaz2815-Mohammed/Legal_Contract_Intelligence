import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../layouts/Layout';
import './DocumentAnalysis.css';

import { API_URL } from '../config';

const TemplateAnalysis = ({ user, onLogout }) => {
    const { templateId } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_URL}/api/templates/analysis/${templateId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const result = await response.json();
                if (response.ok) {
                    setData(result);
                } else {
                    setError(result.detail || 'Failed to load analysis');
                }
            } catch (err) {
                console.error('Fetch error:', err);
                setError('Connection error');
            } finally {
                setLoading(false);
            }
        };

        fetchAnalysis();
    }, [templateId]);

    const getClauseTypeColor = (type) => {
        const colors = {
            'Indemnity': '#ef4444',
            'Limitation of Liability': '#f59e0b',
            'Confidentiality': '#3b82f6',
            'Termination': '#ec4899',
            'Payment Terms': '#10b981',
            'SLA': '#6366f1',
            'Governing Law': '#8b5cf6',
            'Force Majeure': '#f97316',
            'Intellectual Property': '#06b6d4',
            'Others': '#64748b'
        };
        return colors[type] || '#64748b';
    };

    if (loading) {
        return (
            <Layout user={user} onLogout={onLogout} pageTitle="Template Analysis">
                <div className="analysis-container">
                    <div style={{ textAlign: 'center', padding: '5rem', color: '#94a3b8' }}>
                        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                        Extracting template clauses and classifying...
                    </div>
                </div>
            </Layout>
        );
    }

    if (error) {
        return (
            <Layout user={user} onLogout={onLogout} pageTitle="Template Analysis">
                <div className="analysis-container">
                    <div className="alert alert-error">
                        <span>⚠</span>
                        <span>{error}</span>
                    </div>
                    <Link to="/templates" className="btn-back" style={{ marginTop: '2rem' }}>
                        ← Back to Templates
                    </Link>
                </div>
            </Layout>
        );
    }

    const { document, clauses, status } = data;

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Template Analysis">
            <div className="analysis-container">
                <div className="analysis-header">
                    <Link to="/templates" className="btn-back">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="19" y1="12" x2="5" y2="12"></line>
                            <polyline points="12 19 5 12 12 5"></polyline>
                        </svg>
                        Back to Templates
                    </Link>
                    <h1>Template Assessment</h1>
                    <div className="badge badge-success">
                        Standard
                    </div>
                </div>

                <div className="doc-info-bar">
                    <div className="info-item">
                        <span className="info-label">Filename</span>
                        <span className="info-value">{document.filename}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Template Type</span>
                        <span className="info-value">{document.template_type}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Uploaded</span>
                        <span className="info-value">{new Date(document.uploaded_at).toLocaleDateString()}</span>
                    </div>
                    {status === 'processing' && (
                        <div className="info-item" style={{ marginLeft: 'auto' }}>
                            <span className="clause-type-badge" style={{ background: '#f59e0b', color: 'white' }}>
                                Processing AI Analysis...
                            </span>
                        </div>
                    )}
                </div>

                {clauses.length === 0 ? (
                    <div className="workspace-card" style={{ textAlign: 'center', padding: '4rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}></div>
                        <h3 style={{ color: 'white' }}>No clauses detected</h3>
                        <p style={{ color: '#94a3b8' }}>
                            {status === 'processing'
                                ? "Our AI is currently analyzing this template. Please check back in a few seconds."
                                : "The extraction engine couldn't find any specific clauses in this template."}
                        </p>
                    </div>
                ) : (
                    <div className="clause-grid">
                        {clauses.map((clause, index) => (
                            <div key={clause.content_id || index} className="clause-card">
                                <div className="clause-card-header">
                                    <span className="clause-id">{clause.clause_id || (index + 1)}</span>
                                    <span
                                        className="clause-type-badge"
                                        style={{
                                            background: `${getClauseTypeColor(clause.clause)}20`,
                                            color: getClauseTypeColor(clause.clause),
                                            border: `1px solid ${getClauseTypeColor(clause.clause)}40`
                                        }}
                                    >
                                        {clause.clause}
                                    </span>
                                </div>
                                <div className="clause-content">
                                    {clause.content}
                                </div>
                                <div className="page-indicator">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                        <polyline points="14 2 14 8 20 8"></polyline>
                                    </svg>
                                    Page {clause.page_number}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default TemplateAnalysis;
