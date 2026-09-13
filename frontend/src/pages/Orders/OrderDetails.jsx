import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { toast } from "react-toastify";

import {
    cancelOrder,
    getOrder,
} from "../../services/orderService";
import RefundRequestForm from "../../components/Orders/RefundRequestForm";
import OrderStatusHistory from "../../components/Orders/OrderStatusHistory";
import CustomerOrderTimeline from "../../components/Orders/CustomerOrderTimeline";

const API_BASE_URL = "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://placehold.co/96x96?text=No+Image";

const formatDateTime = (value) => (
    value ? new Date(value).toLocaleString() : "-"
);

const formatMoney = (value) => (
    `৳${Number(value || 0).toFixed(2)}`
);

const getImageUrl = (image) => {
    if (!image) return FALLBACK_IMAGE;
    return image.startsWith("http") ? image : `${API_BASE_URL}${image}`;
};

const DetailRow = ({ label, value }) => (
    <div className="d-flex justify-content-between gap-3 border-bottom py-2">
        <span className="text-muted">{label}</span>
        <strong className="text-end">{value || "-"}</strong>
    </div>
);

const OrderDetails = () => {
    const { orderId } = useParams();
    const [order, setOrder] = useState(null);
    const [error, setError] = useState("");
    const [cancelling, setCancelling] = useState(false);
    const [showCancellationFlow, setShowCancellationFlow] = useState(false);
    const [cancellationReason, setCancellationReason] = useState("");
    const [cancellationError, setCancellationError] = useState("");

    const loadOrder = useCallback(async () => {
        try {
            const response = await getOrder(orderId);
            setOrder(response.data);
            setError("");
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to load order details."
            );
        }
    }, [orderId]);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void loadOrder();
        }, 0);

        return () => window.clearTimeout(timer);
    }, [loadOrder]);

    const openCancellationFlow = () => {
        setCancellationError("");
        setCancellationReason("");
        setShowCancellationFlow(true);
    };

    const handleCancel = async () => {
        if (!order?.can_cancel || cancelling) return;
        if (!cancellationReason) {
            setCancellationError("Select a reason before confirming cancellation.");
            return;
        }

        if (!window.confirm(`Cancel this order because: ${cancellationReason}?`)) return;

        try {
            setCancelling(true);
            setCancellationError("");
            await cancelOrder(order.id);
            toast.success("Order cancelled successfully.");
            setShowCancellationFlow(false);
            await loadOrder();
        } catch (requestError) {
            const message = requestError.response?.data?.detail || "Failed to cancel order.";
            setCancellationError(message);
            toast.error(message);
        } finally {
            setCancelling(false);
        }
    };

    const cancellationEligibilityMessage = () => {
        if (order?.can_cancel) return "This order is currently eligible for cancellation.";
        if (order?.status === "Cancelled") return "This order has already been cancelled.";
        if (order?.status === "Delivered") return "Delivered orders cannot be cancelled.";
        if (!["Pending", "Accepted"].includes(order?.status)) {
            return "This order can no longer be cancelled at its current status.";
        }
        return "This order is outside the cancellation policy or has a payment restriction.";
    };

    return (
        <div className="container py-4">
            <Link to="/orders" className="btn btn-outline-secondary mb-3">Back to Orders</Link>
            {error && <div className="alert alert-danger">{error}</div>}
            {!order && !error && (
                <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status" />
                    <p className="text-muted mt-3 mb-0">Loading order details...</p>
                </div>
            )}
            {order && (
                <>
                    <div className="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
                        <div>
                            <h2 className="mb-1">Order #{order.id}</h2>
                            <p className="text-muted mb-0">Placed {formatDateTime(order.created_at)}</p>
                        </div>
                        <span className="badge bg-primary fs-6">{order.status}</span>
                    </div>

                    <CustomerOrderTimeline order={order} />

                    <div className="row g-4 mt-1">
                        <div className="col-lg-7">
                            <div className="card border-0 shadow-sm h-100">
                                <div className="card-header bg-white fw-bold">Items</div>
                                <div className="list-group list-group-flush">
                                    {(order.items || []).map((item) => (
                                        <div className="list-group-item" key={item.id}>
                                            <div className="d-flex gap-3 align-items-center">
                                                <img
                                                    src={getImageUrl(item.product_image)}
                                                    alt={item.product_name}
                                                    width="72"
                                                    height="72"
                                                    className="rounded object-fit-cover"
                                                    onError={(event) => { event.currentTarget.src = FALLBACK_IMAGE; }}
                                                />
                                                <div className="flex-grow-1">
                                                    <div className="fw-semibold">{item.product_name}</div>
                                                    <div className="small text-muted">Quantity: {item.quantity}</div>
                                                </div>
                                                <div className="text-end">
                                                    <div className="small text-muted">{formatMoney(item.price)} each</div>
                                                    <strong>{formatMoney(item.subtotal)}</strong>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="col-lg-5">
                            <div className="card border-0 shadow-sm mb-4">
                                <div className="card-header bg-white fw-bold">Order summary</div>
                                <div className="card-body">
                                    <DetailRow label="Order date" value={formatDateTime(order.created_at)} />
                                    <DetailRow label="Payment method" value={order.payment_method} />
                                    <DetailRow label="Payment status" value={order.payment_status || "-"} />
                                    <DetailRow label="Order status" value={order.status} />
                                    <DetailRow label="Subtotal" value={formatMoney(order.subtotal)} />
                                    <DetailRow label="Delivery charge" value={formatMoney(order.delivery_charge)} />
                                    <div className="d-flex justify-content-between pt-3">
                                        <strong>Total</strong>
                                        <strong>{formatMoney(order.total_amount)}</strong>
                                    </div>
                                </div>
                            </div>

                            <div className="card border-0 shadow-sm">
                                <div className="card-header bg-white fw-bold">Cancellation and refund</div>
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-center gap-3 mb-3">
                                        <span>Cancellation</span>
                                        <span className={`badge ${order.can_cancel ? "bg-warning text-dark" : "bg-secondary"}`}>
                                            {order.can_cancel ? "Eligible" : "Not eligible"}
                                        </span>
                                    </div>
                                    {order.can_cancel && (
                                        <button type="button" className="btn btn-outline-danger btn-sm mb-3" onClick={openCancellationFlow} disabled={cancelling}>
                                            Cancel Order
                                        </button>
                                    )}
                                    <p className={`small ${order.can_cancel ? "text-success" : "text-muted"}`}>
                                        {cancellationEligibilityMessage()}
                                    </p>
                                    {showCancellationFlow && order.can_cancel && (
                                        <div className="border rounded p-3 mt-2">
                                            <div className="small text-muted mb-2">Step 1 of 3: Eligibility confirmed by the server.</div>
                                            <label className="form-label" htmlFor="cancellation-reason">Step 2 of 3: Why are you cancelling?</label>
                                            <select
                                                id="cancellation-reason"
                                                className="form-select mb-3"
                                                value={cancellationReason}
                                                onChange={(event) => {
                                                    setCancellationReason(event.target.value);
                                                    setCancellationError("");
                                                }}
                                                disabled={cancelling}
                                            >
                                                <option value="">Select a reason</option>
                                                <option value="I placed the order by mistake">I placed the order by mistake</option>
                                                <option value="I no longer need the items">I no longer need the items</option>
                                                <option value="I need to change the order">I need to change the order</option>
                                                <option value="Other">Other</option>
                                            </select>
                                            {cancellationError && <div className="alert alert-danger py-2">{cancellationError}</div>}
                                            <div className="small text-muted mb-2">Step 3 of 3: The backend will re-check eligibility before cancelling.</div>
                                            <div className="d-flex gap-2">
                                                <button type="button" className="btn btn-danger btn-sm" onClick={handleCancel} disabled={cancelling}>
                                                    {cancelling ? "Cancelling..." : "Confirm Cancellation"}
                                                </button>
                                                <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setShowCancellationFlow(false)} disabled={cancelling}>
                                                    Keep Order
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                    <div className="d-flex justify-content-between align-items-center gap-3">
                                        <span>Refund status</span>
                                        <strong>{order.refund_status || "No refund requested"}</strong>
                                    </div>
                                    {order.refund_deadline && !order.refund_window_expired && (
                                        <p className="small text-muted mt-2 mb-2">
                                            Refund requests are accepted until {formatDateTime(order.refund_deadline)}.
                                        </p>
                                    )}
                                    {order.refund_window_expired && !order.refund_status && (
                                        <div className="alert alert-secondary mt-3 mb-0">
                                            The 72-hour refund window has expired. New refund requests are no longer available for this order.
                                        </div>
                                    )}
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
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row g-4 mt-1">
                        <div className="col-lg-6">
                            <div className="card border-0 shadow-sm h-100">
                                <div className="card-header bg-white fw-bold">Delivery information</div>
                                <div className="card-body">
                                    <DetailRow label="Delivery status" value={order.delivery_status || "Not assigned"} />
                                    <DetailRow label="Assigned" value={formatDateTime(order.delivery_timestamps?.assigned_at)} />
                                    <DetailRow label="Picked up" value={formatDateTime(order.delivery_timestamps?.picked_up_at)} />
                                    <DetailRow label="Out for delivery" value={formatDateTime(order.delivery_timestamps?.out_for_delivery_at)} />
                                    <DetailRow label="Delivered" value={formatDateTime(order.delivery_timestamps?.delivered_at)} />
                                    <div className="mt-3"><span className="text-muted">Shipping address</span><div className="mt-1">{order.shipping_address || "-"}</div></div>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-6">
                            <div className="card border-0 shadow-sm h-100">
                                <div className="card-header bg-white fw-bold">Rider information</div>
                                <div className="card-body">
                                    {order.rider_name ? (
                                        <>
                                            <DetailRow label="Rider" value={order.rider_name} />
                                            <DetailRow label="Delivery status" value={order.delivery_status} />
                                        </>
                                    ) : (
                                        <p className="text-muted mb-0">Rider information will appear after delivery assignment.</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    <OrderStatusHistory history={order.history} />
                </>
            )}
        </div>
    );
};

export default OrderDetails;
