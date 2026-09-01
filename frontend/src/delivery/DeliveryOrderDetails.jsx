import React, { useEffect, useState } from "react";

import { Link, useNavigate, useParams } from "react-router-dom";

import deliveryService from "../services/deliveryService";

import "./delivery.css";

// ==========================================================
// DELIVERY ORDER DETAILS
// ==========================================================

const DeliveryOrderDetails = () => {

    const { orderId } = useParams();

    const navigate = useNavigate();

    const [order, setOrder] = useState(null);

    const [loading, setLoading] = useState(true);

    const [updating, setUpdating] = useState(false);

    const [error, setError] = useState("");

    const [success, setSuccess] = useState("");

    // ======================================================
    // LOAD ORDER
    // ======================================================

    const loadOrder = async () => {

        try {

            setLoading(true);
            setError("");

            const data = await deliveryService.getOrderDetails(orderId);

            setOrder(data);

        } catch (err) {

            console.error("Order details error:", err);

            setError(
                err.response?.data?.detail || "Failed to load order."
            );

        } finally {

            setLoading(false);
        }
    };

    useEffect(() => {

        loadOrder();

    }, [orderId]);

    // ======================================================
    // UPDATE STATUS
    // ======================================================

    const handleStatusUpdate = async (newStatus) => {

        try {

            setUpdating(true);
            setError("");
            setSuccess("");

            const data = await deliveryService.updateStatus(orderId, newStatus);

            setSuccess(
                data.message || "Delivery status updated successfully."
            );

            await loadOrder();

        } catch (err) {

            console.error("Status update error:", err);

            setError(
                err.response?.data?.detail || "Failed to update delivery status."
            );

        } finally {

            setUpdating(false);
        }
    };

    // ======================================================
    // NEXT STATUS
    // ======================================================

    const getNextStatus = (status) => {

        const workflow = {

            ASSIGNED: "ACCEPTED",
            ACCEPTED: "PICKED_UP",
            PICKED_UP: "OUT_FOR_DELIVERY",
            OUT_FOR_DELIVERY: "DELIVERED",
        };

        return workflow[status] || null;
    };

    // ======================================================
    // STATUS LABEL
    // ======================================================

    const formatStatus = (status) => {

        if (!status) {
            return "Unknown";
        }

        return status
            .replaceAll("_", " ")
            .replace(/\b\w/g, (char) => char.toUpperCase());
    };

    // ======================================================
    // LOADING
    // ======================================================

    if (loading) {

        return (
            <div className="delivery-page">

                <div className="delivery-loading">
                    Loading order...
                </div>

            </div>
        );
    }

    // ======================================================
    // ERROR
    // ======================================================

    if (error && !order) {

        return (
            <div className="delivery-page">

                <div className="delivery-error">
                    {error}
                </div>

                <button
                    className="delivery-btn"
                    onClick={() => navigate("/delivery/orders")}
                >
                    Back to Deliveries
                </button>

            </div>
        );
    }

    const currentStatus = order?.status || "ASSIGNED";

    const nextStatus = getNextStatus(currentStatus);

    // ======================================================
    // PAGE
    // ======================================================

    return (
        <div className="delivery-page">

            {/* ============================================ */}
            {/* HEADER */}
            {/* ============================================ */}

            <div className="delivery-header">

                <div>

                    <h1>
                        ORDER #
                        {order?.order_id || order?.id}
                    </h1>

                    <p>
                        Delivery details
                    </p>

                </div>

                <Link
                    to="/delivery/orders"
                    className="delivery-header-btn"
                >
                    Back
                </Link>

            </div>

            {/* ============================================ */}
            {/* MESSAGES */}
            {/* ============================================ */}

            {success && (

                <div className="delivery-success">
                    {success}
                </div>

            )}

            {error && (

                <div className="delivery-error">
                    {error}
                </div>

            )}

            {/* ============================================ */}
            {/* STATUS */}
            {/* ============================================ */}

            <div className="delivery-details-card">

                <div className="details-header">

                    <div>

                        <h2>
                            Delivery Status
                        </h2>

                    </div>

                    <span
                        className={
                            `status-badge status-${String(currentStatus)
                                .toLowerCase()
                                .replaceAll("_", "-")}`
                        }
                    >
                        {formatStatus(currentStatus)}
                    </span>

                </div>

                {/* ======================================== */}
                {/* STATUS WORKFLOW */}
                {/* ======================================== */}

                <div className="delivery-workflow">

                    <div
                        className={
                            currentStatus === "ASSIGNED"
                                ? "workflow-step active"
                                : "workflow-step completed"
                        }
                    >
                        <span>1</span>
                        <p>Assigned</p>
                    </div>

                    <div className="workflow-line" />

                    <div
                        className={
                            currentStatus === "ACCEPTED"
                                ? "workflow-step active"
                                : ["PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED"].includes(
                                    currentStatus
                                )
                                    ? "workflow-step completed"
                                    : "workflow-step"
                        }
                    >
                        <span>2</span>
                        <p>Accepted</p>
                    </div>

                    <div className="workflow-line" />

                    <div
                        className={
                            currentStatus === "PICKED_UP"
                                ? "workflow-step active"
                                : ["OUT_FOR_DELIVERY", "DELIVERED"].includes(
                                    currentStatus
                                )
                                    ? "workflow-step completed"
                                    : "workflow-step"
                        }
                    >
                        <span>3</span>
                        <p>Picked Up</p>
                    </div>

                    <div className="workflow-line" />

                    <div
                        className={
                            currentStatus === "OUT_FOR_DELIVERY"
                                ? "workflow-step active"
                                : currentStatus === "DELIVERED"
                                    ? "workflow-step completed"
                                    : "workflow-step"
                        }
                    >
                        <span>4</span>
                        <p>Out for Delivery</p>
                    </div>

                    <div className="workflow-line" />

                    <div
                        className={
                            currentStatus === "DELIVERED"
                                ? "workflow-step completed"
                                : "workflow-step"
                        }
                    >
                        <span>5</span>
                        <p>Delivered</p>
                    </div>

                </div>

                {/* ======================================== */}
                {/* NEXT ACTION */}
                {/* ======================================== */}

                {nextStatus && (

                    <div className="next-action">

                        <p>
                            Next action
                        </p>

                        <button
                            className="delivery-status-btn"
                            disabled={updating}
                            onClick={() => handleStatusUpdate(nextStatus)}
                        >

                            {updating
                                ? "Updating..."
                                : `Mark as ${formatStatus(nextStatus)}`}

                        </button>

                    </div>

                )}

                {currentStatus === "DELIVERED" && (

                    <div className="delivered-message">
                        ✓ Delivery completed successfully.
                    </div>

                )}

            </div>

            {/* ============================================ */}
            {/* CUSTOMER INFORMATION */}
            {/* ============================================ */}

            <div className="delivery-details-grid">

                <div className="delivery-details-card">

                    <h2>
                        Customer Information
                    </h2>

                    <div className="detail-row">

                        <strong>
                            Name
                        </strong>

                        <span>
                            {order?.customer_name || "N/A"}
                        </span>

                    </div>

                    <div className="detail-row">

                        <strong>
                            Email
                        </strong>

                        <span>
                            {order?.customer_email || "N/A"}
                        </span>

                    </div>

                    {order?.customer_phone && (

                        <div className="detail-row">

                            <strong>
                                Phone
                            </strong>

                            <span>
                                {order.customer_phone}
                            </span>

                        </div>

                    )}

                </div>

                {/* ======================================== */}
                {/* ADDRESS */}
                {/* ======================================== */}

                <div className="delivery-details-card">

                    <h2>
                        Delivery Address
                    </h2>

                    <div className="address-box">

                        📍

                        <span>
                            {order?.shipping_address || order?.address || "Address not available"}
                        </span>

                    </div>

                </div>

            </div>

            {/* ============================================ */}
            {/* ORDER INFORMATION */}
            {/* ============================================ */}

            <div className="delivery-details-card">

                <h2>
                    Order Information
                </h2>

                <div className="detail-row">

                    <strong>
                        Order ID
                    </strong>

                    <span>
                        #{order?.order_id || order?.id}
                    </span>

                </div>

                <div className="detail-row">

                    <strong>
                        Payment Method
                    </strong>

                    <span>
                        {order?.payment_method || "N/A"}
                    </span>

                </div>

                <div className="detail-row">

                    <strong>
                        Total Amount
                    </strong>

                    <span>
                        ৳{order?.total_amount || "0.00"}
                    </span>

                </div>

            </div>

            {/* ============================================ */}
            {/* ORDER ITEMS */}
            {/* ============================================ */}

            <div className="delivery-details-card">

                <h2>
                    Order Items
                </h2>

                {order?.items?.length > 0 ? (

                    <div className="delivery-items">

                        {order.items.map((item) => (

                            <div
                                className="delivery-item"
                                key={item.id}
                            >

                                <div>

                                    <strong>
                                        {item.product_name || item.name || "Product"}
                                    </strong>

                                    <span>
                                        Quantity: {item.quantity}
                                    </span>

                                </div>

                                <strong>
                                    ৳
                                    {item.subtotal || (
                                        Number(item.price || 0) * Number(item.quantity || 0)
                                    ).toFixed(2)}
                                </strong>

                            </div>

                        ))}

                    </div>

                ) : (

                    <p>
                        No item information available.
                    </p>

                )}

            </div>

        </div>
    );
};

export default DeliveryOrderDetails;
