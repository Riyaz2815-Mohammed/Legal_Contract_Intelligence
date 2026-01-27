import './Navbar.css';

function Navbar({ user, onLogout, title = "LACCIS Dashboard" }) {
    const getInitials = (name) => {
        return name ? name.substring(0, 2).toUpperCase() : 'U';
    };

    return (
        <nav className="navbar">
            <h2>{title}</h2>
            <div className="user-info">
                <span>{user?.name || 'User'}</span>
                <div className="user-avatar">{getInitials(user?.name)}</div>
                <button className="btn btn-secondary" onClick={onLogout}>
                    Logout
                </button>
            </div>
        </nav>
    );
}

export default Navbar;
