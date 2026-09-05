import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    getSupplierDashboard,
} from "../../../services/supplierService";


// ==========================================================
// STAT CARD
// ==========================================================

function StatCard({
    title,
    value,
}) {
    return (
        <div className="col-md-6 col-xl-3 mb-4">

            <div className="card h-100 shadow-sm border-0">

                <div className="card-body">

                    <h6 className="text-muted mb-2">
                        {title}
                    </h6>

                    <h3 className="fw-bold mb-0">
                        {value}
                    </h3>

                </div>

            </div>

        </div>
    );
}


// ==========================================================
// SUPPLIER ORDER WORKFLOW
// ==========================================================

function SupplierOrderWorkflow() {
    return (
        <div className="card border-0 shadow-sm mb-4">

            <div className="card-header bg-white py-3">

                <h5 className="mb-1 fw-bold">
                    Supplier Order Workflow
                </h5>

                <p className="text-muted small mb-0">
                    Follow the item-level workflow below.
                    The parent order status is controlled automatically.
                </p>

            </div>


            <div className="card-body">

                {/* ==================================================
                    PROCESSING
                ================================================== */}

                <div className="border rounded p-3 mb-3">

                    <div className="d-flex align-items-start gap-3">

                        <span className="badge bg-info text-dark mt-1">
                            Processing
                        </span>

                        <div className="flex-grow-1">

                            <h6 className="fw-bold mb-1">
                                Processing
                            </h6>

                            <p className="mb-1">
                                No direct parent-order status change.
                            </p>

                            <small className="text-muted">
                                Update your own order items from{" "}
                                <strong>
                                    Pending → Processing
                                </strong>{" "}
                                and then{" "}
                                <strong>
                                    Processing → Ready
                                </strong>.
                            </small>

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    READY - NOT ALL ITEMS READY
                ================================================== */}

                <div className="border rounded p-3 mb-3">

                    <div className="d-flex align-items-start gap-3">

                        <span className="badge bg-warning text-dark mt-1">
                            Wait
                        </span>

                        <div className="flex-grow-1">

                            <h6 className="fw-bold mb-1">
                                Ready + items not all Ready
                            </h6>

                            <p className="mb-1">
                                Wait until all supplier items are Ready.
                            </p>

                            <small className="text-muted">
                                If some items are still Pending or Processing,
                                the order is not ready for rider assignment.
                            </small>

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    READY - ALL ITEMS READY
                ================================================== */}

                <div className="border rounded p-3">

                    <div className="d-flex align-items-start gap-3">

                        <span className="badge bg-success mt-1">
                            Ready
                        </span>

                        <div className="flex-grow-1">

                            <h6 className="fw-bold mb-1">
                                Ready + all items Ready
                            </h6>

                            <p className="mb-1">
                                No further supplier action is required.
                            </p>

                            <small className="text-muted">
                                Once all supplier items are Ready, the
                                parent order becomes Ready automatically.
                                The Admin can then select a specific rider
                                and assign the delivery.
                            </small>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}


// ==========================================================
// SUPPLIER DASHBOARD
// ==========================================================

