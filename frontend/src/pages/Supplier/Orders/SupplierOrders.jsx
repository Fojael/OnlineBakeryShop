import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import { getSupplierOrders } from "../../../services/orderService";

const getOrderStatusBadge = (status) => {
    switch (status) {
        case "Pending":
            return "bg-warning text-dark";
        case "Processing":
            return "bg-primary";
        case "Shipped":
        case "Ready":
            return "bg-info text-dark";
        case "Completed":
        case "Delivered":
            return "bg-success";
        case "Cancelled":
            return "bg-danger";
        default:
            return "bg-secondary";
    }
};

const getPaymentStatusBadge = (status) => {
    switch (status) {
        case "Paid":
        case "Completed":
            return "bg-success";
        case "Pending":
            return "bg-warning text-dark";
        case "Failed":
        case "Cancelled":
            return "bg-danger";
        default:
            return "bg-secondary";
    }
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
    });
};

const SupplierOrders = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        const loadOrders = async () => {
            try {
                setLoading(true);
                const response = await getSupplierOrders();
                const data = Array.isArray(response?.data) ? response.data : response?.data?.results || [];
                setOrders(data);
            } catch (error) {
                console.error("Failed to load supplier orders:", error);
                toast.error(error?.response?.data?.detail || "Failed to load orders.");
                setOrders([]);
            } finally {
                setLoading(false);
            }
        };

        void loadOrders();
    }, []);

    const filteredOrders = useMemo(() => {
        const keyword = search.trim().toLowerCase();

        if (!keyword) {
            return orders;
        }

        return orders.filter((order) => {
            const orderNumber = `ORD${String(order.id).padStart(3, "0")}`;
            const customerName = String(order.customer_name || "").toLowerCase();
            const status = String(order.status || "").toLowerCase();
            const paymentStatus = String(order.payment_status || "").toLowerCase();

            return (
                orderNumber.toLowerCase().includes(keyword) ||
                customerName.includes(keyword) ||
                status.includes(keyword) ||
                paymentStatus.includes(keyword)
            );
        });
    }, [orders, search]);

    if (loading) {
        return (
            <div className="container py-4">
                <div className="text-center py-5">
                    <div className="spinner-border" role="status" />
                    <p className="mt-3 mb-0">Loading supplier orders...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
                <div>
                    <h2 className="fw-bold mb-1">Supplier Orders</h2>
                    <p className="text-muted mb-0">Orders containing your products only.</p>
                </div>
            </div>

            <div className="row mb-4">
                <div className="col-md-4">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search order or customer"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />
                </div>
            </div>

            <div className="card shadow-sm border-0">
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>Order Number</th>
                                    <th>Customer</th>
                                    <th>Order Date</th>
                                    <th>Total Items</th>
                                    <th>Order Status</th>
                                    <th>Payment Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredOrders.length === 0 ? (
                                    <tr>
                                        <td colSpan="7" className="text-center text-muted py-4">
                                            No orders for your products yet.
                                        </td>
                                    </tr>
                                ) : (
                                    filteredOrders.map((order) => {
                                        const totalItems = Array.isArray(order.items) ? order.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0) : 0;

                                        return (
                                            <tr key={order.id}>
                                                <td>ORD{String(order.id).padStart(3, "0")}</td>
                                                <td>{order.customer_name || "Unknown Customer"}</td>
                                                <td>{formatDate(order.created_at)}</td>
                                                <td>{totalItems}</td>
                                                <td>
                                                    <span className={`badge ${getOrderStatusBadge(order.status)}`}>
                                                        {order.status || "Pending"}
                                                    </span>
                                                </td>
                                                <td>
                                                    <span className={`badge ${getPaymentStatusBadge(order.payment_status)}`}>
                                                        {order.payment_status || "Pending"}
                                                    </span>
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        className="btn btn-sm btn-outline-primary"
                                                        onClick={() => navigate(`/supplier/orders/${order.id}`)}
                                                    >
                                                        View Order
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SupplierOrders;

