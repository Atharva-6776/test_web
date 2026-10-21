import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Admin() {
    const [data, setData] = useState<any>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        api.get('/api/admin/dashboard')
           .then(res => setData(res.data))
           .catch(err => setError(err.response?.data?.detail || 'Access denied'));
    }, []);

    if (error) return <div className="card"><h2 className="error-msg">Access Denied</h2><p>{error}</p></div>;
    if (!data) return <div>Loading...</div>;

    return (
        <div>
            <h2>Admin Dashboard</h2>
            <div className="grid">
                {Object.entries(data).map(([key, value]: any) => (
                    <div key={key} className="card">
                        <h3>{key}</h3>
                        <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{value}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
