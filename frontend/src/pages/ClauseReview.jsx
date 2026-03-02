import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../layouts/Layout';
import DocumentChatbot from '../components/DocumentChatbot';
import './ClauseReview.css';

const API_URL = 'http://localhost:8000';

/* ── Colour helpers ──────────────────────────────────────────── */
const CLAUSE_COLORS = {
    'Indemnity': '#ef4444',
    'Limitation of Liability': '#f59e0b',
    'Confidentiality': '#3b82f6',
    'Termination': '#ec4899',
    'Payment Terms': '#10b981',
    'SLA': '#6366f1',
    'Governing Law': '#8b5cf6',
    'Force Majeure': '#f97316',
    'Intellectual Property': '#06b6d4',
    'Warranty': '#84cc16',
    'Data Protection': '#0ea5e9',
    'Other': '#64748b',
};
const clauseColor = (type) => CLAUSE_COLORS[type] || '#64748b';

const RISK_CONFIG = {
    High: { class: 'high', icon: '🔴', barColor: '#ef4444' },
    Medium: { class: 'medium', icon: '🟡', barColor: '#f59e0b' },
    Low: { class: 'low', icon: '🟢', barColor: '#10b981' },
};

/* ── Sub-component: single clause card ───────────────────────── */
function ClauseCard({ clause, documentId, onActionDone }) {
    const [expanded, setExpanded] = useState(false);
    const [llmOpen, setLlmOpen] = useState(false);
    const [question, setQuestion] = useState('Please analyze the risks and implications of this exact clause, and suggest how it could be made more favorable.');
    const [llmAnswer, setLlmAnswer] = useState('');
    const [llmLoading, setLlmLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);

    const risk = clause.risk || 'High';
    const rc = RISK_CONFIG[risk] || RISK_CONFIG.High;
    const color = clauseColor(clause.clause_type);
    const score = clause.similarity_score;
    const status = clause.status || 'pending';

    const handleAction = async (action) => {
        setActionLoading(true);
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/api/documents/review/${documentId}/action`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content_id: clause.content_id, action }),
            });
            onActionDone();
        } catch (err) {
            console.error('Action error', err);
        } finally {
            setActionLoading(false);
        }
    };

    const handleAskLLM = async () => {
        if (!question.trim()) return;
        setLlmLoading(true);
        setLlmAnswer('');
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/review/${documentId}/ask-llm`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content_id: clause.content_id, question }),
            });
            const data = await res.json();
            setLlmAnswer(data.answer || data.detail || 'No response');
        } catch (err) {
            setLlmAnswer('⚠️ Connection error');
        } finally {
            setLlmLoading(false);
        }
    };

    return (
        <div className={`clause-review-card risk-${rc.class} status-${status}`}>

            {/* Header row */}
            <div className="card-header-row">
                <span
                    className="clause-type-tag"
                    style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}
                >
                    {clause.clause_type || 'Other'}
                </span>

                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className={`risk-badge ${rc.class}`}>
                        {rc.icon} {risk} Risk
                    </span>
                    {status !== 'pending' && (
                        <span className={`status-chip ${status}`}>
                            {status === 'accepted' ? '✓ Accepted' : '✗ Rejected'}
                        </span>
                    )}
                </div>
            </div>

            {/* Clause content */}
            <div>
                <p className={`clause-content-text ${expanded ? 'expanded' : ''}`}>
                    {clause.content}
                </p>
                {clause.content && clause.content.length > 300 && (
                    <button className="btn-toggle-expand" onClick={() => setExpanded(e => !e)}>
                        {expanded ? 'Show less ↑' : 'Show more ↓'}
                    </button>
                )}
            </div>

            {/* Matched standard clause */}
            {clause.matched_clause && (
                <div className="matched-clause-box">
                    <div className="matched-clause-label">
                        🔗 Matched Standard Clause — {clause.matched_clause.document_type || 'Template'}
                    </div>
                    <p className="matched-clause-text">
                        {clause.matched_clause.content || 'No content available'}
                    </p>
                    {score !== null && score !== undefined && (
                        <div className="similarity-bar-row">
                            <div className="similarity-bar-wrap">
                                <div
                                    className="similarity-bar-fill"
                                    style={{
                                        width: `${Math.round(score * 100)}%`,
                                        background: rc.barColor,
                                    }}
                                />
                            </div>
                            <span className="similarity-score-text" style={{ color: rc.barColor }}>
                                {Math.round(score * 100)}% similar
                            </span>
                        </div>
                    )}
                </div>
            )}

            {/* Action buttons */}
            <div className="card-actions">
                <button
                    className="btn-accept"
                    onClick={() => handleAction('accept')}
                    disabled={actionLoading || status !== 'pending'}
                >
                    ✅ Accept
                </button>
                <button
                    className="btn-reject"
                    onClick={() => handleAction('reject')}
                    disabled={actionLoading || status !== 'pending'}
                >
                    ❌ Reject
                </button>
                <button
                    className="btn-ask-llm"
                    onClick={() => setLlmOpen(o => !o)}
                >
                    💬 Ask LLM
                </button>
            </div>

            {/* LLM panel */}
            {llmOpen && (
                <div className="llm-panel">
                    <textarea
                        placeholder="Ask about this clause… e.g. What are the risks? Is this standard?"
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        rows={3}
                    />
                    <button
                        className="btn-submit-llm"
                        onClick={handleAskLLM}
                        disabled={llmLoading || !question.trim()}
                    >
                        {llmLoading ? 'Thinking…' : 'Ask →'}
                    </button>
                    {llmAnswer && (
                        <div className="llm-answer">{llmAnswer}</div>
                    )}
                </div>
            )}
        </div>
    );
}


