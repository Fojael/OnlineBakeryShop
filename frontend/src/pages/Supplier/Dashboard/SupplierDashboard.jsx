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
// SUPPLIER DASHBOARD
// ==========================================================

export default function SupplierDashboard() {

    const [
        dashboard,
        setDashboard,
    ] = useState(null);


    const [
        loading,
        setLoading,
    ] = useState(true);


    const [
        error,
        setError,
    ] = useState("");


    // ==========================================================
    // LOAD DASHBOARD
    // ==========================================================

    const loadDashboard =
        useCallback(
            async () => {

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

            },
            []
        );


    // ==========================================================
    // INITIAL LOAD
    // ==========================================================

    useEffect(() => {

        const timer =
            setTimeout(() => {

                loadDashboard();

            }, 0);


        return () => {

            clearTimeout(timer);

        };

    }, [loadDashboard]);


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
                    />

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

    const recentActivity =
        dashboard.recent_activity || [];

    const recentProducts =
        dashboard.recent_products || [];


    // ==========================================================
    // RENDER
    // ==========================================================

    return (

        <div className="container-fluid py-4">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="mb-4">

                <h2 className="fw-bold">
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
                PRODUCT STATISTICS
            ================================================== */}

            <h5 className="fw-bold mb-3">
                Product Overview
            </h5>


            <div className="row">

                <StatCard
                    title="Total Products"
                    value={
                        statistics.total_products ?? 0
                    }
                />


                <StatCard
                    title="Available Products"
                    value={
                        statistics.available_products ?? 0
                    }
                />


                <StatCard
                    title="Total Stock"
                    value={
                        statistics.total_stock ?? 0
                    }
                />


                <StatCard
                    title="Low Stock"
                    value={
                        statistics.low_stock ?? 0
                    }
                />


                <StatCard
                    title="Out of Stock"
                    value={
                        statistics.out_of_stock ?? 0
                    }
                />

            </div>


            {/* ==================================================
                ORDER STATISTICS
            ================================================== */}

            <h5 className="fw-bold mb-3 mt-3">
                Order Overview
            </h5>


            <div className="row">

                <StatCard
                    title="Pending Orders"
                    value={
                        statistics.pending_orders ?? 0
                    }
                />


                <StatCard
                    title="Completed Orders"
                    value={
                        statistics.completed_orders ?? 0
                    }
                />


                <StatCard
                    title="Cancelled Orders"
                    value={
                        statistics.cancelled_orders ?? 0
                    }
                />

            </div>


            {/* ==================================================
                PAYMENT STATISTICS
            ================================================== */}

            <h5 className="fw-bold mb-3 mt-3">
                Payment Overview
            </h5>


            <div className="row">

                <StatCard
                    title="Pending Payments"
                    value={
                        statistics.pending_payments ?? 0
                    }
                />


                <StatCard
                    title="Completed Payments"
                    value={
                        statistics.completed_payments ?? 0
                    }
                />


                <StatCard
                    title="Total Income"
                    value={
                        `৳${statistics.total_income ?? "0.00"}`
                    }
                />

            </div>


            {/* ==================================================
                RECENT CONTENT
            ================================================== */}

            <div className="row mt-3">


                {/* ==================================================
                    RECENT ACTIVITY
                ================================================== */}

                <div className="col-lg-6 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Recent Activity
                            </h5>

                        </div>


                        <div className="card-body">

                            {recentActivity.length === 0 ? (

                                <p className="text-muted mb-0">
                                    No recent activity.
                                </p>

                            ) : (

                                <div className="list-group list-group-flush">

                                    {recentActivity.map(
                                        (activity) => (

                                            <div
                                                key={
                                                    activity.id
                                                }
                                                className="list-group-item px-0"
                                            >

                                                <h6 className="mb-1">

                                                    {
                                                        activity.title
                                                    }

                                                </h6>


                                                <p className="mb-1 text-muted">

                                                    {
                                                        activity.description
                                                    }

                                                </p>


                                                <small className="text-muted">

                                                    {
                                                        activity.date
                                                            ? new Date(
                                                                activity.date
                                                            ).toLocaleString()
                                                            : "Unknown date"
                                                    }

                                                </small>

                                            </div>

                                        )
                                    )}

                                </div>

                            )}

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    RECENT PRODUCTS
                ================================================== */}

                <div className="col-lg-6 mb-4">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-header bg-white">

                            <h5 className="mb-0">
                                Recent Products
                            </h5>

                        </div>


                        <div className="card-body">

                            {recentProducts.length === 0 ? (

                                <p className="text-muted mb-0">
                                    No products available.
                                </p>

                            ) : (

                                <div className="table-responsive">

                                    <table className="table align-middle">

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
                                                            ৳
                                                            {
                                                                product.price
                                                            }
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
                                                                className={
                                                                    product.inventory_status ===
                                                                    "Out of Stock"

                                                                        ? "badge bg-danger"

                                                                        : product.inventory_status ===
                                                                          "Low Stock"

                                                                            ? "badge bg-warning text-dark"

                                                                            : "badge bg-success"
                                                                }
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

            </div>

        </div>

    );

}