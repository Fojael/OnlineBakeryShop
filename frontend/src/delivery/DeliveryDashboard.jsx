import { useEffect, useState } from "react";

import { Link } from "react-router-dom";

import deliveryService from "../services/deliveryService";

import "./delivery.css";

// ==========================================================
// DELIVERY DASHBOARD
// ==========================================================

const DeliveryDashboard = () => {

    const [dashboard, setDashboard] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    // ======================================================
    // LOAD DASHBOARD
    // ======================================================

    const loadDashboard = async () => {

        try {

            setLoading(true);
            setError("");

            const data = await deliveryService.getDashboard();

            setDashboard(data);

        } catch (err) {

            console.error("Dashboard error:", err);

            setError(
                err.response?.data?.detail ||
                "Failed to load delivery dashboard."
            );

        } finally {

            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void loadDashboard();
        }, 0);
        return () => window.clearTimeout(timer);
    }, []);

    // ======================================================
    // LOADING
    // ======================================================

    if (loading) {

        return (
            <div className="delivery-page">

                <div className="delivery-loading">
                    Loading dashboard...
                </div>

            </div>
        );
    }

    // ======================================================
    // ERROR
    // ======================================================

    if (error) {

        return (
            <div className="delivery-page">

                <div className="delivery-error">
                    {error}
                </div>

                <button
                    className="delivery-btn"
                    onClick={loadDashboard}
                >
                    Try Again
                </button>

            </div>
        );
    }

    // ======================================================
    // DEFAULT VALUES
    // ======================================================

    const stats = dashboard?.stats || {};

    const deliveries = dashboard?.deliveries || dashboard?.orders || [];
    const refundPickups = dashboard?.refundPickups || [];

    const handleRefundAction = async (refund, action) => {
        try {
            setError("");
            if (action === "accept") {
                await deliveryService.acceptRefundPickup(refund.id);
            } else if (action === "request") {
                await deliveryService.requestRefundPickupOtp(refund.id);
            } else {
                const otp = window.prompt("Enter the 6-digit customer OTP:");
                if (!otp) return;
                await deliveryService.verifyRefundPickupOtp(refund.id, otp);
            }
            await loadDashboard();
        } catch (err) {
            setError(err.response?.data?.detail || "Refund pickup action failed.");
        }
    };

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
                        DELIVERY DASHBOARD
                    </h1>

                    <p>
                        Manage your assigned customer deliveries.
                    </p>

                </div>

                <Link
                    to="/delivery/orders"
                    className="delivery-header-btn "
                >
                    View All Deliveries
                </Link>

                <Link
                    to="/notifications"
                    className="delivery-header-btn"
                >
                    Notifications
                </Link>

            </div>

            {/* ============================================ */}
            {/* STATISTICS */}
            {/* ============================================ */}

            <div className="delivery-stats-grid">

                <div className="delivery-stat-card">

                    <div className="stat-icon">
                        📦
                    </div>

                    <div>
                        <h3>
                            Assigned
                        </h3>

                        <strong>
                            {stats.assigned || 0}
                        </strong>
                    </div>

                </div>

                <div className="delivery-stat-card">

                    <div className="stat-icon">
                        ✓
                    </div>

                    <div>
                        <h3>
                            Accepted
                        </h3>

                        <strong>
                            {stats.accepted || 0}
                        </strong>
                    </div>

                </div>

                <div className="delivery-stat-card">

                    <div className="stat-icon">
                        📦
                    </div>

                    <div>
                        <h3>
                            Picked Up
                        </h3>

                        <strong>
                            {stats.picked_up || 0}
                        </strong>
                    </div>

                </div>

                <div className="delivery-stat-card">

                    <div className="stat-icon">
                        🚚
                    </div>

                    <div>
                        <h3 class>
                            Out for Delivery
                        </h3>

                        <strong>
                            {stats.out_for_delivery || 0}
                        </strong>
                    </div>

                </div>

                <div className="delivery-stat-card">

                    <div className="stat-icon">
                        🏠
                    </div>

                    <div>
                        <h3>
                            Delivered
                        </h3>

                        <strong>
                            {stats.delivered || 0}
                        </strong>
                    </div>

                </div>

            </div>

            {/* ============================================ */}
            {/* MY DELIVERIES */}
            {/* ============================================ */}

            <div className="delivery-section">

                <div className="section-header">

                    <h2 className="text-primary">
                        MY DELIVERIES
                    </h2>

                    <Link
                        to="/delivery/orders"
                        className="text-success"
                    >
                        View All
                    </Link>

                </div>

                {deliveries.length === 0 ? (

                    <div className="empty-delivery">

                        <div className="empty-icon">
                            📦
                        </div>

                        <h3>
                            No deliveries
                        </h3>

                        <p>
                            You currently have no assigned deliveries.
                        </p>

                    </div>

                ) : (

                    <div className="delivery-list">

                        {deliveries.slice(0, 5).map((delivery) => (

                            <div
                                className="delivery-card"
                                key={delivery.id}
                            >

                                <div className="delivery-card-top">

                                    <div>

                                        <h3>
                                            Order #
                                            {delivery.order_id || delivery.id}
                                        </h3>

                                        <p>
                                            Customer: {delivery.customer_name || "N/A"}
                                        </p>

                                    </div>

                                    <span
                                        className={
                                            `status-badge status-${String(
                                                delivery.status || ""
                                            )
                                                .toLowerCase()
                                                .replaceAll("_", "-")}`
                                        }
                                    >
                                        {delivery.status || "Assigned"}
                                    </span>

                                </div>

                                <div className="delivery-address">

                                    📍 {delivery.shipping_address || delivery.address || "Address not available"}

                                </div>

                                <div className="delivery-card-bottom">

                                    <span>
                                        Total: ৳{delivery.total_amount || "0.00"}
                                    </span>

                                    <Link
                                        to={`/delivery/orders/${delivery.id}`}
                                        className="view-details-btn"
                                    >
                                        View Details
                                    </Link>

                                </div>

                            </div>

                        ))}

                    </div>

                )}

            </div>

            <div className="delivery-section">
                <div className="section-header"><h2>REFUND PICKUPS</h2></div>
                {refundPickups.length === 0 ? (
                    <div className="empty-delivery"><p>No refund pickups assigned.</p></div>
                ) : (
                    <div className="delivery-list">
                        {refundPickups.map((refund) => (
                            <div className="delivery-card" key={`refund-${refund.id}`}>
                                <div className="delivery-card-top">
                                    <div><h3>Refund #{refund.id} / Order #{refund.order}</h3><p>Customer: {refund.customer_name || "N/A"}</p></div>
                                    <span className="status-badge">{refund.status}</span>
                                </div>
                                <p>Pickup deadline: {refund.pickup_deadline ? new Date(refund.pickup_deadline).toLocaleString() : "-"}</p>
                                <p>Refund amount: ৳{Number(refund.approved_amount || 0).toFixed(2)}</p>
                                {refund.status === "Rider Assigned" && <button className="delivery-status-btn" onClick={() => handleRefundAction(refund, "accept")}>Accept Pickup</button>}
                                {refund.status === "Rider Accepted" && <div className="d-flex gap-2"><button className="delivery-status-btn" onClick={() => handleRefundAction(refund, "request")}>Request OTP</button><button className="delivery-status-btn" onClick={() => handleRefundAction(refund, "verify")}>Complete Pickup</button></div>}
                            </div>
                        ))}
                    </div>
                )}
            </div>

        </div>
    );
};

export default DeliveryDashboard;
