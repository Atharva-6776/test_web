import { useEffect, useState } from 'react';
import { api } from '../api';
import { Link } from 'react-router-dom';

export default function Dashboard() {
    const [user, setUser] = useState<any>(null);
    const [stats, setStats] = useState({ products: 0, orders: 0 });
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const userRes = await api.get('/api/auth/me');
                setUser(userRes.data);
                
                const prodRes = await api.get('/api/products');
                const orderRes = await api.get('/api/orders');
                
                setStats({
                    products: prodRes.data.length,
                    orders: orderRes.data.length
                });
            } catch (err: any) {
                console.error(err);
                if (err.response?.status === 401) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('role');
                    window.location.href = '/login';
                } else {
                    setError('Failed to connect to backend server. Make sure the backend is running.');
                }
            }
        };
        fetchData();
    }, []);

    if (error) {
        return (
            <div className="card">
                <h3 className="error-msg">Connection / Auth Error</h3>
                <p>{error}</p>
                <button className="btn" onClick={() => { localStorage.clear(); window.location.href = '/login'; }}>
                    Go to Login
                </button>
            </div>
        );
    }

    if (!user) return <div>Loading...</div>;

    return (
        <div>
            <h2>Dashboard</h2>
            <div className="card">
                <h3>Welcome, {user.name}</h3>
                <p>Email: {user.email}</p>
                <p>Role: {user.role}</p>
                <p>Status: {user.status}</p>
            </div>
            
            <div className="grid" style={{ marginTop: '2rem' }}>
                <div className="card">
                    <h3>Total Products</h3>
                    <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.products}</p>
                    <Link to="/products" className="btn" style={{textDecoration:'none', display: 'inline-block'}}>View Products</Link>
                </div>
                <div className="card">
                    <h3>My Orders</h3>
                    <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.orders}</p>
                    <Link to="/orders" className="btn" style={{textDecoration:'none', display: 'inline-block'}}>View Orders</Link>
                </div>
                {user.role === 'ADMIN' && (
                    <div className="card">
                        <h3>Admin Panel</h3>
                        <p>Manage application settings</p>
                        <Link to="/admin" className="btn" style={{textDecoration:'none', display: 'inline-block'}}>Go to Admin</Link>
                    </div>
                )}
            </div>
        </div>
    );
}
