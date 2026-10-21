import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Orders from './pages/Orders';
import Profile from './pages/Profile';
import Admin from './pages/Admin';

const Navbar = ({ role, onLogout }: { role: string | null, onLogout: () => void }) => {
    return (
        <nav className="navbar">
            <Link to="/dashboard" className="navbar-brand">SecureShop Test</Link>
            <div className="nav-links">
                {role ? (
                    <>
                        <Link to="/dashboard">Dashboard</Link>
                        <Link to="/products">Products</Link>
                        <Link to="/orders">Orders</Link>
                        <Link to="/profile">Profile</Link>
                        {role === 'ADMIN' && <Link to="/admin">Admin</Link>}
                        <a href="#" onClick={onLogout}>Logout</a>
                    </>
                ) : (
                    <Link to="/login">Login</Link>
                )}
            </div>
        </nav>
    );
};

const ProtectedRoute = ({ children, roleRequired }: { children: React.ReactNode, roleRequired?: string }) => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (!token) return <Navigate to="/login" />;
    
    if (roleRequired && role !== roleRequired) {
        return (
            <div className="container">
                <div className="card">
                    <h2 className="error-msg">Access Denied</h2>
                    <p>You do not have permission to access this page.</p>
                </div>
            </div>
        );
    }
    return <>{children}</>;
};

function App() {
    const [role, setRole] = useState<string | null>(localStorage.getItem('role'));

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        setRole(null);
        window.location.href = '/login';
    };

    useEffect(() => {
        const handleStorageChange = () => {
            setRole(localStorage.getItem('role'));
        };
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    return (
        <BrowserRouter>
            <Navbar role={role} onLogout={handleLogout} />
            <div className="container">
                <Routes>
                    <Route path="/login" element={<Login setRole={setRole} />} />
                    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
                    <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProtectedRoute><Profile onLogout={handleLogout}/></ProtectedRoute>} />
                    <Route path="/admin" element={<ProtectedRoute roleRequired="ADMIN"><Admin /></ProtectedRoute>} />
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;
