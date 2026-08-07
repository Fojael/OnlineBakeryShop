import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import { toast } from "react-toastify";

import {
    getOrders,
    cancelOrder,
} from "../../services/orderService";

const Orders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [cancellingId, setCancellingId] = useState(null);
    const [search, setSearch] = useState("");

    // =========================================================
    // Fetch Customer Orders
    // =========================================================

    const fetchOrders = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getOrders();

            setOrders(
                Array.isArray(response.data)
                    ? response.data
                    : []
            );
        } catch (error) {
            console.error(error);

            toast.error("Failed to load orders.");
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
            const orderNumber = `ORD${String(order.id).padStart(
                3,
                "0"
            )}`;

            const status = String(
                order.status || ""
            ).toLowerCase();

            const orderId = String(order.id);

            return (
                orderNumber
                    .toLowerCase()
                    .includes(keyword) ||
                orderId.includes(keyword) ||
                status.includes(keyword)
            );
        });
    }, [orders, search]);

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
    // Cancel Order
    // =========================================================

    const handleCancelOrder = async (id) => {
        const confirmCancel = window.confirm(
            "Are you sure you want to cancel this order?"
        );

        if (!confirmCancel) {
            return;
        }

        try {
            setCancellingId(id);

            // Backend changes:
            // Pending -> Cancelled
            //
            // The order remains in the database.
            await cancelOrder(id);

            toast.success(
                "Order cancelled successfully."
            );

            await fetchOrders();
        } catch (error) {
            console.error(error);

            const message =
                error?.response?.data?.detail ||
                "Failed to cancel order.";

            toast.error(message);
        } finally {
            setCancellingId(null);
        }
    };

    // =========================================================
    // Loading
    // =========================================================

    if (loading) {
        return (
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
        );
    }

    // =========================================================
    // Page
    // =========================================================

    return (
        <div className="container py-5">

            {/* Header */}

            <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">

                <div>
                    <h2 className="mb-1">
                        My Orders
                    </h2>

                    <p className="text-muted mb-0">
                        Total Orders:
                        <strong>
                            {" "}
                            {filteredOrders.length}
                        </strong>
                    </p>
                </div>

                {/* Search */}

                <div
                    className="w-100"
                    style={{ maxWidth: "300px" }}
                >
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search Order..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                    />
                </div>
            </div>

            {/* Orders Table */}

            <div className="card shadow">

                <div className="card-header bg-primary text-white">
                    <h5 className="mb-0">
                        Order History
                    </h5>
                </div>

                <div className="card-body">

                    <div className="table-responsive">

                        <table className="table table-bordered table-hover align-middle">

                            <thead className="table-dark">
                                <tr>
                                    <th>Order</th>
                                    <th>Date</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>

                            <tbody>

                                {filteredOrders.length > 0 ? (
                                    filteredOrders.map((order) => {
                                        const orderNumber =
                                            `ORD${String(
                                                order.id
                                            ).padStart(
                                                3,
                                                "0"
                                            )}`;

                                        return (
                                            <tr
                                                key={order.id}
                                            >

                                                {/* Order Number */}

                                                <td>
                                                    <strong>
                                                        {orderNumber}
                                                    </strong>
                                                </td>

                                                {/* Date */}

                                                <td>
                                                    {order.created_at
                                                        ? new Date(
                                                            order.created_at
                                                        ).toLocaleDateString(
                                                            "en-GB"
                                                        )
                                                        : "N/A"}
                                                </td>

                                                {/* Total */}

                                                <td>
                                                    ৳
                                                    {Number(
                                                        order.total_amount ||
                                                        0
                                                    ).toFixed(2)}
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
                                                    {order.status ===
                                                    "Pending" ? (
                                                        <button
                                                            type="button"
                                                            className="btn btn-danger btn-sm"
                                                            disabled={
                                                                cancellingId ===
                                                                order.id
                                                            }
                                                            onClick={() =>
                                                                handleCancelOrder(
                                                                    order.id
                                                                )
                                                            }
                                                        >
                                                            {cancellingId ===
                                                            order.id ? (
                                                                <>
                                                                    <span
                                                                        className="spinner-border spinner-border-sm me-1"
                                                                        role="status"
                                                                    />

                                                                    Cancelling...
                                                                </>
                                                            ) : (
                                                                "Cancel"
                                                            )}
                                                        </button>
                                                    ) : (
                                                        <span className="text-muted">
                                                            —
                                                        </span>
                                                    )}
                                                </td>

                                            </tr>
                                        );
                                    })
                                ) : (
                                    <tr>
                                        <td
                                            colSpan="5"
                                            className="text-center py-4"
                                        >
                                            {search
                                                ? "No orders match your search."
                                                : "No orders found."}
                                        </td>
                                    </tr>
                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Orders;