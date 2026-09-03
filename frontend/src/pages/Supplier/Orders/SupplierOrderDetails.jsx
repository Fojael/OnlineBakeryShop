import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import { getSupplierOrder, updateSupplierOrderItemStatus } from "../../../services/orderService";

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
        default:
            return "bg-secondary";
    }
};

const formatCurrency = (value) => {
    const numeric = Number(value || 0);
    return `৳${numeric.toFixed(2)}`;
};

const formatDate = (value) => {
    if (!value) return "N/A";

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

const SupplierOrderDetails = () => {
    const { id } = useParams();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updatingItemId, setUpdatingItemId] = useState(null);

    useEffect(() => {
        let isMounted = true;

        const fetchOrder = async () => {
            try {
                setLoading(true);
                const response = await getSupplierOrder(id);

                if (isMounted) {
                    setOrder(response?.data || response || null);
                }
            } catch (error) {
                console.error("Failed to load supplier order details:", error);

                if (isMounted) {
                    toast.error(error?.response?.data?.detail || "Failed to load order details.");
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

    const itemTotal = useMemo(() => {
        if (!order?.items) return 0;

        return order.items.reduce((sum, item) => sum + Number(item.subtotal || 0), 0);
    }, [order]);

    const handleStatusChange = async (itemId, nextStatus) => {
        try {
            setUpdatingItemId(itemId);
            await updateSupplierOrderItemStatus(itemId, nextStatus);

            setOrder((previous) => {
                if (!previous) return previous;

                return {
                    ...previous,
                    items: previous.items.map((item) =>
                        item.id === itemId
                            ? { ...item, supplier_status: nextStatus }
                            : item
                    ),
                };
            });

            toast.success("Delivery status updated.");
        } catch (error) {
            console.error("Failed to update order item status:", error);
            toast.error(error?.response?.data?.detail || "Failed to update delivery status.");
        } finally {
            setUpdatingItemId(null);
        }
    };

    if (loading) {
        return (
            <div className="container py-4">
                <div className="text-center py-5">
                    <div className="spinner-border" role="status" />
                    <p className="mt-3 mb-0">Loading order details...</p>
                </div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="container py-4">
                <div className="alert alert-danger">Order not found or access is restricted.</div>
                <Link to="/supplier/orders" className="btn btn-primary">Back to Orders</Link>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
                <div>
                    <h2 className="fw-bold mb-1">Order Details</h2>
                    <p className="text-muted mb-0">Order #{order.id}</p>
                </div>
                <Link to="/supplier/orders" className="btn btn-outline-secondary">
                    Back to Orders
                </Link>
            </div>

            <div className="row g-4 mb-4">
                <div className="col-lg-6">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <h5 className="fw-bold mb-3">Customer Information</h5>
                            <p className="mb-2"><strong>Name:</strong> {order.customer_name || "Unknown"}</p>
                            <p className="mb-2"><strong>Email:</strong> {order.customer_email || "N/A"}</p>
                            <p className="mb-2"><strong>Address:</strong> {order.shipping_address || "N/A"}</p>
                            <p className="mb-0"><strong>Order Date:</strong> {formatDate(order.created_at)}</p>
                        </div>
                    </div>
                </div>

                <div className="col-lg-6">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <h5 className="fw-bold mb-3">Order Summary</h5>
                            <p className="mb-2"><strong>Order Status:</strong> <span className={`badge ${getStatusBadgeClass(order.status)}`}>{order.status || "Pending"}</span></p>
                            <p className="mb-2"><strong>Payment Status:</strong> <span className="badge bg-secondary">{order.payment_status || "Pending"}</span></p>
                            <p className="mb-2"><strong>Payment Method:</strong> {order.payment_method || "N/A"}</p>
                            <p className="mb-0"><strong>Total:</strong> {formatCurrency(itemTotal)}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card shadow-sm border-0">
                <div className="card-body">
                    <h5 className="fw-bold mb-3">Ordered Products</h5>

                    <div className="table-responsive">
                        <table className="table align-middle">
                            <thead className="table-light">
                                <tr>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Subtotal</th>
                                    <th>Delivery Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Array.isArray(order.items) && order.items.length > 0 ? (
                                    order.items.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.product_name || "Product"}</td>
                                            <td>{item.quantity || 0}</td>
                                            <td>{formatCurrency(item.price)}</td>
                                            <td>{formatCurrency(item.subtotal)}</td>
                                            <td>
                                                <select
                                                    className="form-select form-select-sm"
                                                    value={item.supplier_status || "Pending"}
                                                    onChange={(event) => handleStatusChange(item.id, event.target.value)}
                                                    disabled={updatingItemId === item.id}
                                                >
                                                    <option value="Pending">Pending</option>
                                                    <option value="Processing">Processing</option>
                                                    <option value="Ready">Ready</option>
                                                </select>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="5" className="text-center text-muted py-4">
                                            No products in this order.
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

export default SupplierOrderDetails;

