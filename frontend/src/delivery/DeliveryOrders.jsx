import React, { useEffect, useState } from "react";

import { Link } from "react-router-dom";

import deliveryService from "../services/deliveryService";

import "./delivery.css";

// ==========================================================
// DELIVERY ORDERS
// ==========================================================

const DeliveryOrders = () => {

    const [orders, setOrders] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const [selectedStatus, setSelectedStatus] = useState("");

    // ======================================================
    // LOAD ORDERS
    // ======================================================

    const loadOrders = async () => {

        try {

            setLoading(true);
            setError("");

            const data = await deliveryService.getOrders(selectedStatus);

            if (Array.isArray(data)) {

                setOrders(data);

            } else {

                setOrders(
                    data.results || data.orders || data.deliveries || []
                );
            }

        } catch (err) {

            console.error("Orders error:", err);

            setError(
                err.response?.data?.detail || "Failed to load deliveries."
            );

        } finally {

            setLoading(false);
        }
    };

    useEffect(() => {

        loadOrders();

    }, [selectedStatus]);

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
                        MY DELIVERIES
                    </h1>

                    <p>
                        View and manage your assigned deliveries.
                    </p>

                </div>

                <Link
                    to="/delivery/dashboard"
                    className="delivery-header-btn"
                >
                    Dashboard
                </Link>

            </div>

            {/* ============================================ */}
            {/* FILTER */}
            {/* ============================================ */}

            <div className="delivery-filter">

                <label>
                    Filter by status
                </label>

                <select
                    value={selectedStatus}
                    onChange={(event) => setSelectedStatus(event.target.value)}
                >

                    <option value="">
                        All Deliveries
                    </option>

                    <option value="ASSIGNED">
                        Assigned
                    </option>

                    <option value="ACCEPTED">
                        Accepted
                    </option>

                    <option value="PICKED_UP">
                        Picked Up
                    </option>

                    <option value="OUT_FOR_DELIVERY">
                        Out for Delivery
                    </option>

                    <option value="DELIVERED">
                        Delivered
                    </option>

                </select>

            </div>

            {/* ============================================ */}
            {/* ERROR */}
            {/* ============================================ */}

            {error && (

                <div className="delivery-error">
                    {error}
                </div>

            )}

            {/* ============================================ */}
            {/* LOADING */}
            {/* ============================================ */}

            {loading ? (

                <div className="delivery-loading">
                    Loading deliveries...
                </div>

            ) : orders.length === 0 ? (

                <div className="empty-delivery">

                    <div className="empty-icon">
                        📦
                    </div>

                    <h3>
                        No deliveries found
                    </h3>

                    <p>
                        There are no deliveries matching your filter.
                    </p>

                </div>

            ) : (

                <div className="delivery-list">

                    {orders.map((order) => (

                        <div
                            className="delivery-card"
                            key={order.id}
                        >

                            <div className="delivery-card-top">

                                <div>

                                    <h3>
                                        Order #
                                        {order.order_id || order.id}
                                    </h3>

                                    <p>
                                        Customer: {order.customer_name || "N/A"}
                                    </p>

                                </div>

                                <span
                                    className={
                                        `status-badge status-${String(
                                            order.status || ""
                                        )
                                            .toLowerCase()
                                            .replaceAll("_", "-")}`
                                    }
                                >
                                    {formatStatus(order.status)}
                                </span>

                            </div>

                            <div className="delivery-info-row">

                                <div>

                                    <strong>
                                        Address
                                    </strong>

                                    <p>
                                        {order.shipping_address || order.address || "N/A"}
                                    </p>

                                </div>

                                <div>

                                    <strong>
                                        Amount
                                    </strong>

                                    <p>
                                        ৳{order.total_amount || "0.00"}
                                    </p>

                                </div>

                            </div>

                            <div className="delivery-card-bottom">

                                <small>
                                    {order.created_at
                                        ? new Date(order.created_at).toLocaleString()
                                        : ""}
                                </small>

                                <Link
                                    to={`/delivery/orders/${order.id}`}
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
    );
};

export default DeliveryOrders;
