import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import { toast } from "react-toastify";
import { Link } from "react-router-dom";

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
    const [cancellingId, setCancellingId] = useState(null);
    const [expandedOrder, setExpandedOrder] = useState(null);
    const [search, setSearch] = useState("");


    // =========================================================
    // FETCH ORDERS
    // =========================================================

    const fetchOrders = useCallback(async () => {

        try {

            setLoading(true);

            const response = await getOrders();

            const data = response?.data;

            /*
             * Supports both:
             *
             * [
             *   {...},
             *   {...}
             * ]
             *
             * and:
             *
             * {
             *   results: [...]
             * }
             */

            if (Array.isArray(data)) {

                setOrders(data);

            } else if (
                Array.isArray(data?.results)
            ) {

                setOrders(data.results);

            } else {

                setOrders([]);

            }

        } catch (error) {

            console.error(
                "Fetch orders error:",
                error
            );

            // -------------------------------------------------
            // UNAUTHORIZED
            // -------------------------------------------------

            if (
                error?.response?.status === 401
            ) {

                localStorage.removeItem(
                    "access"
                );

                localStorage.removeItem(
                    "refresh"
                );

                toast.info(
                    "Please login again."
                );

                window.location.href =
                    "/login";

                return;
            }

            // -------------------------------------------------
            // ERROR MESSAGE
            // -------------------------------------------------

            toast.error(
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
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
    // SEARCH ORDERS
    // =========================================================

    const filteredOrders = useMemo(() => {

        const keyword =
            search.trim().toLowerCase();

        if (!keyword) {

            return orders;

        }

        return orders.filter((order) => {

            const orderNumber =
                `ORD${String(
                    order.id
                ).padStart(3, "0")}`;

            return (

                orderNumber
                    .toLowerCase()
                    .includes(keyword)

                ||

                String(order.id)
                    .includes(keyword)

                ||

                String(
                    order.status || ""
                )
                    .toLowerCase()
                    .includes(keyword)

                ||

                String(
                    order.payment_method || ""
                )
                    .toLowerCase()
                    .includes(keyword)

                ||

                String(
                    order.payment_status || ""
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

        if (!orderId) {

            return;

        }

        // -----------------------------------------------------
        // CONFIRMATION
        // -----------------------------------------------------

        const confirmed =
            window.confirm(
                "Are you sure you want to cancel this order?"
            );

        if (!confirmed) {

            return;

        }

        // -----------------------------------------------------
        // CANCEL REQUEST
        // -----------------------------------------------------

        try {

            setCancellingId(orderId);

            const response =
                await cancelOrder(
                    orderId
                );

            toast.success(
                response?.message ||
                response?.data?.message ||
                "Order cancelled successfully."
            );

            // -------------------------------------------------
            // REFRESH ORDERS
            // -------------------------------------------------

            await fetchOrders();

        } catch (error) {

            console.error(
                "Cancel order error:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
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
                    aria-hidden="true"
                />

                <h4 className="mt-3">
                    Loading Orders...
                </h4>

            </div>

        );

    }


    // =========================================================
    // PAGE
    // =========================================================

    return (

        <div className="container py-5">

            {/* =================================================
                HEADER
            ================================================= */}

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


                {/* =================================================
                    SEARCH
                ================================================= */}

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


            {/* =================================================
                ORDER HISTORY
            ================================================= */}

            <div className="card shadow">

                <div className="card-header bg-primary text-white">

                    <h5 className="mb-0">
                        Order History
                    </h5>

                </div>


                <div className="card-body">

                    {/* =================================================
                        NO ORDERS
                    ================================================= */}

                    {filteredOrders.length === 0 ? (

                        <div className="text-center py-5">

                            <h5>
                                No orders found.
                            </h5>

                            <p className="text-muted mb-0">

                                {search
                                    ? "No orders match your search."
                                    : "You haven't placed any orders yet."
                                }

                            </p>

                        </div>

                    ) : (

                        filteredOrders.map(
                            (order) => {

                                const orderNumber =
                                    `ORD${String(
                                        order.id
                                    ).padStart(
                                        3,
                                        "0"
                                    )}`;

                                const isExpanded =
                                    expandedOrder ===
                                    order.id;

                                return (

                                    <div
                                        key={order.id}
                                        className="card mb-4 border"
                                    >

                                        {/* =================================================
                                            ORDER HEADER
                                        ================================================= */}

                                        <div className="card-header bg-light">

                                            <div className="row align-items-center">

                                                {/* =========================================
                                                    ORDER NUMBER
                                                ========================================= */}

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
                                                            : "N/A"
                                                        }

                                                    </div>

                                                </div>


                                                {/* =========================================
                                                    STATUS
                                                ========================================= */}

                                                <div className="col-lg-2 mt-2 mt-lg-0">

                                                    <span
                                                        className={getStatusBadge(
                                                            order.status
                                                        )}
                                                    >

                                                        {order.status}

                                                    </span>

                                                </div>


                                                {/* =========================================
                                                    ITEMS
                                                ========================================= */}

                                                <div className="col-lg-2 mt-2 mt-lg-0">

                                                    <strong>
                                                        {order.item_count ??
                                                            order.items?.length ??
                                                            0
                                                        }
                                                    </strong>

                                                    <div className="small text-muted">
                                                        Items
                                                    </div>

                                                </div>


                                                {/* =========================================
                                                    TOTAL
                                                ========================================= */}

                                                <div className="col-lg-2 mt-2 mt-lg-0">

                                                    <strong>

                                                        ৳
                                                        {Number(
                                                            order.total_amount ||
                                                            0
                                                        ).toFixed(2)}

                                                    </strong>

                                                    <div className="small text-muted">
                                                        Total
                                                    </div>

                                                </div>


                                                {/* =========================================
                                                    ACTIONS
                                                ========================================= */}

                                                <div className="col-lg-3 text-lg-end mt-3 mt-lg-0">

                                                    {/* =====================================
                                                        VIEW DETAILS
                                                    ===================================== */}

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
                                                            : "View Details"
                                                        }

                                                    </button>

                                                    <Link
                                                        to={`/orders/${order.id}`}
                                                        className="btn btn-outline-secondary btn-sm me-2"
                                                    >
                                                        Track Order
                                                    </Link>


                                                    {/* =====================================
                                                        CANCEL ORDER

                                                        IMPORTANT:
                                                        Backend controls can_cancel.

                                                        No stock_deducted is used.
                                                    ===================================== */}

                                                    {order.can_cancel && (

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
                                                                        aria-hidden="true"
                                                                    />

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


                                        {/* =================================================
                                            ORDER DETAILS
                                        ================================================= */}

                                        {isExpanded && (

                                            <div className="card-body">

                                                {/* =========================================
                                                    ORDER INFORMATION
                                                ========================================= */}

                                                <div className="row mb-4">

                                                    {/* =====================================
                                                        SHIPPING ADDRESS
                                                    ===================================== */}

                                                    <div className="col-md-6">

                                                        <h6>
                                                            Shipping Address
                                                        </h6>

                                                        <p className="text-muted mb-3">

                                                            {
                                                                order.shipping_address ||
                                                                "N/A"
                                                            }

                                                        </p>

                                                    </div>


                                                    {/* =====================================
                                                        PAYMENT METHOD
                                                    ===================================== */}

                                                    <div className="col-md-6">

                                                        <h6>
                                                            Payment Method
                                                        </h6>

                                                        <p className="text-muted mb-3">

                                                            {
                                                                order.payment_method ||
                                                                "N/A"
                                                            }

                                                        </p>

                                                    </div>

                                                </div>


                                                {/* =================================================
                                                    PAYMENT STATUS
                                                ================================================= */}

                                                {order.payment_status && (

                                                    <div className="mb-3">

                                                        <strong>
                                                            Payment Status:
                                                        </strong>

                                                        <span className="ms-2">

                                                            {
                                                                order.payment_status
                                                            }

                                                        </span>

                                                    </div>

                                                )}


                                                {/* =================================================
                                                    TRANSACTION ID
                                                ================================================= */}

                                                {order.transaction_id && (

                                                    <div className="mb-3">

                                                        <strong>
                                                            Transaction ID:
                                                        </strong>

                                                        <span className="ms-2 text-muted">

                                                            {
                                                                order.transaction_id
                                                            }

                                                        </span>

                                                    </div>

                                                )}


                                                {/* =================================================
                                                    ORDER ITEMS
                                                ================================================= */}

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

                                                            {Array.isArray(
                                                                order.items
                                                            ) &&
                                                            order.items.length > 0 ? (

                                                                order.items.map(
                                                                    (item) => (

                                                                        <tr
                                                                            key={
                                                                                item.id
                                                                            }
                                                                        >

                                                                            {/* =================================
                                                                                PRODUCT
                                                                            ================================= */}

                                                                            <td>

                                                                                {
                                                                                    item.product_name ||
                                                                                    item.product ||
                                                                                    "Product"
                                                                                }

                                                                            </td>


                                                                            {/* =================================
                                                                                QUANTITY
                                                                            ================================= */}

                                                                            <td>

                                                                                {
                                                                                    item.quantity
                                                                                }

                                                                            </td>


                                                                            {/* =================================
                                                                                UNIT PRICE
                                                                            ================================= */}

                                                                            <td>

                                                                                ৳
                                                                                {Number(
                                                                                    item.price ||
                                                                                    0
                                                                                ).toFixed(
                                                                                    2
                                                                                )}

                                                                            </td>


                                                                            {/* =================================
                                                                                SUBTOTAL
                                                                            ================================= */}

                                                                            <td>

                                                                                ৳
                                                                                {Number(
                                                                                    item.subtotal ??
                                                                                    (
                                                                                        Number(
                                                                                            item.price ||
                                                                                            0
                                                                                        ) *
                                                                                        Number(
                                                                                            item.quantity ||
                                                                                            0
                                                                                        )
                                                                                    )
                                                                                ).toFixed(
                                                                                    2
                                                                                )}

                                                                            </td>

                                                                        </tr>

                                                                    )

                                                                )

                                                            ) : (

                                                                <tr>

                                                                    <td
                                                                        colSpan="4"
                                                                        className="text-center text-muted"
                                                                    >

                                                                        No order items found.

                                                                    </td>

                                                                </tr>

                                                            )}

                                                        </tbody>

                                                    </table>

                                                </div>


                                                {/* =================================================
                                                    ORDER SUMMARY
                                                ================================================= */}

                                                <div className="row justify-content-end">

                                                    <div className="col-md-5 col-lg-4">

                                                        <div className="border rounded p-3">

                                                            {/* =====================================
                                                                SUBTOTAL
                                                            ===================================== */}

                                                            <div className="d-flex justify-content-between mb-2">

                                                                <span>
                                                                    Subtotal
                                                                </span>

                                                                <strong>

                                                                    ৳
                                                                    {Number(
                                                                        order.subtotal ||
                                                                        0
                                                                    ).toFixed(2)}

                                                                </strong>

                                                            </div>


                                                            {/* =====================================
                                                                DELIVERY
                                                            ===================================== */}

                                                            <div className="d-flex justify-content-between mb-2">

                                                                <span>
                                                                    Delivery Charge
                                                                </span>

                                                                <strong>

                                                                    ৳
                                                                    {Number(
                                                                        order.delivery_charge ||
                                                                        0
                                                                    ).toFixed(2)}

                                                                </strong>

                                                            </div>


                                                            <hr />


                                                            {/* =====================================
                                                                TOTAL
                                                            ===================================== */}

                                                            <div className="d-flex justify-content-between">

                                                                <strong>
                                                                    Total
                                                                </strong>

                                                                <strong>

                                                                    ৳
                                                                    {Number(
                                                                        order.total_amount ||
                                                                        0
                                                                    ).toFixed(2)}

                                                                </strong>

                                                            </div>

                                                        </div>

                                                    </div>

                                                </div>

                                            </div>

                                        )}

                                    </div>

                                );

                            }

                        )

                    )}

                </div>

            </div>

        </div>

    );

};


export default Orders;