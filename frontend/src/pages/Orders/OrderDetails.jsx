import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";
import { getOrder } from "../../services/orderService";

const ORDER_STEPS = [
    "Pending",
    "Accepted",
    "Processing",
    "Ready",
    "Assigned",
    "Out for Delivery",
    "Delivered",
];

const OrderDetails = () => {
    const { orderId } = useParams();
    const [order, setOrder] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        getOrder(orderId)
            .then((response) => setOrder(response.data))
            .catch((requestError) => setError(
                requestError.response?.data?.detail ||
                "Failed to load order details."
            ));
    }, [orderId]);

    return (
        <MainLayout>
            <div className="container py-4">
                <Link to="/orders" className="btn btn-outline-secondary mb-3">Back to Orders</Link>
                {error && <div className="alert alert-danger">{error}</div>}
                {!order && !error && <div>Loading order...</div>}
                {order && (
                    <>
                        <h2>Order #{order.id}</h2>
                        <p className="text-muted">Track your order status and delivery progress.</p>
                        <div className="d-flex flex-wrap gap-2 mb-4">
                            {ORDER_STEPS.map((step) => (
                                <span key={step} className={`badge ${step === order.status ? "bg-primary" : "bg-light text-dark"}`}>
                                    {step}
                                </span>
                            ))}
                        </div>
                        <div className="card border-0 shadow-sm p-4">
                            <p><strong>Status:</strong> {order.status}</p>
                            <p><strong>Payment:</strong> {order.payment_status || order.payment_method}</p>
                            <p><strong>Shipping address:</strong> {order.shipping_address}</p>
                            <p className="mb-0"><strong>Total:</strong> ৳{order.total_amount}</p>
                        </div>
                        <div className="card border-0 shadow-sm mt-4">
                            <div className="card-header">Items</div>
                            <ul className="list-group list-group-flush">
                                {(order.items || []).map((item) => (
                                    <li className="list-group-item d-flex justify-content-between" key={item.id}>
                                        <span>{item.product_name} x {item.quantity}</span>
                                        <span>৳{item.subtotal}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </>
                )}
            </div>
        </MainLayout>
    );
};

export default OrderDetails;
