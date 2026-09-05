import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const INITIAL_STATS = {
    customers: 0,
    suppliers: 0,
    delivery_riders: 0,
    products: 0,
    orders: 0,
    sales: "0.00",
    pending_orders: 0,
    processing_orders: 0,
    delivered_orders: 0,
    low_stock_products: 0,
};

const Dashboard = () => {
    const [stats, setStats] = useState(INITIAL_STATS);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let ignore = false;

        const loadDashboard = async () => {
            try {
                const response = await api.get(
                    "auth/admin-dashboard/"
                );

                if (ignore) {
                    return;
                }

                const dashboardStats = response.data?.stats;

                setStats((previousStats) => ({
                    ...previousStats,
                    ...(dashboardStats || {}),
                }));
            } catch (err) {
                console.error(
                    "Admin dashboard error:",
                    err
                );

                if (!ignore) {
                    setError(
                        err.response?.data?.detail ||
                        err.response?.data?.message ||
                        "Failed to load dashboard data."
                    );
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadDashboard();

        return () => {
            ignore = true;
        };
    }, []);

    const cards = [
        {
            label: "Customers",
            value: stats.customers,
        },
        {
            label: "Suppliers",
            value: stats.suppliers,
        },
        {
            label: "Delivery Men",
            value: stats.delivery_riders,
        },
        {
            label: "Products",
            value: stats.products,
        },
        {
            label: "Orders",
            value: stats.orders,
        },
        {
            label: "Sales",
            value: `৳${stats.sales}`,
        },
    ];

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">

                <h2>Admin Dashboard</h2>

                <hr />

                {error && (
                    <div className="alert alert-danger">
                        {error}
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-5">

                        <div
                            className="spinner-border text-primary"
                            role="status"
                        >
                            <span className="visually-hidden">
                                Loading...
                            </span>
                        </div>

                        <p className="mt-3 text-muted">
                            Loading dashboard...
                        </p>

                    </div>
                ) : (
                    <>
                        {/* ==================================================
                            MAIN STATISTICS
                        ================================================== */}

                        <div className="row g-3 mb-4">

                            {cards.map((card) => (
                                <div
                                    className="col-md-4 col-lg-2"
                                    key={card.label}
                                >
                                    <div className="card h-100 shadow-sm border-0">

                                        <div className="card-body">

                                            <div className="text-muted small">
                                                {card.label}
                                            </div>

                                            <h4 className="mt-2 mb-0">
                                                {card.value}
                                            </h4>

                                        </div>

                                    </div>
                                </div>
                            ))}

                        </div>


                        {/* ==================================================
                            ORDER / INVENTORY STATISTICS
                        ================================================== */}

                        <div className="row g-3">

                            {/* Pending */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Pending Orders
                                        </div>

                                        <h4>
                                            {stats.pending_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Processing */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Processing Orders
                                        </div>

                                        <h4>
                                            {stats.processing_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Delivered */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Delivered Orders
                                        </div>

                                        <h4>
                                            {stats.delivered_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Low Stock */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Low Stock Products
                                        </div>

                                        <h4>
                                            {stats.low_stock_products}
                                        </h4>

                                    </div>

                                </div>

                            </div>

                        </div>
                    </>
                )}

            </div>
        </DashboardLayout>
    );
};

export default Dashboard;