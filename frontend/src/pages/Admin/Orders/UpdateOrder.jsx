import {
    useEffect,
    useState,
} from "react";

import {
    useNavigate,
    useParams,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getAdminOrder,
    updateAdminOrderStatus,
} from "../../../services/orderService";


// =========================================================
// AVAILABLE ADMIN STATUSES
// =========================================================
// Admin directly controls only:
//
// Pending -> Accepted
// Pending -> Cancelled
//
// Processing is controlled by Supplier.
// Ready is controlled by Supplier.
// Assigned is controlled by Admin Rider Assignment.
// Out for Delivery is controlled by Rider.
// Delivered is controlled by Rider.
// =========================================================

const getAvailableStatuses = (currentStatus) => {
    switch (currentStatus) {

        case "Pending":
            return [
                {
                    value: "Accepted",
                    label: "Accept Order",
                },
                {
                    value: "Cancelled",
                    label: "Cancel Order",
                },
            ];

        default:
            return [];
    }
};


// =========================================================
// UPDATE ORDER
// =========================================================

const UpdateOrder = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [order, setOrder] = useState(null);
    const [status, setStatus] = useState("");


    // =========================================================
    // FETCH ORDER
    // =========================================================

    useEffect(() => {
        let cancelled = false;

        const fetchOrder = async () => {
            try {
                setLoading(true);

                const response =
                    await getAdminOrder(id);

                if (cancelled) {
                    return;
                }

                const orderData =
                    response.data;

                setOrder(orderData);

                const available =
                    getAvailableStatuses(
                        orderData.status
                    );

                setStatus(
                    available.length > 0
                        ? available[0].value
                        : ""
                );

            } catch (error) {
                if (cancelled) {
                    return;
                }

                console.error(
                    "Failed to load order:",
                    error
                );

                toast.error(
                    error?.response?.data?.detail ||
                    error?.response?.data?.message ||
                    "Failed to load order."
                );

                navigate(
                    "/admin/orders"
                );

            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        void fetchOrder();

        return () => {
            cancelled = true;
        };
    }, [
        id,
        navigate,
    ]);


    // =========================================================
    // STATUS BADGE
    // =========================================================

    const getStatusBadge = (currentStatus) => {
        switch (currentStatus) {

            case "Pending":
                return "badge bg-warning text-dark";

            case "Accepted":
                return "badge bg-primary";

            case "Processing":
                return "badge bg-info text-dark";

            case "Ready":
                return "badge bg-success";

            case "Assigned":
                return "badge bg-secondary";

            case "Out for Delivery":
                return "badge bg-dark";

            case "Delivered":
                return "badge bg-success";

            case "Cancelled":
                return "badge bg-danger";

            default:
                return "badge bg-light text-dark";
        }
    };


    // =========================================================
    // CUSTOMER NAME
    // =========================================================

    const getCustomerName = () => {
        if (!order) {
            return "N/A";
        }

        return (
            order.customer_name ||
            order.customer_email ||
            "N/A"
        );
    };


    // =========================================================
    // FORMAT DATE
    // =========================================================

    const formatDate = (date) => {
        if (!date) {
            return "N/A";
        }

        const parsedDate =
            new Date(date);

        if (
            Number.isNaN(
                parsedDate.getTime()
            )
        ) {
            return "N/A";
        }

        return parsedDate.toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );
    };


    // =========================================================
    // FORMAT AMOUNT
    // =========================================================

    const formatAmount = (amount) => {
        const value =
            Number(amount);

        if (
            Number.isNaN(value)
        ) {
            return "0.00";
        }

        return value.toFixed(2);
    };


    // =========================================================
    // SUBMIT STATUS
    // =========================================================

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!status) {
            toast.warning(
                "There is no admin status action available for this order."
            );

            return;
        }

        try {
            setSaving(true);

            await updateAdminOrderStatus(
                id,
                {
                    status,
                }
            );

            toast.success(
                status === "Accepted"
                    ? "Order accepted successfully."
                    : "Order cancelled successfully."
            );

            navigate(
                "/admin/orders"
            );

        } catch (error) {
            console.error(
                "Update order error:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                "Failed to update order."
            );

        } finally {
            setSaving(false);
        }
    };


    // =========================================================
    // LOADING
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

                    <h5 className="mt-3">
                        Loading Order...
                    </h5>

                </div>

            </DashboardLayout>
        );
    }


    // =========================================================
    // ORDER NOT FOUND
    // =========================================================

    if (!order) {
        return (
            <DashboardLayout>

                <div className="container py-5">

                    <div className="alert alert-danger">
                        Order not found.
                    </div>

                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() =>
                            navigate(
                                "/admin/orders"
                            )
                        }
                    >
                        Back to Orders
                    </button>

                </div>

            </DashboardLayout>
        );
    }


    const availableStatuses =
        getAvailableStatuses(
            order.status
        );


    // =========================================================
    // PAGE
    // =========================================================

    return (
        <DashboardLayout>

            <div className="container py-4">

                <div className="row justify-content-center">

                    <div className="col-lg-8">

                        {/* =================================================
                            ORDER INFORMATION
                        ================================================= */}

                        <div className="card shadow mb-4">

                            <div className="card-header bg-primary text-white">

                                <h3 className="mb-0">
                                    Update Order
                                </h3>

                            </div>

                            <div className="card-body">

                                <div className="row">

                                    <div className="col-md-6 mb-3">

                                        <label className="form-label fw-bold">
                                            Order Number
                                        </label>

                                        <div className="form-control bg-light">
                                            ORD-
                                            {String(
                                                order.id
                                            ).padStart(
                                                4,
                                                "0"
                                            )}
                                        </div>

                                    </div>


                                    <div className="col-md-6 mb-3">

                                        <label className="form-label fw-bold">
                                            Customer
                                        </label>

                                        <div className="form-control bg-light">
                                            {
                                                getCustomerName()
                                            }
                                        </div>

                                    </div>


                                    <div className="col-md-6 mb-3">

                                        <label className="form-label fw-bold">
                                            Order Date
                                        </label>

                                        <div className="form-control bg-light">
                                            {
                                                formatDate(
                                                    order.created_at
                                                )
                                            }
                                        </div>

                                    </div>


                                    <div className="col-md-6 mb-3">

                                        <label className="form-label fw-bold">
                                            Total Amount
                                        </label>

                                        <div className="form-control bg-light">
                                            ৳{" "}
                                            {
                                                formatAmount(
                                                    order.total_amount
                                                )
                                            }
                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>


                        {/* =================================================
                            STATUS UPDATE
                        ================================================= */}

                        <div className="card shadow">

                            <div className="card-header bg-warning">

                                <h4 className="mb-0">
                                    Order Status
                                </h4>

                            </div>

                            <div className="card-body">

                                <form
                                    onSubmit={
                                        handleSubmit
                                    }
                                >

                                    {/* CURRENT STATUS */}

                                    <div className="mb-4">

                                        <label className="form-label fw-bold">
                                            Current Status
                                        </label>

                                        <div>
                                            <span
                                                className={getStatusBadge(
                                                    order.status
                                                )}
                                            >
                                                {
                                                    order.status
                                                }
                                            </span>
                                        </div>

                                    </div>


                                    {/* =================================================
                                        ADMIN WORKFLOW INFORMATION
                                    ================================================= */}

                                    {order.status === "Pending" && (
                                        <div className="alert alert-warning">

                                            <strong>
                                                Admin action available
                                            </strong>

                                            <div className="small mt-2">
                                                You can accept or cancel this
                                                pending order.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Accepted" && (
                                        <div className="alert alert-info">

                                            <strong>
                                                Waiting for supplier
                                            </strong>

                                            <div className="small mt-2">
                                                The supplier will process the
                                                order items. The order will
                                                automatically move to Processing
                                                when supplier processing begins.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Processing" && (
                                        <div className="alert alert-info">

                                            <strong>
                                                Supplier is processing the order
                                            </strong>

                                            <div className="small mt-2">
                                                The supplier controls the item
                                                status. When all supplier items
                                                are Ready, the order will
                                                automatically become Ready.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Ready" && (
                                        <div className="alert alert-success">

                                            <strong>
                                                Order is Ready
                                            </strong>

                                            <div className="small mt-2">
                                                Rider assignment is handled from
                                                the Admin Orders page. Select a
                                                specific active rider and assign
                                                the delivery there.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Assigned" && (
                                        <div className="alert alert-secondary">

                                            <strong>
                                                Rider Assigned
                                            </strong>

                                            <div className="small mt-2">
                                                The selected rider must now
                                                accept and operate the delivery.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Out for Delivery" && (
                                        <div className="alert alert-dark">

                                            <strong>
                                                Out for Delivery
                                            </strong>

                                            <div className="small mt-2">
                                                The delivery rider is currently
                                                handling this order.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Delivered" && (
                                        <div className="alert alert-success">

                                            <strong>
                                                Order Delivered
                                            </strong>

                                            <div className="small mt-2">
                                                This order has completed the
                                                delivery workflow.
                                            </div>

                                        </div>
                                    )}


                                    {order.status === "Cancelled" && (
                                        <div className="alert alert-danger">

                                            <strong>
                                                Order Cancelled
                                            </strong>

                                            <div className="small mt-2">
                                                This order can no longer be
                                                modified.
                                            </div>

                                        </div>
                                    )}


                                    {/* =================================================
                                        STATUS SELECT
                                    ================================================= */}

                                    {availableStatuses.length > 0 && (
                                        <div className="mb-4">

                                            <label
                                                htmlFor="status"
                                                className="form-label fw-bold"
                                            >
                                                Admin Action
                                            </label>

                                            <select
                                                id="status"
                                                name="status"
                                                className="form-select"
                                                value={status}
                                                onChange={(
                                                    event
                                                ) =>
                                                    setStatus(
                                                        event.target.value
                                                    )
                                                }
                                                disabled={
                                                    saving
                                                }
                                            >

                                                <option value="">
                                                    Select Action
                                                </option>

                                                {availableStatuses.map(
                                                    (item) => (
                                                        <option
                                                            key={
                                                                item.value
                                                            }
                                                            value={
                                                                item.value
                                                            }
                                                        >
                                                            {
                                                                item.label
                                                            }
                                                        </option>
                                                    )
                                                )}

                                            </select>

                                        </div>
                                    )}


                                    {/* =================================================
                                        BUTTONS
                                    ================================================= */}

                                    <div className="d-flex gap-2">

                                        {availableStatuses.length > 0 && (
                                            <button
                                                type="submit"
                                                className="btn btn-primary"
                                                disabled={
                                                    saving ||
                                                    !status
                                                }
                                            >

                                                {saving ? (
                                                    <>
                                                        <span
                                                            className="spinner-border spinner-border-sm me-2"
                                                            role="status"
                                                            aria-hidden="true"
                                                        />

                                                        Saving...
                                                    </>
                                                ) : (
                                                    "Save Changes"
                                                )}

                                            </button>
                                        )}


                                        <button
                                            type="button"
                                            className="btn btn-secondary"
                                            disabled={
                                                saving
                                            }
                                            onClick={() =>
                                                navigate(
                                                    "/admin/orders"
                                                )
                                            }
                                        >
                                            Back to Orders
                                        </button>

                                    </div>

                                </form>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
};


export default UpdateOrder;