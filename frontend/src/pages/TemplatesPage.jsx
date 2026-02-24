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
        { id: 'RA', name: 'Referee Agreement (RA)', description: 'Standard agreement for referee services.' },
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
                                    <div className="template-icon">{type.id}</div>
                                    <h3>{type.name}</h3>
                                </div>
                                <p className="template-desc">{type.description}</p>

                                <div className="template-status-area">
                                    {active ? (
                                        <div className="active-template">
                                            <span className="status-label">Active:</span>
                                            <span className="template-name" title={active.filename}>
                                                {active.filename.length > 25 ? active.filename.substring(0, 22) + '...' : active.filename}
                                            </span>
                                            <span className="template-date">
                                                Updated: {new Date(active.uploaded_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    ) : (
                                        <div className="no-template">No template uploaded yet</div>
                                    )}
                                </div>

                                <div className="template-actions">
                                    <label className={`upload-btn ${uploading === type.id ? 'loading' : ''}`}>
                                        {uploading === type.id ? 'Uploading...' : (active ? 'Update Template' : 'Upload New')}
                                        <input
                                            type="file"
                                            accept=".pdf,.docx"
                                            onChange={(e) => handleUpload(type.id, e.target.files[0])}
                                            disabled={uploading !== null}
                                            hidden
                                        />
                                    </label>
                                    {active && (
                                        <div className="active-actions">
                                            <button
                                                onClick={() => handleDownloadRequest(active.id)}
                                                className="view-btn"
                                            >
                                                View Source
                                            </button>
                                        </div>
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
