import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Profile({ onLogout }: { onLogout: () => void }) {
    const [user, setUser] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        api.get('/api/auth/me')
            .then(res => setUser(res.data))
            .catch(err => {
                console.error(err);
                if (err.response?.status === 401) {
                    onLogout();
                } else {
                    setError('Failed to load profile.');
                }
            });
    }, [onLogout]);

    if (error) return <div className="card"><h3 className="error-msg">{error}</h3></div>;
    if (!user) return <div>Loading...</div>;

    return (
        <div>
            <h2>My Profile</h2>
            <div className="card" style={{ maxWidth: '600px' }}>
                <p><strong>Name:</strong> {user.name}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Role:</strong> {user.role}</p>
                <p><strong>Account Status:</strong> {user.status}</p>
                <button className="btn btn-danger" style={{ marginTop: '1rem' }} onClick={onLogout}>Logout</button>
            </div>
        </div>
    );
}
