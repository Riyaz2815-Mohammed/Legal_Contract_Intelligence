import { useState } from 'react';
import './Login.css';

const API_URL = 'http://localhost:8000';

function Login({ onLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [alert, setAlert] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setAlert(null);

        try {
            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                setAlert({ type: 'success', message: 'Login successful! Redirecting...' });
                setTimeout(() => {
                    onLogin(data.token, data.user);
                }, 1000);
            } else {
                setAlert({ type: 'error', message: data.detail || 'Invalid credentials' });
            }
        } catch (error) {
            setAlert({ type: 'error', message: 'Connection error. Please ensure the backend is running.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="logo">
                    <h1>LACCIS</h1>
                    <p>Legal Clause Classification Intelligence System</p>
                </div>

                <div className="glass-container">
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <input
                                type="email"
                                id="email"
                                className="form-control"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                className="form-control"
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {alert && (
                            <div className={`alert alert-${alert.type}`}>
                                <span>{alert.type === 'success' ? '✓' : '⚠'}</span>
                                <span>{alert.message}</span>
                            </div>
                        )}

                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    <span>Signing in...</span>
                                </>
                            ) : (
                                <span>Sign In</span>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Login;
