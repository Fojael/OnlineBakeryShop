
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getAdminOrder,
    updateAdminOrderStatus,
} from "../../../services/orderService";

const UpdateOrder = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [order, setOrder] = useState(null);
    const [status, setStatus] = useState("");

    // =========================================================
    // Fetch Order
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

        case "Ready":
            return [
                {
                    value: "Assigned",
                    label: "Assign Rider",
                },
            ];

        default:
            return [];
    }
};


    useEffect(() => {
        let cancelled = false;

        const fetchOrder = async () => {
            try {
                setLoading(true);

               const response = await getAdminOrder(id);

                if (cancelled) {
                    return;
                }

                const orderData = response.data;

                setOrder(orderData);

const available =
    getAvailableStatuses(orderData.status);

setStatus(
    available.length
        ? available[0].value
        : ""
);
            } catch (error) {
                if (cancelled) {
                    return;
                }

                console.error(error);

                toast.error("Failed to load order.");

                navigate("/admin/orders");
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
    }, [id, navigate]);

    // =========================================================
    // Status Badge
    // =========================================================

    const getStatusBadge = (status) => {

    switch (status) {

        case "Pending":
            return "badge bg-warning text-dark";

        case "Accepted":
            return "badge bg-primary";

        case "Processing":
            return "badge bg-info";

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
    // Customer Name
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

        return parsedDate.toLocaleDateString("en-GB");
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
    // Submit Status
    // =========================================================

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!status) {
            toast.warning("Please select an order status.");
            return;
        }

        try {
            setSaving(true);

            await updateAdminOrderStatus(id, {
                status,
            });

            toast.success("Order updated successfully.");

            navigate("/admin/orders");
        } catch (error) {
            console.error(error);

            toast.error("Failed to update order.");
        } finally {
            setSaving(false);
        }
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

                    <h5 className="mt-3">
                        Loading Order...
                    </h5>
                </div>
            </DashboardLayout>
        );
    }

    // =========================================================
    // Order Not Found
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
                        onClick={() => navigate("/admin/orders")}
                    >
                        Back to Orders
                    </button>
                </div>
            </DashboardLayout>
        );
    }

    // =========================================================
    // Page
    // =========================================================

    return (
        <DashboardLayout>
            <div className="container py-4">

                <div className="row justify-content-center">
                    <div className="col-lg-8">

                        {/* Order Information */}

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
                                            ORD
                                            {String(order.id).padStart(
                                                3,
                                                "0"
                                            )}
                                        </div>
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">
                                            Customer
                                        </label>

                                        <div className="form-control bg-light">
                                            {getCustomerName()}
                                        </div>
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">
                                            Order Date
                                        </label>

                                        <div className="form-control bg-light">
                                            {formatDate(
                                                order.created_at
                                            )}
                                        </div>
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">
                                            Total Amount
                                        </label>

                                        <div className="form-control bg-light">
                                            ৳
                                            {formatAmount(
                                                order.total_amount
                                            )}
                                        </div>
                                    </div>

                                </div>

                            </div>
                        </div>

                        {/* Status Update */}

                        <div className="card shadow">

                            <div className="card-header bg-warning">
                                <h4 className="mb-0">
                                    Order Status
                                </h4>
                            </div>

                            <div className="card-body">

                                <form onSubmit={handleSubmit}>

                                    {/* Current Status */}

                                    <div className="mb-3">
                                        <label className="form-label fw-bold">
                                            Current Status
                                        </label>

                                        <div>
                                            <span className={getStatusBadge(order.status)}>
                                                {order.status}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Status */}

                                    <div className="mb-4">
                                        <label
                                            htmlFor="status"
                                            className="form-label fw-bold"
                                        >
                                            Status *
                                        </label>

                                        <select
                                            id="status"
                                            name="status"
                                            className="form-select"
                                            value={status}
                                            onChange={(event) =>
                                                setStatus(
                                                    event.target.value
                                                )
                                            }
                                            disabled={
                                                saving ||
                                                !status
                                            }
                                        >
                                           {getAvailableStatuses(order.status).length > 0 ? (

                                                getAvailableStatuses(order.status).map((item) => (

                                                    <option
                                                        key={item.value}
                                                        value={item.value}
                                                    >
                                                        {item.label}
                                                    </option>

                                                ))

                                            ) : (

                                                    <option value="">
                                                        No admin action available
                                                    </option>

                                            )} 
                                        </select>
                                    </div>

                                    {/* Buttons */}

                                    <div className="d-flex gap-2">

                                        <button
                                            type="submit"
                                            className="btn btn-primary"
                                            disabled={saving}
                                        >
                                            {saving ? (
                                                <>
                                                    <span
                                                        className="spinner-border spinner-border-sm me-2"
                                                        role="status"
                                                    />

                                                    Saving...
                                                </>
                                            ) : (
                                                "Save Changes"
                                            )}
                                        </button>

                                        <button
                                            type="button"
                                            className="btn btn-secondary"
                                            disabled={saving}
                                            onClick={() =>
                                                navigate(
                                                    "/admin/orders"
                                                )
                                            }
                                        >
                                            Cancel
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

