import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../layouts/Layout';
import DocumentChatbot from '../components/DocumentChatbot';
import './ClauseReview.css';

const API_URL = 'http://localhost:8000';

/* ── Colour helpers ──────────────────────────────────────────── */
const CLAUSE_COLORS = {
    'Header': '#7c3aed',
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

const RISK_CONFIG = {
    High: { class: 'high', icon: '🔴', barColor: '#ef4444' },
    Medium: { class: 'medium', icon: '🟡', barColor: '#f59e0b' },
    Low: { class: 'low', icon: '🟢', barColor: '#10b981' },
};

// Normalise risk strings coming from backend ('high' → 'High')
const normalizeRisk = (r) => {
    if (!r) return 'High';
    return r.charAt(0).toUpperCase() + r.slice(1).toLowerCase();
};

export default function ClauseReview({ user, onLogout }) {
    const { documentId } = useParams();
    const navigate = useNavigate();

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('All');

    // Master-Detail State
    const [selectedClauseId, setSelectedClauseId] = useState(null);

    // Edit & Comment States
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState('');
    const [isCommenting, setIsCommenting] = useState(false);
    const [commentValue, setCommentValue] = useState('');

    // Action Loading states
    const [actionLoading, setActionLoading] = useState(false);

    // LLM State
    const [llmLoading, setLlmLoading] = useState(false);
    const [llmAnswer, setLlmAnswer] = useState('');

    const fetchReview = useCallback(async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/review/${documentId}`, {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            const result = await res.json();
            if (res.ok) {
                setData(result);
                return result.status;
            } else {
                setError(result.detail || 'Failed to load review');
            }
        } catch (err) {
            setError('Connection error');
        } finally {
            setLoading(false);
        }
        return null;
    }, [documentId]);

    const isPollingRef = React.useRef(false);

    // Risk summary counts
    const counts = useMemo(() => {
        const clauses = data?.clauses || [];
        return clauses.reduce((acc, c) => {
            const r = normalizeRisk(c.risk);
            acc[r] = (acc[r] || 0) + 1;
            return acc;
        }, {});
    }, [data]);

    // Filtered clauses
    const filteredClauses = useMemo(() => {
        const clauses = data?.clauses || [];
        return clauses.filter(c => {
            if (activeTab === 'All') return true;
            return normalizeRisk(c.risk) === activeTab;
        });
    }, [data, activeTab]);

    // Currently selected clause object
    const selectedClause = useMemo(() => {
        return filteredClauses.find(c => c.content_id === selectedClauseId) || filteredClauses[0];
    }, [filteredClauses, selectedClauseId]);

    // Force selection of first available item if selected isn't in filtered list
    useEffect(() => {
        if (filteredClauses.length > 0 && selectedClauseId) {
            const exists = filteredClauses.some(c => c.content_id === selectedClauseId);
            if (!exists) {
                setSelectedClauseId(filteredClauses[0].content_id);
            }
        } else if (filteredClauses.length > 0 && !selectedClauseId) {
            setSelectedClauseId(filteredClauses[0].content_id);
        }
    }, [filteredClauses, selectedClauseId]);

    useEffect(() => {
        let isMounted = true;
        let pollTimer = null;

        const poll = async () => {
            if (!isMounted || isPollingRef.current) return;
            isPollingRef.current = true;

            const status = await fetchReview();
            isPollingRef.current = false;

            if (isMounted && status === 'processing') {
                pollTimer = setTimeout(poll, 5000);
            }
        };

        poll();

        return () => {
            isMounted = false;
            if (pollTimer) clearTimeout(pollTimer);
            isPollingRef.current = false;
        };
    }, [fetchReview]);

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

    const doc = data?.document;
    const clauses = data?.clauses || [];
    const status = data?.status;
    const isProcessing = status === 'processing';

    // --- Actions ---

    const handleAction = async (actionStr) => {
        if (!selectedClause) return;
        setActionLoading(true);
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/api/documents/review/${documentId}/action`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content_id: selectedClause.content_id, action: actionStr }),
            });
            await fetchReview();
        } catch (err) {
            console.error('Action error', err);
        } finally {
            setActionLoading(false);
        }
    };

    const saveEdit = async () => {
        if (!selectedClause) return;
        setActionLoading(true);
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/api/documents/review/${documentId}/edit`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content_id: selectedClause.content_id, edited_content: editValue }),
            });
            await fetchReview();
            setIsEditing(false);
        } catch (err) {
            console.error('Edit error', err);
        } finally {
            setActionLoading(false);
        }
    };

    const saveComment = async () => {
        if (!selectedClause) return;
        setActionLoading(true);
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/api/documents/review/${documentId}/comment`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content_id: selectedClause.content_id, comment: commentValue }),
            });
            await fetchReview();
            setIsCommenting(false);
        } catch (err) {
            console.error('Comment error', err);
        } finally {
            setActionLoading(false);
        }
    };

    const handleAskLLM = async () => {
        if (!selectedClause) return;
        setLlmLoading(true);
        setLlmAnswer('');
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/review/${documentId}/ask-llm`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content_id: selectedClause.content_id,
                    question: 'Please analyze the risks and key differences of this client clause compared to a standard template, and suggest how it could be made more favorable.'
                }),
            });
            const d = await res.json();
            setLlmAnswer(d.answer || d.detail || 'No response');
        } catch (err) {
            setLlmAnswer('⚠️ Connection error');
        } finally {
            setLlmLoading(false);
        }
    };

    const handleDownloadRedline = async () => {
        setActionLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/download-redline/${documentId}`, {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (!res.ok) {
                const text = await res.text();
                throw new Error(text || 'Download failed');
            }
            const blob = await res.blob();

            // Get filename from Content-Disposition if available, or generate one
            const contentDisposition = res.headers.get('Content-Disposition');
            let filename = `Redlined_Document.docx`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                if (filenameMatch && filenameMatch.length === 2) {
                    filename = filenameMatch[1];
                }
            }

            // Create object URL and trigger download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('Download redline error', err);
            alert(`Failed to download redline document: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
    };

    // --- Render Helpers ---

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Clause Review">
            <div className="review-page master-detail-mode">

                {/* Header & Global Tab Filters */}
                <div className="md-header">
                    <button className="md-btn-back" onClick={() => navigate(-1)}>← Back</button>
                    <h2>Contract Clause Review</h2>

                    <div className="md-risk-tabs">
                        <button className={`tab-btn ${activeTab === 'All' ? 'active' : ''}`} onClick={() => setActiveTab('All')}>
                            All ({clauses.length})
                        </button>
                        {counts.High > 0 && <button className={`tab-btn high ${activeTab === 'High' ? 'active' : ''}`} onClick={() => setActiveTab('High')}>⊗ High Risk ({counts.High})</button>}
                        {counts.Medium > 0 && <button className={`tab-btn medium ${activeTab === 'Medium' ? 'active' : ''}`} onClick={() => setActiveTab('Medium')}>⚠ Medium Risk ({counts.Medium})</button>}
                        {counts.Low > 0 && <button className={`tab-btn low ${activeTab === 'Low' ? 'active' : ''}`} onClick={() => setActiveTab('Low')}>✓ Low Risk ({counts.Low})</button>}

                        <div style={{ paddingLeft: '2rem', display: 'flex' }}>
                            <button
                                className="btn-action"
                                style={{ backgroundColor: '#2563eb', color: 'white', padding: '0.4rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '500' }}
                                onClick={handleDownloadRedline}
                                disabled={actionLoading || isProcessing}
                            >
                                <span>📄</span> Download Redline (.docx)
                            </button>
                        </div>
                    </div>
                </div>

                <div className="md-layout">
                    {/* Left Sidebar Navigation */}
                    <div className="md-sidebar">
                        <h3 className="sidebar-title">Clauses</h3>
                        {filteredClauses.length === 0 ? (
                            <div className="sidebar-empty">
                                {isProcessing ? (
                                    <div style={{ textAlign: 'center', padding: '1rem' }}>
                                        <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
                                        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Analysing document…</p>
                                    </div>
                                ) : (
                                    <p>No clauses found.</p>
                                )}
                            </div>
                        ) : (
                            <div className="sidebar-list">
                                {filteredClauses.map(c => {
                                    const r = normalizeRisk(c.risk);
                                    const rc = RISK_CONFIG[r];
                                    const isSelected = selectedClause && selectedClause.content_id === c.content_id;
                                    return (
                                        <div
                                            key={c.content_id}
                                            className={`sidebar-item ${isSelected ? 'selected' : ''} risk-${rc.class}`}
                                            onClick={() => {
                                                setSelectedClauseId(c.content_id);
                                                setLlmAnswer('');
                                                setIsEditing(false);
                                                setIsCommenting(false);
                                            }}
                                        >
                                            <div className="item-lhs">
                                                <div className="item-title">{c.clause_type}</div>
                                                <div className="item-meta">Page {c.page_number}</div>
                                            </div>
                                            <div className={`item-risk-pill ${rc.class}`}>
                                                {r} Risk
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Right Detail Pane */}
                    <div className="md-detail">
                        {!selectedClause ? (
                            <div className="detail-empty">Select a clause from the sidebar to begin review.</div>
                        ) : (
                            <div className={`detail-card risk-${RISK_CONFIG[normalizeRisk(selectedClause.risk || 'High')].class}`}>

                                {/* Detail Header */}
                                <div className="detail-header">
                                    <div>
                                        <h3>{selectedClause.clause_type}</h3>
                                        <span className="detail-meta">Page {selectedClause.page_number}</span>
                                    </div>
                                    <div className="detail-status-area">
                                        <span className={`detail-risk-pill ${RISK_CONFIG[normalizeRisk(selectedClause.risk || 'High')].class}`}>
                                            {normalizeRisk(selectedClause.risk)} Risk
                                        </span>
                                        {selectedClause.similarity_score !== null && (
                                            <span className="detail-confidence">
                                                {Math.round(selectedClause.similarity_score * 100)}% match
                                            </span>
                                        )}
                                        {selectedClause.status === 'accepted' && (
                                            <span className="detail-approved-badge">✓ Approved</span>
                                        )}
                                    </div>
                                </div>

                                {/* Comparison Panes */}
                                <div className="comparison-box">

                                    {/* Left: Client Contract */}
                                    <div className="comp-pane upload-pane">
                                        <div className="pane-title">📄 Uploaded Contract</div>
                                        <div className="pane-content" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            <div className="clause-edit-section">
                                                {isEditing ? (
                                                    <div className="edit-mode-container">
                                                        <textarea
                                                            className="edit-textarea"
                                                            value={editValue}
                                                            onChange={e => setEditValue(e.target.value)}
                                                            rows={6}
                                                        />
                                                        <div className="edit-actions">
                                                            <button className="btn-save btn-small" onClick={saveEdit}>Save Edit</button>
                                                            <button className="btn-cancel btn-small" onClick={() => setIsEditing(false)}>Cancel</button>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="text-display">
                                                        {selectedClause.html_diff ? (
                                                            <span dangerouslySetInnerHTML={{ __html: selectedClause.html_diff }} />
                                                        ) : (
                                                            selectedClause.content
                                                        )}
                                                    </div>
                                                )}
                                            </div>

                                            <div className="clause-comment-section" style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
                                                <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#475569' }}>Legal Note / Comment:</div>
                                                {isCommenting ? (
                                                    <div className="comment-mode-container">
                                                        <textarea
                                                            className="comment-input"
                                                            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e1', minHeight: '60px', resize: 'vertical' }}
                                                            value={commentValue}
                                                            onChange={e => setCommentValue(e.target.value)}
                                                            placeholder="Add a comment..."
                                                        />
                                                        <div className="edit-actions" style={{ marginTop: '0.5rem' }}>
                                                            <button className="btn-save btn-small" onClick={saveComment}>Save Comment</button>
                                                            <button className="btn-cancel btn-small" onClick={() => {
                                                                setCommentValue(selectedClause.comment || '');
                                                                setIsCommenting(false);
                                                            }}>Cancel</button>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="clause-comment-display" style={{ padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '4px', border: '1px solid #e2e8f0', cursor: 'pointer' }} onClick={() => {
                                                        setCommentValue(selectedClause.comment || '');
                                                        setIsCommenting(true);
                                                    }}>
                                                        {selectedClause.comment ? (
                                                            <span>{selectedClause.comment}</span>
                                                        ) : (
                                                            <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>Add a comment...</span>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Right: Standard Clause */}
                                    <div className="comp-pane standard-pane">
                                        <div className="pane-title">📄 Standard Clause</div>
                                        <div className="pane-content">
                                            {selectedClause.matched_clause?.content || "No matching standard clause found via SBERT."}
                                        </div>
                                    </div>
                                </div>

                                {/* LLM Differences Box */}
                                <div className="differences-box">
                                    <div className="diff-header">
                                        <span className="diff-title">✨ AI Analysis & Differences</span>
                                        {!llmAnswer && !llmLoading && (
                                            <button className="btn-ask-llm-small" onClick={handleAskLLM}>
                                                Run Analysis
                                            </button>
                                        )}
                                    </div>
                                    <div className="diff-content">
                                        {llmLoading ? (
                                            <div className="spinner-small" />
                                        ) : llmAnswer ? (
                                            <p>{llmAnswer}</p>
                                        ) : selectedClause.llm_reasoning ? (
                                            <p>{selectedClause.llm_reasoning}</p>
                                        ) : (
                                            <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                                                Click "Run Analysis" to generate an on-demand AI assessment of risks and deviations.
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Bottom Action Bar */}
                                <div className="detail-actions">
                                    <div className="left-actions">
                                        <button
                                            className="btn-action btn-edit"
                                            onClick={() => {
                                                setEditValue(selectedClause.edited_content || selectedClause.content);
                                                setIsEditing(true);
                                                setIsCommenting(false);
                                            }}
                                            disabled={actionLoading}
                                        >
                                            ✏️ Edit Clause
                                        </button>
                                    </div>
                                    <div className="right-actions">
                                        {/* Reject explicitly removed by User Request */}
                                        <button
                                            className="btn-action btn-approve"
                                            onClick={() => handleAction('accept')}
                                            disabled={actionLoading || selectedClause.status === 'accepted'}
                                        >
                                            ✓ Approve
                                        </button>
                                    </div>
                                </div>

                            </div>
                        )}
                    </div>
                </div>

                <DocumentChatbot documentId={documentId} />
            </div>
        </Layout>
    );
}
