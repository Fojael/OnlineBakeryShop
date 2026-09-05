import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Link,
    useParams,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    getSupplierOrder,
    updateSupplierOrderItemStatus,
} from "../../../services/orderService";


// ==========================================================
// STATUS BADGE
// ==========================================================

const getStatusBadgeClass = (status) => {
    switch (status) {
        case "Pending":
            return "bg-warning text-dark";

        case "Processing":
            return "bg-primary";

        case "Ready":
            return "bg-info text-dark";

        case "Delivered":
            return "bg-success";

        case "Cancelled":
            return "bg-danger";

        case "Accepted":
            return "bg-secondary";

        case "Assigned":
            return "bg-secondary";

        case "Out for Delivery":
            return "bg-primary";

        default:
            return "bg-secondary";
    }
};


// ==========================================================
// CURRENCY
// ==========================================================

const formatCurrency = (value) => {
    const numeric = Number(value || 0);

    if (!Number.isFinite(numeric)) {
        return "৳0.00";
    }

    return `৳${numeric.toFixed(2)}`;
};


// ==========================================================
// DATE
// ==========================================================

const formatDate = (value) => {
    if (!value) {
        return "N/A";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "N/A";
    }

    return date.toLocaleString("en-BD", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};


// ==========================================================
// SUPPLIER ORDER DETAILS
// ==========================================================

const SupplierOrderDetails = () => {
    const { id } = useParams();

    const [order, setOrder] = useState(null);

    const [loading, setLoading] = useState(true);

    const [refreshing, setRefreshing] =
        useState(false);

    const [updatingItemId, setUpdatingItemId] =
        useState(null);


    // ==========================================================
    // LOAD ORDER
    // ==========================================================

    const loadOrder = useCallback(
        async ({
            showLoader = false,
        } = {}) => {
            try {
                if (showLoader) {
                    setLoading(true);
                } else {
                    setRefreshing(true);
                }

                const response =
                    await getSupplierOrder(id);

                const data =
                    response?.data ||
                    response ||
                    null;

                setOrder(data);
            } catch (error) {
                console.error(
                    "Failed to load supplier order details:",
                    error
                );

                if (!order) {
                    toast.error(
                        error?.response?.data?.detail ||
                            "Failed to load order details."
                    );
                } else {
                    toast.error(
                        "Failed to refresh order details."
                    );
                }
            } finally {
                if (showLoader) {
                    setLoading(false);
                } else {
                    setRefreshing(false);
                }
            }
        },
        [id, order]
    );


    // ==========================================================
    // INITIAL LOAD
    // ==========================================================

    useEffect(() => {
        let isMounted = true;

        const fetchOrder = async () => {
            try {
                setLoading(true);

                const response =
                    await getSupplierOrder(id);

                if (!isMounted) {
                    return;
                }

                const data =
                    response?.data ||
                    response ||
                    null;

                setOrder(data);
            } catch (error) {
                console.error(
                    "Failed to load supplier order details:",
                    error
                );

                if (isMounted) {
                    toast.error(
                        error?.response?.data?.detail ||
                            "Failed to load order details."
                    );
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        void fetchOrder();

        return () => {
            isMounted = false;
        };
    }, [id]);


    // ==========================================================
    // ITEM TOTAL
    // ==========================================================

    const itemTotal = useMemo(() => {
        if (!Array.isArray(order?.items)) {
            return 0;
        }

        return order.items.reduce(
            (sum, item) =>
                sum +
                Number(item.subtotal || 0),
            0
        );
    }, [order]);


    // ==========================================================
    // NEXT STATUS
    // ==========================================================

    const getNextStatus = (currentStatus) => {
        switch (currentStatus) {
            case "Pending":
                return "Processing";

            case "Processing":
                return "Ready";

            case "Ready":
                return null;

            default:
                return null;
        }
    };


    // ==========================================================
    // BUTTON TEXT
    // ==========================================================

    const getStatusButtonText = (
        currentStatus
    ) => {
        switch (currentStatus) {
            case "Pending":
                return "Start Processing";

            case "Processing":
                return "Mark Ready";

            case "Ready":
                return "Ready";

            default:
                return "No Action";
        }
    };


    // ==========================================================
    // STATUS UPDATE
    // ==========================================================

    const handleStatusChange = async (
        item
    ) => {
        const currentStatus =
            item.supplier_status || "Pending";

        const nextStatus =
            getNextStatus(currentStatus);

        // Ready has no next supplier action.
        if (!nextStatus) {
            return;
        }

        try {
            setUpdatingItemId(item.id);

            // --------------------------------------------------
            // CORRECT API CALL
            // --------------------------------------------------

            await updateSupplierOrderItemStatus(
                item.id,
                nextStatus
            );

            // --------------------------------------------------
            // REFRESH FROM BACKEND
            // --------------------------------------------------
            // This is important because the backend also
            // updates the parent Order status:
            //
            // Pending -> Processing
            // Processing -> Ready
            //
            // depending on all supplier items.
            // --------------------------------------------------

            await loadOrder();

            toast.success(
                `Product status changed from ${currentStatus} to ${nextStatus}.`
            );
        } catch (error) {
            console.error(
                "Failed to update supplier order item status:",
                error
            );

            const serverMessage =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                "Failed to update supplier item status.";

            toast.error(serverMessage);
        } finally {
            setUpdatingItemId(null);
        }
    };


    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {
        return (
            <div className="container py-4">

                <div className="text-center py-5">

                    <div
                        className="spinner-border"
                        role="status"
                    />

                    <p className="mt-3 mb-0">
                        Loading order details...
                    </p>

                </div>

            </div>
        );
    }


    // ==========================================================
    // NOT FOUND
    // ==========================================================

    if (!order) {
        return (
            <div className="container py-4">

                <div className="alert alert-danger">
                    Order not found or access is
                    restricted.
                </div>

                <Link
                    to="/supplier/orders"
                    className="btn btn-primary"
                >
                    Back to Orders
                </Link>

            </div>
        );
    }


    // ==========================================================
    // ITEMS
    // ==========================================================

    const supplierItems =
        Array.isArray(order.items)
            ? order.items
            : [];


    return (
        <div className="container py-4">

            {/* HEADER */}

            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">

                <div>

                    <h2 className="fw-bold mb-1">
                        Order Details
                    </h2>

                    <p className="text-muted mb-0">
                        Order #{order.id}
                    </p>

                </div>


                <div className="d-flex gap-2">

                    {refreshing && (
                        <span className="text-muted align-self-center">
                            Refreshing...
                        </span>
                    )}

                    <Link
                        to="/supplier/orders"
                        className="btn btn-outline-secondary"
                    >
                        Back to Orders
                    </Link>

                </div>

            </div>


            {/* ORDER INFORMATION */}

            <div className="row g-4 mb-4">

                {/* CUSTOMER */}

                <div className="col-lg-6">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-body">

                            <h5 className="fw-bold mb-3">
                                Customer Information
                            </h5>

                            <p className="mb-2">
                                <strong>Name:</strong>{" "}
                                {order.customer_name ||
                                    "Unknown"}
                            </p>

                            <p className="mb-2">
                                <strong>Email:</strong>{" "}
                                {order.customer_email ||
                                    "N/A"}
                            </p>

                            <p className="mb-2">
                                <strong>Address:</strong>{" "}
                                {order.shipping_address ||
                                    "N/A"}
                            </p>

                            <p className="mb-0">
                                <strong>
                                    Order Date:
                                </strong>{" "}
                                {formatDate(
                                    order.created_at
                                )}
                            </p>

                        </div>

                    </div>

                </div>


                {/* SUMMARY */}

                <div className="col-lg-6">

                    <div className="card border-0 shadow-sm h-100">

                        <div className="card-body">

                            <h5 className="fw-bold mb-3">
                                Order Summary
                            </h5>

                            <p className="mb-2">

                                <strong>
                                    Order Status:
                                </strong>{" "}

                                <span
                                    className={`badge ${getStatusBadgeClass(
                                        order.status
                                    )}`}
                                >
                                    {order.status ||
                                        "Pending"}
                                </span>

                            </p>

                            <p className="mb-2">

                                <strong>
                                    Payment Status:
                                </strong>{" "}

                                <span className="badge bg-secondary">
                                    {order.payment_status ||
                                        "Pending"}
                                </span>

                            </p>

                            <p className="mb-2">

                                <strong>
                                    Payment Method:
                                </strong>{" "}

                                {order.payment_method ||
                                    "N/A"}

                            </p>

                            <p className="mb-0">

                                <strong>
                                    Supplier Items Total:
                                </strong>{" "}

                                {formatCurrency(
                                    itemTotal
                                )}

                            </p>

                        </div>

                    </div>

                </div>

            </div>


            {/* SUPPLIER PRODUCTS */}

            <div className="card shadow-sm border-0">

                <div className="card-body">

                    <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">

                        <div>

                            <h5 className="fw-bold mb-1">
                                Your Products in This Order
                            </h5>

                            <small className="text-muted">
                                You can process only the
                                products supplied by your
                                supplier account.
                            </small>

                        </div>

                    </div>


                    <div className="table-responsive">

                        <table className="table align-middle">

                            <thead className="table-light">

                                <tr>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Subtotal</th>
                                    <th>Supplier Status</th>
                                    <th>Action</th>
                                </tr>

                            </thead>


                            <tbody>

                                {supplierItems.length >
                                0 ? (
                                    supplierItems.map(
                                        (item) => {
                                            const currentStatus =
                                                item.supplier_status ||
                                                "Pending";

                                            const nextStatus =
                                                getNextStatus(
                                                    currentStatus
                                                );

                                            const isUpdating =
                                                updatingItemId ===
                                                item.id;

                                            const buttonText =
                                                getStatusButtonText(
                                                    currentStatus
                                                );

                                            return (
                                                <tr
                                                    key={
                                                        item.id
                                                    }
                                                >

                                                    {/* PRODUCT */}

                                                    <td>

                                                        <div className="fw-semibold">
                                                            {item.product_name ||
                                                                "Product"}
                                                        </div>

                                                    </td>


                                                    {/* QUANTITY */}

                                                    <td>
                                                        {
                                                            item.quantity
                                                        }
                                                    </td>


                                                    {/* PRICE */}

                                                    <td>
                                                        {formatCurrency(
                                                            item.price
                                                        )}
                                                    </td>


                                                    {/* SUBTOTAL */}

                                                    <td>
                                                        {formatCurrency(
                                                            item.subtotal
                                                        )}
                                                    </td>


                                                    {/* CURRENT STATUS */}

                                                    <td>

                                                        <span
                                                            className={`badge ${getStatusBadgeClass(
                                                                currentStatus
                                                            )}`}
                                                        >
                                                            {
                                                                currentStatus
                                                            }
                                                        </span>

                                                    </td>


                                                    {/* ACTION */}

                                                    <td>

                                                        {currentStatus ===
                                                        "Ready" ? (
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-success"
                                                                disabled
                                                            >
                                                                ✓ Ready
                                                            </button>
                                                        ) : currentStatus ===
                                                          "Cancelled" ? (
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-secondary"
                                                                disabled
                                                            >
                                                                Cancelled
                                                            </button>
                                                        ) : (
                                                            <button
                                                                type="button"
                                                                className={
                                                                    currentStatus ===
                                                                    "Pending"
                                                                        ? "btn btn-sm btn-primary"
                                                                        : "btn btn-sm btn-info"
                                                                }
                                                                onClick={() =>
                                                                    handleStatusChange(
                                                                        item
                                                                    )
                                                                }
                                                                disabled={
                                                                    isUpdating ||
                                                                    !nextStatus
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
                                                                    buttonText
                                                                )}
                                                            </button>
                                                        )}

                                                    </td>

                                                </tr>
                                            );
                                        }
                                    )
                                ) : (
                                    <tr>

                                        <td
                                            colSpan="6"
                                            className="text-center text-muted py-4"
                                        >
                                            No products from
                                            your supplier
                                            account are in
                                            this order.
                                        </td>

                                    </tr>
                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>


            {/* WORKFLOW INFORMATION */}

            <div className="card border-0 shadow-sm mt-4">

                <div className="card-body">

                    <h5 className="fw-bold mb-3">
                        Supplier Workflow
                    </h5>

                    <div className="row text-center">

                        <div className="col-md-4 mb-3">

                            <div className="border rounded p-3 h-100">

                                <span className="badge bg-warning text-dark mb-2">
                                    1
                                </span>

                                <h6 className="fw-bold">
                                    Pending
                                </h6>

                                <p className="text-muted small mb-0">
                                    Start processing your
                                    product.
                                </p>

                            </div>

                        </div>


                        <div className="col-md-4 mb-3">

                            <div className="border rounded p-3 h-100">

                                <span className="badge bg-primary mb-2">
                                    2
                                </span>

                                <h6 className="fw-bold">
                                    Processing
                                </h6>

                                <p className="text-muted small mb-0">
                                    Prepare the product
                                    and mark it Ready when
                                    completed.
                                </p>

                            </div>

                        </div>


                        <div className="col-md-4 mb-3">

                            <div className="border rounded p-3 h-100">

                                <span className="badge bg-info text-dark mb-2">
                                    3
                                </span>

                                <h6 className="fw-bold">
                                    Ready
                                </h6>

                                <p className="text-muted small mb-0">
                                    No further supplier
                                    action is required.
                                    Delivery is handled by
                                    Admin and Rider.
                                </p>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};


export default SupplierOrderDetails;