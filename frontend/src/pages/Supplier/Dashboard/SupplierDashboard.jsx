import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    getSupplierDashboard,
} from "../../../services/supplierService";

import {
    getSupplierOrders,
    updateSupplierOrderItemStatus,
} from "../../../services/orderService";


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
// STATUS BADGE
// ==========================================================

function StatusBadge({
    status,
}) {
    const normalizedStatus =
        String(status || "").trim();

    let className =
        "badge bg-secondary";

    if (normalizedStatus === "Pending") {
        className =
            "badge bg-warning text-dark";
    }

    if (normalizedStatus === "Processing") {
        className =
            "badge bg-primary";
    }

    if (normalizedStatus === "Ready") {
        className =
            "badge bg-success";
    }

    if (normalizedStatus === "Assigned") {
        className =
            "badge bg-secondary";
    }

    if (normalizedStatus === "Out for Delivery") {
        className =
            "badge bg-dark";
    }

    if (normalizedStatus === "Delivered") {
        className =
            "badge bg-success";
    }

    if (normalizedStatus === "Cancelled") {
        className =
            "badge bg-secondary";
    }

    return (
        <span className={className}>
            {normalizedStatus || "Unknown"}
        </span>
    );
}


// ==========================================================
// SUPPLIER ITEM ACTION
// ==========================================================

function SupplierItemAction({
    item,
    updatingItemId,
    onUpdate,
}) {
    const status =
        String(
            item?.supplier_status || "Pending"
        ).trim();

    const isUpdating =
        updatingItemId === item?.id;


    // ======================================================
    // PENDING → PROCESSING
    // ======================================================

    if (status === "Pending") {

        return (
            <button
                type="button"
                className="btn btn-primary btn-sm"
                disabled={isUpdating}
                onClick={() =>
                    onUpdate(
                        item.id,
                        "Processing"
                    )
                }
            >

                {isUpdating ? (
                    <>
                        <span
                            className="spinner-border spinner-border-sm me-2"
                            role="status"
                            aria-hidden="true"
                        />

                        Processing...
                    </>
                ) : (
                    "Start Processing"
                )}

            </button>
        );
    }


    // ======================================================
    // PROCESSING → READY
    // ======================================================

    if (status === "Processing") {

        return (
            <button
                type="button"
                className="btn btn-success btn-sm"
                disabled={isUpdating}
                onClick={() =>
                    onUpdate(
                        item.id,
                        "Ready"
                    )
                }
            >

                {isUpdating ? (
                    <>
                        <span
                            className="spinner-border spinner-border-sm me-2"
                            role="status"
                            aria-hidden="true"
                        />

                        Updating...
                    </>
                ) : (
                    "Mark Ready"
                )}

            </button>
        );
    }


    // ======================================================
    // READY
    // ======================================================

    if (status === "Ready") {

        return (
            <span className="text-success small fw-semibold">
                Ready — No further action
            </span>
        );
    }


    // ======================================================
    // CANCELLED
    // ======================================================

    if (status === "Cancelled") {

        return (
            <span className="text-danger small fw-semibold">
                Cancelled
            </span>
        );
    }


    // ======================================================
    // UNKNOWN / OTHER STATUS
    // ======================================================

    return (
        <span className="text-muted small">
            No action available
        </span>
    );
}


// ==========================================================
// SUPPLIER ORDER WORKFLOW
// ==========================================================