export default function SupplierDashboard() {

    const [dashboard, setDashboard] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    // ==========================================================
    // LOAD DASHBOARD
    // ==========================================================

    const loadDashboard = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const response =
                await getSupplierDashboard();

            if (
                response?.success &&
                response?.dashboard
            ) {

                setDashboard(
                    response.dashboard
                );

            } else {

                setError(
                    "Invalid dashboard response."
                );
            }

        } catch (error) {

            console.error(
                "Supplier dashboard error:",
                error
            );

            if (
                error.response?.status === 401
            ) {

                setError(
                    "Your session has expired. Please login again."
                );

            } else if (
                error.response?.status === 403
            ) {

                setError(
                    "Your supplier account is not approved or active."
                );

            } else if (
                error.response?.status === 404
            ) {

                setError(
                    "Supplier profile does not exist."
                );

            } else {

                setError(
                    "Failed to load supplier dashboard."
                );
            }

        } finally {

            setLoading(false);
        }

    }, []);


    // ==========================================================
    // INITIAL LOAD
    // ==========================================================

    useEffect(() => {

        const timer =
            setTimeout(() => {
                void loadDashboard();
            }, 0);

        return () => {
            clearTimeout(timer);
        };

    }, [
        loadDashboard,
    ]);


    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {

        return (
            <div className="container-fluid py-4">

                <div className="text-center py-5">

                    <div
                        className="spinner-border"
                        role="status"
                    >
                        <span className="visually-hidden">
                            Loading...
                        </span>
                    </div>

                    <p className="mt-3">
                        Loading supplier dashboard...
                    </p>

                </div>

            </div>
        );
    }


    // ==========================================================
    // ERROR
    // ==========================================================

    if (error) {

        return (
            <div className="container-fluid py-4">

                <div
                    className="alert alert-danger"
                    role="alert"
                >

                    {error}

                    <div className="mt-3">

                        <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={loadDashboard}
                        >
                            Try Again
                        </button>

                    </div>

                </div>

            </div>
        );
    }


    if (!dashboard) {
        return null;
    }


    // ==========================================================
    // DASHBOARD DATA
    // ==========================================================

    const supplier =
        dashboard.supplier || {};

    const statistics =
        dashboard.statistics || {};

    const notifications =
        Array.isArray(
            dashboard.notifications
        )
            ? dashboard.notifications
            : [];

    const recentOrders =
        Array.isArray(
            dashboard.recent_orders
        )
            ? dashboard.recent_orders
            : [];

    const lowStockAlerts =
        Array.isArray(
            dashboard.low_stock_alerts
        )
            ? dashboard.low_stock_alerts
            : [];

    const inventorySummary =
        dashboard.inventory_summary || {};

    const recentProducts =
        Array.isArray(
            dashboard.recent_products
        )
            ? dashboard.recent_products
            : [];

    const salesOverview =
        Array.isArray(
            dashboard.sales_overview
        )
            ? dashboard.sales_overview
            : [];


    // ==========================================================
    // HELPERS
    // ==========================================================

    const formatCurrency = (value) => {

        const numericValue =
            Number(value ?? 0);

        if (
            !Number.isFinite(
                numericValue
            )
        ) {
            return "৳0.00";
        }

        return `৳${numericValue.toLocaleString(
            "en-BD",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        )}`;
    };


    const formatDate = (value) => {

        if (!value) {
            return "Unknown date";
        }

        const date =
            new Date(value);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return "Unknown date";
        }

        return date.toLocaleString(
            "en-BD",
            {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            }
        );
    };


    const statusBadgeClass = (
        status = ""
    ) => {

        if (
            status === "Out of Stock"
        ) {
            return "badge bg-danger";
        }

        if (
            status === "Low Stock"
        ) {
            return "badge bg-warning text-dark";
        }

        if (
            status === "Pending"
        ) {
            return "badge bg-warning text-dark";
        }

        if (
            status === "Processing"
        ) {
            return "badge bg-info text-dark";
        }

        if (
            status === "Ready"
        ) {
            return "badge bg-success";
        }

        if (
            status === "Assigned"
        ) {
            return "badge bg-secondary";
        }

        if (
            status === "Out for Delivery"
        ) {
            return "badge bg-dark";
        }

        if (
            status === "Delivered"
        ) {
            return "badge bg-success";
        }

        if (
            status === "Cancelled"
        ) {
            return "badge bg-secondary";
        }

        return "badge bg-info text-dark";
    };


    // ==========================================================
    // RENDER
    // ==========================================================

    return (
        <div className="container-fluid py-4">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="mb-4">

                <h2 className="fw-bold mb-1">
                    Supplier Dashboard
                </h2>

                <p className="text-muted mb-0">
                    Welcome back,{" "}
                    {supplier.name || "Supplier"}
                </p>

                {supplier.company && (
                    <small className="text-muted">
                        {supplier.company}
                    </small>
                )}

            </div>


            {/* ==================================================
                STATISTICS
            ================================================== */}

            <div className="row">

                <StatCard
                    title="Total Products"
                    value={
                        statistics.total_products ??
                        0
                    }
                />

                <StatCard
                    title="Available Products"
                    value={
                        statistics.available_products ??
                        0
                    }
                />

                <StatCard
                    title="Low Stock"
                    value={
                        statistics.low_stock ??
                        0
                    }
                />

                <StatCard
                    title="Out of Stock"
                    value={
                        statistics.out_of_stock ??
                        0
                    }
                />

                <StatCard
                    title="Pending Orders"
                    value={
                        statistics.pending_orders ??
                        0
                    }
                />

                <StatCard
                    title="Completed Orders"
                    value={
                        statistics.completed_orders ??
                        0
                    }
                />

                <StatCard
                    title="Total Revenue"
                    value={formatCurrency(
                        statistics.total_income ??
                        0
                    )}
                />

                <StatCard
                    title="Notifications"
                    value={
                        notifications.length
                    }
                />

            </div>


            {/* ==================================================
                SUPPLIER ORDER WORKFLOW
            ================================================== */}

            <SupplierOrderWorkflow />


            {/* ==================================================
                RECENT ORDERS + NOTIFICATIONS
            ================================================== */}

            <div className="row mt-3">

                {/* ==================================================
                    RECENT ORDERS
                ================================================== */}

                <div className="col-lg-7 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Recent Orders
                            </h5>

                        </div>


                        <div className="card-body p-0">

                            {recentOrders.length === 0 ? (

                                <div className="p-3 text-muted">
                                    No recent orders.
                                </div>

                            ) : (

                                <div className="table-responsive">

                                    <table className="table align-middle mb-0">

                                        <thead>

                                            <tr>

                                                <th>
                                                    Order
                                                </th>

                                                <th>
                                                    Customer
                                                </th>

                                                <th>
                                                    Status
                                                </th>

                                                <th>
                                                    Total
                                                </th>

                                                <th>
                                                    Date
                                                </th>

                                            </tr>

                                        </thead>


                                        <tbody>

                                            {recentOrders.map(
                                                (order) => (

                                                    <tr
                                                        key={
                                                            order.id
                                                        }
                                                    >

                                                        <td>
                                                            {
                                                                order.order_number ||
                                                                `#${order.id}`
                                                            }
                                                        </td>


                                                        <td>
                                                            {
                                                                order.customer ||
                                                                "Customer"
                                                            }
                                                        </td>


                                                        <td>

                                                            <span
                                                                className={statusBadgeClass(
                                                                    order.status
                                                                )}
                                                            >
                                                                {
                                                                    order.status ||
                                                                    "Unknown"
                                                                }
                                                            </span>

                                                        </td>


                                                        <td>
                                                            {formatCurrency(
                                                                order.total_amount ??
                                                                0
                                                            )}
                                                        </td>


                                                        <td>
                                                            {formatDate(
                                                                order.date
                                                            )}
                                                        </td>

                                                    </tr>

                                                )
                                            )}

                                        </tbody>

                                    </table>

                                </div>

                            )}

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    NOTIFICATIONS
                ================================================== */}

                <div className="col-lg-5 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Notifications
                            </h5>

                        </div>


                        <div className="card-body">

                            {notifications.length === 0 ? (

                                <p className="text-muted mb-0">
                                    No notifications.
                                </p>

                            ) : (

                                <div className="list-group list-group-flush">

                                    {notifications.map(
                                        (notification) => (

                                            <div
                                                key={
                                                    notification.id ||
                                                    notification.title
                                                }
                                                className="list-group-item px-0"
                                            >

                                                <div className="d-flex justify-content-between align-items-start gap-3">

                                                    <div>

                                                        <h6 className="mb-1">
                                                            {
                                                                notification.title ||
                                                                "Update"
                                                            }
                                                        </h6>

                                                        <p className="mb-1 text-muted">
                                                            {
                                                                notification.message ||
                                                                notification.description ||
                                                                "No details available."
                                                            }
                                                        </p>

                                                        <small className="text-muted">
                                                            {
                                                                notification.type ||
                                                                "Info"
                                                            }
                                                        </small>

                                                    </div>


                                                    <small className="text-muted text-nowrap">

                                                        {formatDate(
                                                            notification.date
                                                        )}

                                                    </small>

                                                </div>

                                            </div>

                                        )
                                    )}

                                </div>

                            )}

                        </div>

                    </div>

                </div>

            </div>


            {/* ==================================================
                LOW STOCK + INVENTORY
            ================================================== */}

            <div className="row mt-1">

                {/* ==================================================
                    LOW STOCK
                ================================================== */}

                <div className="col-lg-5 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Low Stock Alerts
                            </h5>

                        </div>


                        <div className="card-body">

                            {lowStockAlerts.length === 0 ? (

                                <p className="text-muted mb-0">
                                    All products are well stocked.
                                </p>

                            ) : (

                                <div className="list-group list-group-flush">

                                    {lowStockAlerts.map(
                                        (alert) => (

                                            <div
                                                key={
                                                    alert.id
                                                }
                                                className="list-group-item px-0"
                                            >

                                                <div className="d-flex justify-content-between align-items-center gap-3">

                                                    <div>

                                                        <h6 className="mb-1">
                                                            {
                                                                alert.product_name ||
                                                                "Product"
                                                            }
                                                        </h6>

                                                        <small className="text-muted">

                                                            {
                                                                alert.stock_quantity ??
                                                                0
                                                            }{" "}
                                                            in stock · minimum{" "}
                                                            {
                                                                alert.minimum_stock ??
                                                                0
                                                            }

                                                        </small>

                                                    </div>


                                                    <span
                                                        className={statusBadgeClass(
                                                            alert.status
                                                        )}
                                                    >
                                                        {
                                                            alert.status ||
                                                            "Low Stock"
                                                        }
                                                    </span>

                                                </div>

                                            </div>

                                        )
                                    )}

                                </div>

                            )}

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    INVENTORY SUMMARY
                ================================================== */}

                <div className="col-lg-7 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Inventory Summary
                            </h5>

                        </div>


                        <div className="card-body">

                            <div className="row g-3">

                                <div className="col-md-6">

                                    <div className="border rounded p-3 h-100">

                                        <small className="text-muted">
                                            In Stock
                                        </small>

                                        <h4 className="mb-0 mt-1">
                                            {
                                                inventorySummary.in_stock_items ??
                                                0
                                            }
                                        </h4>

                                    </div>

                                </div>


                                <div className="col-md-6">

                                    <div className="border rounded p-3 h-100">

                                        <small className="text-muted">
                                            Low Stock
                                        </small>

                                        <h4 className="mb-0 mt-1">
                                            {
                                                inventorySummary.low_stock_items ??
                                                0
                                            }
                                        </h4>

                                    </div>

                                </div>


                                <div className="col-md-6">

                                    <div className="border rounded p-3 h-100">

                                        <small className="text-muted">
                                            Out of Stock
                                        </small>

                                        <h4 className="mb-0 mt-1">
                                            {
                                                inventorySummary.out_of_stock_items ??
                                                0
                                            }
                                        </h4>

                                    </div>

                                </div>


                                <div className="col-md-6">

                                    <div className="border rounded p-3 h-100">

                                        <small className="text-muted">
                                            Total Stock
                                        </small>

                                        <h4 className="mb-0 mt-1">
                                            {
                                                inventorySummary.total_stock ??
                                                0
                                            }
                                        </h4>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>


            {/* ==================================================
                PRODUCTS + SALES
            ================================================== */}

            <div className="row mt-1">

                {/* ==================================================
                    RECENT PRODUCTS
                ================================================== */}

                <div className="col-lg-7 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Recent Products
                            </h5>

                        </div>


                        <div className="card-body p-0">

                            {recentProducts.length === 0 ? (

                                <div className="p-3 text-muted">
                                    No products available.
                                </div>

                            ) : (

                                <div className="table-responsive">

                                    <table className="table align-middle mb-0">

                                        <thead>

                                            <tr>

                                                <th>
                                                    Product
                                                </th>

                                                <th>
                                                    Price
                                                </th>

                                                <th>
                                                    Stock
                                                </th>

                                                <th>
                                                    Status
                                                </th>

                                            </tr>

                                        </thead>


                                        <tbody>

                                            {recentProducts.map(
                                                (product) => (

                                                    <tr
                                                        key={
                                                            product.id
                                                        }
                                                    >

                                                        <td>
                                                            {
                                                                product.name
                                                            }
                                                        </td>

                                                        <td>
                                                            {formatCurrency(
                                                                product.price ??
                                                                0
                                                            )}
                                                        </td>

                                                        <td>
                                                            {
                                                                product.current_stock ??
                                                                product.stock_quantity ??
                                                                0
                                                            }
                                                        </td>

                                                        <td>

                                                            <span
                                                                className={statusBadgeClass(
                                                                    product.inventory_status
                                                                )}
                                                            >
                                                                {
                                                                    product.inventory_status ||
                                                                    "Unknown"
                                                                }
                                                            </span>

                                                        </td>

                                                    </tr>

                                                )
                                            )}

                                        </tbody>

                                    </table>

                                </div>

                            )}

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    SALES OVERVIEW
                ================================================== */}

                <div className="col-lg-5 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Sales Overview
                            </h5>

                        </div>


                        <div className="card-body">

                            {salesOverview.length === 0 ? (

                                <p className="text-muted mb-0">
                                    No sales data yet.
                                </p>

                            ) : (

                                <div>

                                    {salesOverview.map(
                                        (entry, index) => {

                                            const maxAmount =
                                                salesOverview.reduce(
                                                    (
                                                        max,
                                                        item
                                                    ) =>
                                                        Math.max(
                                                            max,
                                                            Number(
                                                                item.amount ??
                                                                0
                                                            )
                                                        ),
                                                    0
                                                ) || 1;

                                            const width =
                                                (
                                                    Number(
                                                        entry.amount ??
                                                        0
                                                    ) /
                                                    maxAmount
                                                ) *
                                                100;

                                            return (

                                                <div
                                                    className="mb-3"
                                                    key={`${entry.label}-${index}`}
                                                >

                                                    <div className="d-flex justify-content-between align-items-center mb-1">

                                                        <small className="text-muted">
                                                            {
                                                                entry.label
                                                            }
                                                        </small>

                                                        <strong>
                                                            {formatCurrency(
                                                                entry.amount ??
                                                                0
                                                            )}
                                                        </strong>

                                                    </div>


                                                    <div
                                                        className="progress"
                                                        style={{
                                                            height: "8px",
                                                        }}
                                                    >

                                                        <div
                                                            className="progress-bar bg-success"
                                                            role="progressbar"
                                                            style={{
                                                                width: `${width}%`,
                                                            }}
                                                        />

                                                    </div>

                                                </div>

                                            );
                                        }
                                    )}

                                </div>

                            )}

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}