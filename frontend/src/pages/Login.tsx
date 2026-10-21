import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { jwtDecode } from "jwt-decode";

export default function Login({ setRole }: { setRole: (role: string) => void }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await api.post('/api/auth/login', { email, password });
            const token = res.data.access_token;
            localStorage.setItem('token', token);
            
            const decoded: any = jwtDecode(token);
            localStorage.setItem('role', decoded.role);
            setRole(decoded.role);
            
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <div className="card" style={{ maxWidth: '400px', margin: '4rem auto' }}>
            <h2>Login</h2>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Email</label>
                    <input 
                        type="email" 
                        className="form-control" 
                        value={email} 
                        onChange={e => setEmail(e.target.value)} 
                        required 
                    />
                </div>
                <div className="form-group">
                    <label>Password</label>
                    <input 
                        type="password" 
                        className="form-control" 
                        value={password} 
                        onChange={e => setPassword(e.target.value)} 
                        required 
                    />
                </div>
                <button type="submit" className="btn" style={{ width: '100%' }}>Login</button>
            </form>
            <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#64748b' }}>
                <p>Test Accounts:</p>
                <p>admin@test.com / Admin@123</p>
                <p>user@test.com / User@123</p>
            </div>
        </div>
    );
}
