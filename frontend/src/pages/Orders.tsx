import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Orders() {
    const [orders, setOrders] = useState<any[]>([]);

    useEffect(() => {
        api.get('/api/orders').then(res => setOrders(res.data)).catch(console.error);
    }, []);

    return (
        <div>
            <h2>Orders</h2>
            <div className="card">
                {orders.length === 0 ? <p>No orders found.</p> : (
                    <table>
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Total</th>
                                <th>Status</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {orders.map(o => (
                                <tr key={o.id}>
                                    <td>#{o.id}</td>
                                    <td>{o.product.name}</td>
                                    <td>{o.quantity}</td>
                                    <td>${o.total.toFixed(2)}</td>
                                    <td>{o.status}</td>
                                    <td>{new Date(o.created_at).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