function SupplierOrderWorkflow({
    orders,
    loading,
    updatingItemId,
    onUpdate,
}) {

    return (
        <div className="card border-0 shadow-sm mb-4">

            <div className="card-header bg-white py-3">

                <h5 className="mb-1 fw-bold">
                    Supplier Order Workflow
                </h5>

                <p className="text-muted small mb-0">
                    Process your own order items from{" "}
                    <strong>
                        Pending → Processing → Ready
                    </strong>.
                    The parent order status is updated
                    automatically.
                </p>

            </div>


            <div className="card-body">


                {/* ==================================================
                    WORKFLOW EXPLANATION
                ================================================== */}

                <div className="row g-3 mb-4">

                    <div className="col-md-4">

                        <div className="border rounded p-3 h-100">

                            <div className="d-flex align-items-center gap-2 mb-2">

                                <StatusBadge
                                    status="Pending"
                                />

                                <span>
                                    →
                                </span>

                                <StatusBadge
                                    status="Processing"
                                />

                            </div>

                            <h6 className="fw-bold">
                                Pending → Processing
                            </h6>

                            <p className="text-muted small mb-0">
                                Click{" "}
                                <strong>
                                    Start Processing
                                </strong>{" "}
                                when you begin preparing
                                your item.
                            </p>

                        </div>

                    </div>


                    <div className="col-md-4">

                        <div className="border rounded p-3 h-100">

                            <div className="d-flex align-items-center gap-2 mb-2">

                                <StatusBadge
                                    status="Processing"
                                />

                                <span>
                                    →
                                </span>

                                <StatusBadge
                                    status="Ready"
                                />

                            </div>

                            <h6 className="fw-bold">
                                Processing → Ready
                            </h6>

                            <p className="text-muted small mb-0">
                                Click{" "}
                                <strong>
                                    Mark Ready
                                </strong>{" "}
                                when your item is
                                completely prepared.
                            </p>

                        </div>

                    </div>


                    <div className="col-md-4">

                        <div className="border rounded p-3 h-100">

                            <div className="d-flex align-items-center gap-2 mb-2">

                                <StatusBadge
                                    status="Ready"
                                />

                            </div>

                            <h6 className="fw-bold">
                                Ready + All Items Ready
                            </h6>

                            <p className="text-muted small mb-0">
                                No further supplier action
                                is required. Admin can
                                assign a delivery rider.
                            </p>

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    ORDER ITEMS
                ================================================== */}

                <div className="border-top pt-4">

                    <div className="d-flex justify-content-between align-items-center mb-3">

                        <div>

                            <h6 className="fw-bold mb-1">
                                My Order Items
                            </h6>

                            <small className="text-muted">
                                Update only the products
                                supplied by you.
                            </small>

                        </div>

                    </div>


                    {loading ? (

                        <div className="text-center py-4">

                            <div
                                className="spinner-border"
                                role="status"
                            >
                                <span className="visually-hidden">
                                    Loading orders...
                                </span>
                            </div>

                            <p className="text-muted mt-2 mb-0">
                                Loading supplier orders...
                            </p>

                        </div>

                    ) : orders.length === 0 ? (

                        <div className="alert alert-light border mb-0">
                            No supplier orders are available.
                        </div>

                    ) : (

                        <div
                            className="accordion"
                            id="supplierOrdersAccordion"
                        >

                            {orders.map(
                                (
                                    order,
                                    orderIndex
                                ) => {

                                    const items =
                                        Array.isArray(
                                            order?.items
                                        )
                                            ? order.items
                                            : [];


                                    const allItemsReady =
                                        items.length > 0 &&
                                        items.every(
                                            (item) =>
                                                item?.supplier_status ===
                                                "Ready"
                                        );


                                    const someItemsProcessing =
                                        items.some(
                                            (item) =>
                                                item?.supplier_status ===
                                                "Processing"
                                        );


                                    const someItemsPending =
                                        items.some(
                                            (item) =>
                                                item?.supplier_status ===
                                                "Pending"
                                        );


                                    return (
                                        <div
                                            className="accordion-item"
                                            key={
                                                order.id ||
                                                orderIndex
                                            }
                                        >

                                            {/* ==============================================
                                                ORDER HEADER
                                            ============================================== */}

                                            <h2
                                                className="accordion-header"
                                                id={`supplier-order-heading-${order.id}`}
                                            >

                                                <button
                                                    className={`accordion-button ${
                                                        orderIndex !== 0
                                                            ? "collapsed"
                                                            : ""
                                                    }`}
                                                    type="button"
                                                    data-bs-toggle="collapse"
                                                    data-bs-target={`#supplier-order-collapse-${order.id}`}
                                                    aria-expanded={
                                                        orderIndex === 0
                                                    }
                                                    aria-controls={`supplier-order-collapse-${order.id}`}
                                                >

                                                    <div className="w-100 pe-3">

                                                        <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">

                                                            <div>

                                                                <strong>
                                                                    {order.order_number ||
                                                                        `Order #${order.id}`}
                                                                </strong>

                                                                <div className="small text-muted mt-1">

                                                                    Customer:{" "}

                                                                    {order.customer_name ||
                                                                        order.customer ||
                                                                        "Customer"}

                                                                </div>

                                                            </div>


                                                            <div className="d-flex align-items-center gap-2">

                                                                <StatusBadge
                                                                    status={
                                                                        order.status
                                                                    }
                                                                />

                                                            </div>

                                                        </div>

                                                    </div>

                                                </button>

                                            </h2>


                                            {/* ==============================================
                                                ORDER BODY
                                            ============================================== */}

                                            <div
                                                id={`supplier-order-collapse-${order.id}`}
                                                className={`accordion-collapse collapse ${
                                                    orderIndex === 0
                                                        ? "show"
                                                        : ""
                                                }`}
                                                aria-labelledby={`supplier-order-heading-${order.id}`}
                                                data-bs-parent="#supplierOrdersAccordion"
                                            >

                                                <div className="accordion-body">


                                                    {/* ==========================================
                                                        ORDER SUMMARY
                                                    ========================================== */}

                                                    <div className="row mb-3">

                                                        <div className="col-md-4">

                                                            <small className="text-muted d-block">
                                                                Parent Order Status
                                                            </small>

                                                            <div className="mt-1">

                                                                <StatusBadge
                                                                    status={
                                                                        order.status
                                                                    }
                                                                />

                                                            </div>

                                                        </div>


                                                        <div className="col-md-4">

                                                            <small className="text-muted d-block">
                                                                Supplier Items
                                                            </small>

                                                            <strong>
                                                                {items.length}
                                                            </strong>

                                                        </div>


                                                        <div className="col-md-4">

                                                            <small className="text-muted d-block">
                                                                Total
                                                            </small>

                                                            <strong>
                                                                ৳
                                                                {Number(
                                                                    order.total_amount ??
                                                                    0
                                                                ).toLocaleString(
                                                                    "en-BD",
                                                                    {
                                                                        minimumFractionDigits: 2,
                                                                        maximumFractionDigits: 2,
                                                                    }
                                                                )}
                                                            </strong>

                                                        </div>

                                                    </div>


                                                    {/* ==========================================
                                                        PARENT ORDER WORKFLOW MESSAGE
                                                    ========================================== */}

                                                    {allItemsReady ? (

                                                        <div className="alert alert-success">

                                                            <strong>
                                                                All your supplier
                                                                items are Ready.
                                                            </strong>

                                                            <div className="small mt-1">
                                                                No further supplier
                                                                action is required.
                                                                The parent order is
                                                                ready for Admin to
                                                                assign a specific
                                                                delivery rider.
                                                            </div>

                                                        </div>

                                                    ) : someItemsProcessing ? (

                                                        <div className="alert alert-info">

                                                            <strong>
                                                                Your order items
                                                                are being processed.
                                                            </strong>

                                                            <div className="small mt-1">
                                                                Continue processing
                                                                any remaining
                                                                Pending items and
                                                                mark each completed
                                                                item as Ready.
                                                            </div>

                                                        </div>

                                                    ) : someItemsPending ? (

                                                        <div className="alert alert-warning">

                                                            <strong>
                                                                Some items are still
                                                                Pending.
                                                            </strong>

                                                            <div className="small mt-1">
                                                                Start processing
                                                                your Pending items
                                                                using the buttons
                                                                below.
                                                            </div>

                                                        </div>

                                                    ) : null}


                                                    {/* ==========================================
                                                        ITEM TABLE
                                                    ========================================== */}

                                                    {items.length === 0 ? (

                                                        <div className="alert alert-light border">
                                                            No supplier items
                                                            found for this order.
                                                        </div>

                                                    ) : (

                                                        <div className="table-responsive">

                                                            <table className="table table-hover align-middle mb-0">

                                                                <thead>

                                                                    <tr>

                                                                        <th>
                                                                            Product
                                                                        </th>

                                                                        <th>
                                                                            Quantity
                                                                        </th>

                                                                        <th>
                                                                            Price
                                                                        </th>

                                                                        <th>
                                                                            Subtotal
                                                                        </th>

                                                                        <th>
                                                                            Supplier Status
                                                                        </th>

                                                                        <th className="text-end">
                                                                            Action
                                                                        </th>

                                                                    </tr>

                                                                </thead>


                                                                <tbody>

                                                                    {items.map(
                                                                        (item) => (

                                                                            <tr
                                                                                key={
                                                                                    item.id
                                                                                }
                                                                            >

                                                                                <td>

                                                                                    <div className="fw-semibold">
                                                                                        {
                                                                                            item.product_name ||
                                                                                            item.product?.name ||
                                                                                            "Product"
                                                                                        }
                                                                                    </div>

                                                                                </td>


                                                                                <td>
                                                                                    {
                                                                                        item.quantity ??
                                                                                        0
                                                                                    }
                                                                                </td>


                                                                                <td>
                                                                                    ৳
                                                                                    {Number(
                                                                                        item.price ??
                                                                                        0
                                                                                    ).toLocaleString(
                                                                                        "en-BD",
                                                                                        {
                                                                                            minimumFractionDigits: 2,
                                                                                            maximumFractionDigits: 2,
                                                                                        }
                                                                                    )}
                                                                                </td>


                                                                                <td>
                                                                                    ৳
                                                                                    {Number(
                                                                                        item.subtotal ??
                                                                                        (
                                                                                            Number(
                                                                                                item.price ??
                                                                                                0
                                                                                            ) *
                                                                                            Number(
                                                                                                item.quantity ??
                                                                                                0
                                                                                            )
                                                                                        )
                                                                                    ).toLocaleString(
                                                                                        "en-BD",
                                                                                        {
                                                                                            minimumFractionDigits: 2,
                                                                                            maximumFractionDigits: 2,
                                                                                        }
                                                                                    )}
                                                                                </td>


                                                                                <td>

                                                                                    <StatusBadge
                                                                                        status={
                                                                                            item.supplier_status
                                                                                        }
                                                                                    />

                                                                                </td>


                                                                                <td className="text-end">

                                                                                    <SupplierItemAction
                                                                                        item={
                                                                                            item
                                                                                        }
                                                                                        updatingItemId={
                                                                                            updatingItemId
                                                                                        }
                                                                                        onUpdate={
                                                                                            onUpdate
                                                                                        }
                                                                                    />

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
                                    );
                                }
                            )}

                        </div>

                    )}

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

    const [supplierOrders, setSupplierOrders] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [ordersLoading, setOrdersLoading] =
        useState(true);

    const [updatingItemId, setUpdatingItemId] =
        useState(null);

    const [error, setError] =
        useState("");

    const [orderError, setOrderError] =
        useState("");


    // ==========================================================
    // LOAD DASHBOARD
    // ==========================================================

    const loadDashboard = useCallback(
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
    // LOAD SUPPLIER ORDERS
    // ==========================================================

    const loadSupplierOrders = useCallback(
        async () => {

            try {

                setOrdersLoading(true);
                setOrderError("");


                const response =
                    await getSupplierOrders();


                // ==================================================
                // NORMALIZE SUPPLIER ORDER RESPONSE
                // ==================================================
                //
                // Axios normally returns:
                //
                // response.data
                //
                // The backend may return:
                //
                // 1. Array
                // 2. { results: [...] }
                // 3. { orders: [...] }
                //
                // This function supports all of those forms.
                // ==================================================

                let orders = [];


                // --------------------------------------------------
                // CASE 1
                // Service directly returns an array
                // --------------------------------------------------

                if (Array.isArray(response)) {

                    orders = response;

                }


                // --------------------------------------------------
                // CASE 2
                // Axios response.data is an array
                // --------------------------------------------------

                else if (
                    Array.isArray(
                        response?.data
                    )
                ) {

                    orders =
                        response.data;

                }


                // --------------------------------------------------
                // CASE 3
                // Direct object with orders
                // --------------------------------------------------

                else if (
                    Array.isArray(
                        response?.orders
                    )
                ) {

                    orders =
                        response.orders;

                }


                // --------------------------------------------------
                // CASE 4
                // Axios response.data contains orders
                // --------------------------------------------------

                else if (
                    Array.isArray(
                        response?.data?.orders
                    )
                ) {

                    orders =
                        response.data.orders;

                }


                // --------------------------------------------------
                // CASE 5
                // Direct paginated response
                // --------------------------------------------------

                else if (
                    Array.isArray(
                        response?.results
                    )
                ) {

                    orders =
                        response.results;

                }


                // --------------------------------------------------
                // CASE 6
                // Axios paginated response
                // --------------------------------------------------

                else if (
                    Array.isArray(
                        response?.data?.results
                    )
                ) {

                    orders =
                        response.data.results;

                }


                // --------------------------------------------------
                // SAVE ORDERS
                // --------------------------------------------------

                setSupplierOrders(
                    orders
                );


            } catch (error) {

                console.error(
                    "Supplier orders error:",
                    error
                );

                if (
                    error.response?.status === 401
                ) {

                    setOrderError(
                        "Your session has expired. Please login again."
                    );

                } else if (
                    error.response?.status === 403
                ) {

                    setOrderError(
                        "You are not authorized to view supplier orders."
                    );

                } else {

                    setOrderError(
                        "Failed to load supplier order items."
                    );
                }

                setSupplierOrders([]);

            } finally {

                setOrdersLoading(false);
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

                void loadDashboard();
                void loadSupplierOrders();

            }, 0);

        return () => {

            clearTimeout(timer);

        };

    }, [
        loadDashboard,
        loadSupplierOrders,
    ]);


    // ==========================================================
    // UPDATE SUPPLIER ITEM STATUS
    // ==========================================================

    const handleSupplierItemStatusUpdate =
        async (
            itemId,
            nextStatus
        ) => {

            if (!itemId) {
                return;
            }


            if (
                ![
                    "Processing",
                    "Ready",
                ].includes(nextStatus)
            ) {
                return;
            }


            try {

                setUpdatingItemId(
                    itemId
                );

                setOrderError("");


                // ==================================================
                // UPDATE ITEM
                // ==================================================

                await updateSupplierOrderItemStatus(
                    itemId,
                    nextStatus
                );


                // ==================================================
                // REFRESH ORDERS
                // ==================================================
                //
                // This is important because the backend updates
                // the parent order automatically.
                //
                // Pending → Processing
                //
                // Processing → Ready
                //
                // when all supplier items are ready.
                // ==================================================

                await loadSupplierOrders();


                // ==================================================
                // REFRESH DASHBOARD STATISTICS
                // ==================================================

                await loadDashboard();


            } catch (error) {

                console.error(
                    "Supplier item status update error:",
                    error
                );


                let message =
                    "Failed to update item status.";


                if (
                    error.response?.data
                ) {

                    const data =
                        error.response.data;


                    if (
                        typeof data.detail ===
                        "string"
                    ) {

                        message =
                            data.detail;

                    } else if (
                        typeof data.message ===
                        "string"
                    ) {

                        message =
                            data.message;

                    } else if (
                        typeof data.error ===
                        "string"
                    ) {

                        message =
                            data.error;
                    }

                }


                setOrderError(
                    message
                );

            } finally {

                setUpdatingItemId(
                    null
                );
            }
        };


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

    const formatCurrency = (
        value
    ) => {

        const numericValue =
            Number(
                value ?? 0
            );

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


    const formatDate = (
        value
    ) => {

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
                    value={
                        formatCurrency(
                            statistics.total_income ??
                            0
                        )
                    }
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

            <SupplierOrderWorkflow
                orders={
                    supplierOrders
                }
                loading={
                    ordersLoading
                }
                updatingItemId={
                    updatingItemId
                }
                onUpdate={
                    handleSupplierItemStatusUpdate
                }
            />


            {/* ==================================================
                ORDER ERROR
            ================================================== */}

            {orderError && (

                <div
                    className="alert alert-danger alert-dismissible fade show"
                    role="alert"
                >

                    {orderError}

                    <button
                        type="button"
                        className="btn-close"
                        aria-label="Close"
                        onClick={() =>
                            setOrderError("")
                        }
                    />

                </div>

            )}


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
                                                                order.customer_name ||
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
                                                            {
                                                                formatCurrency(
                                                                    order.total_amount ??
                                                                    0
                                                                )
                                                            }
                                                        </td>


                                                        <td>
                                                            {
                                                                formatDate(
                                                                    order.date ||
                                                                    order.created_at
                                                                )
                                                            }
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

                                                        {
                                                            formatDate(
                                                                notification.date ||
                                                                notification.created_at
                                                            )
                                                        }

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
                                                            {
                                                                formatCurrency(
                                                                    product.price ??
                                                                    0
                                                                )
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
                                        (
                                            entry,
                                            index
                                        ) => {

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
                                                            {
                                                                formatCurrency(
                                                                    entry.amount ??
                                                                    0
                                                                )
                                                            }
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