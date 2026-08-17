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
    // =========================================================
    // STATE
    // =========================================================

    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [cancellingId, setCancellingId] =
        useState(null);

    const [expandedOrder, setExpandedOrder] =
        useState(null);

    const [search, setSearch] = useState("");

    // =========================================================
    // FETCH ORDERS
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

            if (
                error?.response?.status === 401
            ) {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                toast.info(
                    "Please login again."
                );

                window.location.href = "/login";
                return;
            }

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to load orders."
            );
        } finally {
            setLoading(false);
        }
    }, []);

    // =========================================================
    // LOAD ORDERS
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
    // SEARCH
    // =========================================================

    const filteredOrders = useMemo(() => {
        const keyword = search
            .trim()
            .toLowerCase();

        if (!keyword) {
            return orders;
        }

        return orders.filter((order) => {
            const orderNumber = `ORD${String(
                order.id
            ).padStart(3, "0")}`;

            return (
                orderNumber
                    .toLowerCase()
                    .includes(keyword) ||
                String(order.id).includes(
                    keyword
                ) ||
                String(
                    order.status || ""
                )
                    .toLowerCase()
                    .includes(keyword) ||
                String(
                    order.payment_method || ""
                )
                    .toLowerCase()
                    .includes(keyword)
            );
        });
    }, [orders, search]);

    // =========================================================
    // STATUS BADGE
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
    // CANCEL ORDER
    // =========================================================

    const handleCancelOrder = async (
        orderId
    ) => {
        const confirmed =
            window.confirm(
                "Are you sure you want to cancel this order?"
            );

        if (!confirmed) {
            return;
        }

        try {
            setCancellingId(orderId);

            await cancelOrder(orderId);

            toast.success(
                "Order cancelled successfully."
            );

            await fetchOrders();
        } catch (error) {
            console.error(error);

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to cancel order."
            );
        } finally {
            setCancellingId(null);
        }
    };

    // =========================================================
    // LOADING
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

    return (
        <div className="container py-5">

            {/* ================================================
                HEADER
            ================================================ */}

            <div className="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-4">

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

                <div
                    style={{
                        maxWidth: "320px",
                        width: "100%",
                    }}
                >
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search order..."
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                    />
                </div>
            </div>

            <div className="card shadow">

                <div className="card-header bg-primary text-white">
                    <h5 className="mb-0">
                        Order History
                    </h5>
                </div>

                <div className="card-body">
                                        {filteredOrders.length === 0 ? (

                        <div className="text-center py-5">
                            <h5>No orders found.</h5>

                            <p className="text-muted mb-0">
                                {search
                                    ? "No orders match your search."
                                    : "You haven't placed any orders yet."}
                            </p>
                        </div>

                    ) : (

                        filteredOrders.map((order) => {

                            const orderNumber =
                                `ORD${String(order.id).padStart(3, "0")}`;

                            const isExpanded =
                                expandedOrder === order.id;

                            return (
                                <div
                                    key={order.id}
                                    className="card mb-4 border"
                                >

                                    {/* =====================================
                                        ORDER HEADER
                                    ====================================== */}

                                    <div className="card-header bg-light">

                                        <div className="row align-items-center">

                                            <div className="col-lg-3">
                                                <strong>
                                                    {orderNumber}
                                                </strong>

                                                <div className="small text-muted">
                                                    {order.created_at
                                                        ? new Date(
                                                              order.created_at
                                                          ).toLocaleString(
                                                              "en-GB"
                                                          )
                                                        : "N/A"}
                                                </div>
                                            </div>

                                            <div className="col-lg-2 mt-2 mt-lg-0">
                                                <span
                                                    className={getStatusBadge(
                                                        order.status
                                                    )}
                                                >
                                                    {order.status}
                                                </span>
                                            </div>

                                            <div className="col-lg-2 mt-2 mt-lg-0">
                                                <strong>
                                                    {order.item_count}
                                                </strong>
                                                <div className="small text-muted">
                                                    Items
                                                </div>
                                            </div>

                                            <div className="col-lg-2 mt-2 mt-lg-0">
                                                <strong>
                                                    ৳
                                                    {Number(
                                                        order.total_amount || 0
                                                    ).toFixed(2)}
                                                </strong>
                                                <div className="small text-muted">
                                                    Total
                                                </div>
                                            </div>

                                            <div className="col-lg-3 text-lg-end mt-3 mt-lg-0">

                                                <button
                                                    type="button"
                                                    className="btn btn-outline-primary btn-sm me-2"
                                                    onClick={() =>
                                                        setExpandedOrder(
                                                            isExpanded
                                                                ? null
                                                                : order.id
                                                        )
                                                    }
                                                >
                                                    {isExpanded
                                                        ? "Hide Details"
                                                        : "View Details"}
                                                </button>

                                                {order.status ===
                                                "Pending" && (
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
                                                                <span className="spinner-border spinner-border-sm me-1" />
                                                                Cancelling...
                                                            </>
                                                        ) : (
                                                            "Cancel"
                                                        )}
                                                    </button>
                                                )}

                                            </div>

                                        </div>

                                    </div>

                                    {/* =====================================
                                        ORDER DETAILS
                                    ====================================== */}

                                    {isExpanded && (

                                        <div className="card-body">

                                            <div className="row mb-4">

                                                <div className="col-md-6">

                                                    <h6>
                                                        Shipping Address
                                                    </h6>

                                                    <p className="text-muted mb-3">
                                                        {
                                                            order.shipping_address
                                                        }
                                                    </p>

                                                </div>

                                                <div className="col-md-6">

                                                    <h6>
                                                        Payment Method
                                                    </h6>

                                                    <p className="text-muted mb-3">
                                                        {
                                                            order.payment_method
                                                        }
                                                    </p>

                                                </div>

                                            </div>

                                            <div className="table-responsive">

                                                <table className="table table-bordered align-middle">

                                                    <thead className="table-light">

                                                        <tr>
                                                            <th>
                                                                Product
                                                            </th>

                                                            <th>
                                                                Qty
                                                            </th>

                                                            <th>
                                                                Unit Price
                                                            </th>

                                                            <th>
                                                                Subtotal
                                                            </th>
                                                        </tr>

                                                    </thead>

                                                    <tbody>

                                                        {order.items.map(
                                                            (
                                                                item
                                                            ) => (
                                                                <tr
                                                                    key={
                                                                        item.id
                                                                    }
                                                                >
                                                                    <td>
                                                                        {
                                                                            item.product_name
                                                                        }
                                                                    </td>

                                                                    <td>
                                                                        {
                                                                            item.quantity
                                                                        }
                                                                    </td>

                                                                    <td>
                                                                        ৳
                                                                        {Number(
                                                                            item.price
                                                                        ).toFixed(
                                                                            2
                                                                        )}
                                                                    </td>

                                                                    <td>
                                                                        ৳
                                                                        {Number(
                                                                            item.subtotal
                                                                        ).toFixed(
                                                                            2
                                                                        )}
                                                                    </td>
                                                                </tr>
                                                            )
                                                        )}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            </div>
        </div>
    );
};

export default Orders;