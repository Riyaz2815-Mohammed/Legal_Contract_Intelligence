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
                    <div></div> {/* Empty div to push actions to the right using flex space-between */}
                    <div className="header-actions">
                        <button className="header-btn" title="Search">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        </button>
                        <button className="header-btn notification-btn" title="Notifications">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                            <span className="notification-dot"></span>
                        </button>
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
