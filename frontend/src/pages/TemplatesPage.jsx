import React, { useState, useEffect } from 'react';
import Layout from '../layouts/Layout';
import './TemplatesPage.css';

const API_URL = 'http://localhost:8000';

const TemplatesPage = ({ user, onLogout }) => {
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(null); // type being uploaded

    const templateTypes = [
        { id: 'NDA', name: 'Non-Disclosure Agreement (NDA)', description: 'Confidentiality agreement for preliminary discussions.' },
        { id: 'RA', name: 'Referral Agreement (RA)', description: 'Standard agreement for referral services.' },
        { id: 'SOW', name: 'Statement of Work (SOW)', description: 'Detailed project scope and deliverables document.' },
        { id: 'MSA', name: 'Master Service Agreement (MSA)', description: 'Overarching terms for ongoing services.' }
    ];

    const loadTemplates = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/templates/list`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (res.ok) {
                setTemplates(data.templates || []);
            }
        } catch (err) {
            console.error('Error loading templates:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTemplates();
    }, []);

    const handleUpload = async (type, file) => {
        if (!file) return;
        setUploading(type);
        try {
            const token = localStorage.getItem('token');
            const formData = new FormData();
            formData.append('file', file);
            formData.append('template_type', type);

            const res = await fetch(`${API_URL}/api/templates/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });

            if (res.ok) {
                loadTemplates();
                alert(`${type} template uploaded successfully!`);
            } else {
                const data = await res.json();
                alert(`Upload failed: ${data.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('Upload error:', err);
            alert('Upload failed due to a network error.');
        } finally {
            setUploading(null);
        }
    };

    const getActiveTemplate = (type) => {
        // Return the latest template for this type
        const filtered = templates.filter(t => t.template_type === type);
        if (filtered.length === 0) return null;
        return filtered.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at))[0];
    };

    const handleDownloadRequest = async (templateId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/templates/download/${templateId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.download_url) {
                window.open(data.download_url, '_blank');
            } else {
                alert('Template download failed');
            }
        } catch (err) {
            console.error('Download error:', err);
            alert('Connection error');
        }
    };

    return (
        <Layout user={user} onLogout={onLogout} pageTitle="Standard Templates">
            <div className="templates-container">
                <div className="templates-header">
                    <h1>Standard Legal Templates</h1>
                    <p>Manage and upload standard document templates for all legal workspaces.</p>
                </div>

                <div className="templates-grid">
                    {templateTypes.map(type => {
                        const active = getActiveTemplate(type.id);
                        return (
                            <div key={type.id} className="template-card">
                                <div className="template-card-header">
                                    <div className="template-icon">
                                        <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <div className="template-header-text">
                                        <h3>{type.name}</h3>
                                        <span className="template-id-badge">{type.id}</span>
                                    </div>
                                </div>
                                <p className="template-desc">{type.description}</p>

                                <div className="template-status-area">
                                    {active ? (
                                        <div className="active-template">
                                            <div className="active-template-header">
                                                <div className="status-badge">
                                                    <svg style={{ width: '14px', height: '14px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                    Active Version
                                                </div>
                                                <span className="template-date">
                                                    Updated {new Date(active.uploaded_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                            <div className="template-filename-box">
                                                <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                                                <span className="template-name" title={active.filename}>
                                                    {active.filename.length > 25 ? active.filename.substring(0, 22) + '...' : active.filename}
                                                </span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="no-template-box">
                                            <svg style={{ width: '32px', height: '32px', margin: '0 auto 0.5rem', color: '#cbd5e1' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                                            No template uploaded yet
                                        </div>
                                    )}
                                </div>

                                <div className="template-actions">
                                    <label className={`btn-upload ${uploading === type.id ? 'loading' : ''}`}>
                                        <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                                        {uploading === type.id ? 'Uploading...' : (active ? 'Upload New Version' : 'Upload Template')}
                                        <input
                                            type="file"
                                            accept=".pdf,.docx"
                                            onChange={(e) => handleUpload(type.id, e.target.files[0])}
                                            disabled={uploading !== null}
                                            hidden
                                        />
                                    </label>
                                    {active && (
                                        <button
                                            onClick={() => handleDownloadRequest(active.id)}
                                            className="btn-secondary-action"
                                        >
                                            <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                                            View
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </Layout>
    );

};

export default TemplatesPage;
