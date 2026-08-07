import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import { getAdminOrders } from "../../../services/orderService";

const AdminOrders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    // =========================================================
    // Fetch All Orders
    // =========================================================

    const fetchOrders = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getAdminOrders();

            setOrders(
                Array.isArray(response.data)
                    ? response.data
                    : []
            );
        } catch (error) {
            console.error(error);

            toast.error(
                "Failed to load orders."
            );

            setOrders([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // =========================================================
    // Load Orders
    // =========================================================

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchOrders();
        }, 0);

        return () => {
            window.clearTimeout(timer);
        };
    }, [fetchOrders]);

    // =========================================================
    // Search Orders
    // =========================================================

    const filteredOrders = useMemo(() => {
        const keyword = search.trim().toLowerCase();

        if (!keyword) {
            return orders;
        }

        return orders.filter((order) => {
            const orderNumber =
                `ORD${String(order.id).padStart(
                    3,
                    "0"
                )}`;

            const customerName =
                getCustomerName(order).toLowerCase();

            const status = String(
                order.status || ""
            ).toLowerCase();

            const total = String(
                order.total_amount || ""
            );

            return (
                orderNumber
                    .toLowerCase()
                    .includes(keyword) ||
                customerName.includes(keyword) ||
                status.includes(keyword) ||
                total.includes(keyword)
            );
        });
    }, [orders, search]);

    // =========================================================
    // Customer Name
    // =========================================================

    function getCustomerName(order) {
        if (order.customer_name) {
            return order.customer_name;
        }

        if (order.customer?.username) {
            return order.customer.username;
        }

        if (order.customer?.name) {
            return order.customer.name;
        }

        if (order.customer?.email) {
            return order.customer.email;
        }

        if (typeof order.customer === "string") {
            return order.customer;
        }

        return "Unknown Customer";
    }

    // =========================================================
    // Status Badge
    // =========================================================

    const getStatusBadge = (status) => {
        switch (status) {
            case "Pending":
                return "badge bg-warning text-dark";

            case "Processing":
                return "badge bg-info";

            case "Delivered":
                return "badge bg-success";

            case "Cancelled":
                return "badge bg-danger";

            default:
                return "badge bg-secondary";
        }
    };

    // =========================================================
    // Format Date
    // =========================================================

    const formatDate = (date) => {
        if (!date) {
            return "N/A";
        }

        const parsedDate = new Date(date);

        if (Number.isNaN(parsedDate.getTime())) {
            return "N/A";
        }

        return parsedDate.toLocaleDateString(
            "en-GB"
        );
    };

    // =========================================================
    // Format Amount
    // =========================================================

    const formatAmount = (amount) => {
        const value = Number(amount);

        if (Number.isNaN(value)) {
            return "0.00";
        }

        return value.toFixed(2);
    };

    // =========================================================
    // Loading
    // =========================================================

    if (loading) {
        return (
            <DashboardLayout>

                <div className="container py-5 text-center">

                    <div
                        className="spinner-border text-primary"
                        role="status"
                    >
                        <span className="visually-hidden">
                            Loading...
                        </span>
                    </div>

                    <h4 className="mt-3">
                        Loading Orders...
                    </h4>

                </div>

            </DashboardLayout>
        );
    }

    // =========================================================
    // Page
    // =========================================================

    return (
        <DashboardLayout>

            <div className="container-fluid py-4">

                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">

                    <div>

                        <h2 className="mb-1">
                            Order Management
                        </h2>

                        <p className="text-muted mb-0">
                            Manage all customer orders.
                        </p>

                    </div>

                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={fetchOrders}
                    >
                        Refresh Orders
                    </button>

                </div>

                {/* =================================================
                    SEARCH
                ================================================= */}

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <div className="row align-items-end">

                            <div className="col-md-6">

                                <label
                                    htmlFor="orderSearch"
                                    className="form-label"
                                >
                                    Search Orders
                                </label>

                                <input
                                    id="orderSearch"
                                    type="text"
                                    className="form-control"
                                    placeholder="Search by order, customer, status..."
                                    value={search}
                                    onChange={(e) =>
                                        setSearch(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>

                            <div className="col-md-6 mt-3 mt-md-0">

                                <div className="text-md-end">

                                    <span className="text-muted">
                                        Total Orders:{" "}
                                    </span>

                                    <strong>
                                        {
                                            filteredOrders.length
                                        }
                                    </strong>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                {/* =================================================
                    ORDERS TABLE
                ================================================= */}

                <div className="card shadow">

                    <div className="card-header bg-primary text-white">

                        <h4 className="mb-0">
                            All Orders
                        </h4>

                    </div>

                    <div className="card-body p-0">

                        <div className="table-responsive">

                            <table className="table table-bordered table-hover align-middle mb-0">

                                <thead className="table-dark">

                                    <tr>

                                        <th>
                                            Order
                                        </th>

                                        <th>
                                            Customer
                                        </th>

                                        <th>
                                            Date
                                        </th>

                                        <th>
                                            Total
                                        </th>

                                        <th>
                                            Status
                                        </th>

                                        <th>
                                            Action
                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filteredOrders.length > 0 ? (

                                        filteredOrders.map(
                                            (order) => (
                                                <tr
                                                    key={
                                                        order.id
                                                    }
                                                >

                                                    {/* Order Number */}

                                                    <td>

                                                        <strong>
                                                            ORD
                                                            {String(
                                                                order.id
                                                            ).padStart(
                                                                3,
                                                                "0"
                                                            )}
                                                        </strong>

                                                    </td>

                                                    {/* Customer */}

                                                    <td>
                                                        {
                                                            getCustomerName(
                                                                order
                                                            )
                                                        }
                                                    </td>

                                                    {/* Date */}

                                                    <td>
                                                        {formatDate(
                                                            order.created_at
                                                        )}
                                                    </td>

                                                    {/* Total */}

                                                    <td>

                                                        <strong>
                                                            ৳
                                                            {formatAmount(
                                                                order.total_amount
                                                            )}
                                                        </strong>

                                                    </td>

                                                    {/* Status */}

                                                    <td>

                                                        <span
                                                            className={getStatusBadge(
                                                                order.status
                                                            )}
                                                        >
                                                            {
                                                                order.status
                                                            }
                                                        </span>

                                                    </td>

                                                    {/* Action */}

                                                    <td>

                                                        <Link
                                                            to={`/admin/orders/update/${order.id}`}
                                                            className="btn btn-warning btn-sm"
                                                        >
                                                            Update
                                                        </Link>

                                                    </td>

                                                </tr>
                                            )
                                        )

                                    ) : (

                                        <tr>

                                            <td
                                                colSpan="6"
                                                className="text-center py-5"
                                            >

                                                <h5>
                                                    No Orders Found
                                                </h5>

                                                <p className="text-muted mb-0">

                                                    {search
                                                        ? "No orders match your search."
                                                        : "There are no orders yet."}

                                                </p>

                                            </td>

                                        </tr>

                                    )}

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
};

export default AdminOrders;