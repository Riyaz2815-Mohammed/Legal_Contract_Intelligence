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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                setAlert({ type: 'success', message: 'Signed in successfully. Welcome back!' });
                setTimeout(() => {
                    onLogin(data.token, data.user);
                }, 800);
            } else {
                setAlert({ type: 'error', message: data.detail || 'Invalid credentials' });
            }
        } catch (error) {
            setAlert({ type: 'error', message: 'Connection error. Is the backend running?' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="logo-section">
                    <div className="logo-icon">L</div>
                    <h1>LACCIS</h1>
                    <p>Legal Clause Classification Intelligence System</p>
                </div>

                <div className="login-card">
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <input
                                type="email"
                                id="email"
                                className="input-field"
                                placeholder="name@company.com"
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
                                className="input-field"
                                placeholder="••••••••"
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

                        <button type="submit" className="btn-login" disabled={loading}>
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    <span>Verifying...</span>
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
