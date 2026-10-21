import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Products() {
    const [products, setProducts] = useState<any[]>([]);

    useEffect(() => {
        api.get('/api/products').then(res => setProducts(res.data)).catch(console.error);
    }, []);

    const handleOrder = async (productId: number) => {
        try {
            await api.post('/api/orders', { product_id: productId, quantity: 1 });
            alert('Order placed successfully!');
        } catch (err) {
            alert('Failed to place order');
        }
    };

    return (
        <div>
            <h2>Products</h2>
            <div className="grid">
                {products.map(p => (
                    <div key={p.id} className="card">
                        <h3>{p.name}</h3>
                        <p>{p.description}</p>
                        <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#2563eb' }}>${p.price.toFixed(2)}</p>
                        <p style={{ color: '#64748b' }}>Stock: {p.stock}</p>
                        <button className="btn" onClick={() => handleOrder(p.id)}>Order Now</button>
                    </div>
                ))}
            </div>
        </div>
    );
}
