import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import './Layout.css';

const Layout = ({ user, onLogout, children, pageTitle = 'Dashboard' }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div className={`layout-container ${isCollapsed ? 'sidebar-collapsed' : ''}`}>
            <Sidebar
                user={user}
                onLogout={onLogout}
                isCollapsed={isCollapsed}
                onToggle={() => setIsCollapsed(!isCollapsed)}
            />
            <main className="main-content">
                <header className="content-header">
                    <div className="breadcrumb">
                        <span className="breadcrumb-item">LACCIS</span>
                        <span className="breadcrumb-separator">/</span>
                        <span className="breadcrumb-item active">{pageTitle}</span>
                    </div>
                </header>
                <div className="scrollable-content">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
