import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ user, onLogout, isCollapsed, onToggle }) => {
    return (
        <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                <div className="sidebar-logo" onClick={onToggle} title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}>
                    <div className="logo-icon-container">
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="32" height="32" rx="8" fill="#3B5998" />
                            <path d="M12 8C12 7.44772 12.4477 7 13 7H15C15.5523 7 16 7.44772 16 8V19H22C22.5523 19 23 19.4477 23 20V22C23 22.5523 22.5523 23 22 23H13C12.4477 23 12 22.5523 12 22V8Z" fill="white" />
                        </svg>
                    </div>
                    {!isCollapsed && <span className="logo-text">ACCIS</span>}
                </div>
            </div>

            <nav className="sidebar-nav">
                <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'} title="Dashboard">
                    <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    {!isCollapsed && <span>Dashboard</span>}
                </NavLink>

                {(user?.role === 'admin' || user?.role === 'legal_team') && (
                    <>
                        <NavLink to="/legal-team" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'} title="Legal Team">
                            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                            {!isCollapsed && <span>Legal Team</span>}
                        </NavLink>
                        <NavLink to="/invite-client" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'} title="Send Credentials">
                            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            {!isCollapsed && <span>Send Credentials</span>}
                        </NavLink>

                        <NavLink to="/templates" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'} title="Standard templates">
                            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            {!isCollapsed && <span>Standard templates</span>}
                        </NavLink>
                    </>
                )}
            </nav>

            <div className="sidebar-footer">
                <div className="user-info">
                    <div className="user-avatar">{user?.name?.charAt(0)}</div>
                    {!isCollapsed && (
                        <div className="user-details">
                            <span className="user-name">{user?.name}</span>
                            <span className="user-role">
                                {user?.role === 'legal_team' ? 'Legal Team' : user?.role}
                            </span>
                        </div>
                    )}
                </div>
                <button className="logout-btn" onClick={onLogout} title="Logout">
                    <svg className="logout-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    {!isCollapsed && <span>Logout</span>}
                </button>
            </div>
        </aside >
    );
};

export default Sidebar;