/* ── Main page ───────────────────────────────────────────────── */
export default function ClauseReview({ user, onLogout }) {
    const { documentId } = useParams();
    const navigate = useNavigate();

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('All');

    const fetchReview = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/review/${documentId}`, {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            const result = await res.json();
            if (res.ok) {
                setData(result);
            } else {
                setError(result.detail || 'Failed to load review');
            }
        } catch (err) {
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchReview(); }, [documentId]);

    if (loading) {
        return (
            <Layout user={user} onLogout={onLogout} pageTitle="Review">
                <div className="review-processing">
                    <div className="spinner" />
                    <p>Loading clause review…</p>
                </div>
            </Layout>
        );
    }

    if (error) {
        return (
            <Layout user={user} onLogout={onLogout} pageTitle="Review">
                <div className="review-processing">
                    <p style={{ color: '#f87171' }}>⚠️ {error}</p>
                    <button className="btn-back-review" onClick={() => navigate(-1)} style={{ marginTop: '1rem' }}>
                        ← Go Back
                    </button>
                </div>
            </Layout>
        );
    }

    const { document: doc, clauses = [], status } = data;
    const isProcessing = status === 'processing';

    // Risk summary counts
    const counts = clauses.reduce((acc, c) => {
        const r = c.risk || 'High';
        acc[r] = (acc[r] || 0) + 1;
        return acc;
    }, {});

    // Filtered clauses
    const filteredClauses = clauses.filter(c => {
        if (activeTab === 'All') return true;
        const r = c.risk || 'High';
        return r === activeTab;
    });

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Clause Review">
            <div className="review-page">

                {/* Header */}
                <div className="review-header">
                    <button className="btn-back-review" onClick={() => navigate(-1)}>
                        ← Back
                    </button>
                    <h1>Contract Clause Review</h1>
                    {isProcessing && (
                        <span className="risk-pill medium">⏳ Analysis in progress…</span>
                    )}
                </div>

                {/* Document info bar */}
                <div className="review-doc-bar">
                    <div className="info-item">
                        <span className="info-label">Filename</span>
                        <span className="info-value">{doc?.filename || '—'}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Type</span>
                        <span className="info-value">{doc?.document_type || '—'}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Uploaded</span>
                        <span className="info-value">
                            {doc?.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : '—'}
                        </span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Clauses</span>
                        <span className="info-value">{clauses.length}</span>
                    </div>
                </div>

                {/* Risk Tab Filters */}
                {clauses.length > 0 && (
                    <div className="risk-tabs" style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                        <button
                            className={`risk-tab-btn ${activeTab === 'All' ? 'active' : ''}`}
                            onClick={() => setActiveTab('All')}
                            style={{ padding: '0.5rem 1rem', borderRadius: '999px', border: '1px solid #334155', background: activeTab === 'All' ? '#334155' : 'transparent', color: 'white', cursor: 'pointer' }}
                        >
                            All ({clauses.length})
                        </button>
                        {counts.High > 0 && (
                            <button
                                className={`risk-tab-btn high ${activeTab === 'High' ? 'active' : ''}`}
                                onClick={() => setActiveTab('High')}
                                style={{ padding: '0.5rem 1rem', borderRadius: '999px', border: '1px solid #ef4444', background: activeTab === 'High' ? '#ef444422' : 'transparent', color: '#ef4444', cursor: 'pointer' }}
                            >
                                🔴 High Risk ({counts.High})
                            </button>
                        )}
                        {counts.Medium > 0 && (
                            <button
                                className={`risk-tab-btn medium ${activeTab === 'Medium' ? 'active' : ''}`}
                                onClick={() => setActiveTab('Medium')}
                                style={{ padding: '0.5rem 1rem', borderRadius: '999px', border: '1px solid #f59e0b', background: activeTab === 'Medium' ? '#f59e0b22' : 'transparent', color: '#f59e0b', cursor: 'pointer' }}
                            >
                                🟡 Medium Risk ({counts.Medium})
                            </button>
                        )}
                        {counts.Low > 0 && (
                            <button
                                className={`risk-tab-btn low ${activeTab === 'Low' ? 'active' : ''}`}
                                onClick={() => setActiveTab('Low')}
                                style={{ padding: '0.5rem 1rem', borderRadius: '999px', border: '1px solid #10b981', background: activeTab === 'Low' ? '#10b98122' : 'transparent', color: '#10b981', cursor: 'pointer' }}
                            >
                                🟢 Low Risk ({counts.Low})
                            </button>
                        )}
                    </div>
                )}

                {/* Clause grid */}
                {clauses.length === 0 ? (
                    <div className="review-processing">
                        <div className="spinner" />
                        <p>
                            {isProcessing
                                ? 'AI is analysing the document. Check back in a few seconds.'
                                : 'No clauses found in this document.'}
                        </p>
                    </div>
                ) : filteredClauses.length === 0 ? (
                    <div className="review-processing">
                        <p>No clauses match the {activeTab} risk filter.</p>
                    </div>
                ) : (
                    <div className="review-grid">
                        {filteredClauses.map((clause, idx) => (
                            <ClauseCard
                                key={clause.content_id || idx}
                                clause={clause}
                                documentId={documentId}
                                onActionDone={fetchReview}
                            />
                        ))}
                    </div>
                )}

                {/* Floating Chat Assistant */}
                <DocumentChatbot documentId={documentId} />
            </div>
        </Layout>
    );
}
