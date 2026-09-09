import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";
import { getOrder } from "../../services/orderService";
import RefundRequestForm from "../../components/Orders/RefundRequestForm";
import OrderStatusHistory from "../../components/Orders/OrderStatusHistory";
import CustomerOrderTimeline from "../../components/Orders/CustomerOrderTimeline";

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
                        <CustomerOrderTimeline order={order} />
                        <div className="card border-0 shadow-sm p-4">
                            <p><strong>Status:</strong> {order.status}</p>
                            <p><strong>Payment:</strong> {order.payment_status || order.payment_method}</p>
                            <p><strong>Shipping address:</strong> {order.shipping_address}</p>
                            <p className="mb-0"><strong>Total:</strong> ৳{order.total_amount}</p>
                            {order.can_request_refund && (
                                <RefundRequestForm
                                    orderId={order.id}
                                    order={order}
                                    onSubmitted={() => setOrder({
                                        ...order,
                                        can_request_refund: false,
                                        refund_status: "Pending",
                                    })}
                                />
                            )}
                            {order.refund_status && (
                                <p className="mt-3 mb-0">
                                    <strong>Refund Status:</strong> {order.refund_status}
                                </p>
                            )}
                        </div>
                        <OrderStatusHistory history={order.history} />
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
