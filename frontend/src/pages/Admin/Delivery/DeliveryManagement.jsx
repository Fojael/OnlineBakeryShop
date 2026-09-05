import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import {
    assignDeliveryRider,
    getAdminOrders,
    getDeliveryRiders,
} from "../../../services/orderService";

const DELIVERY_TABS = [
    "Ready",
    "Assigned",
    "Accepted",
    "Picked Up",
    "Out for Delivery",
    "Delivered",
    "Cancelled",
];

const deliveryStatus = (order) => {
    if (order.status === "Ready" || order.status === "Cancelled") {
        return order.status;
    }
    if (order.status === "Delivered") {
        return "Delivered";
    }
    return {
        ASSIGNED: "Assigned",
        ACCEPTED: "Accepted",
        PICKED_UP: "Picked Up",
        OUT_FOR_DELIVERY: "Out for Delivery",
    }[order.delivery_status] || order.status;
};

const DeliveryManagement = () => {
    const [orders, setOrders] = useState([]);
    const [riders, setRiders] = useState([]);
    const [tab, setTab] = useState("Ready");
    const [selectedRiders, setSelectedRiders] = useState({});
    const [loading, setLoading] = useState(true);
    const [assigning, setAssigning] = useState(null);

    const load = async () => {
        const [ordersResponse, ridersResponse] = await Promise.all([
            getAdminOrders(),
            getDeliveryRiders(),
        ]);
        setOrders(ordersResponse.data?.results || ordersResponse.data || []);
        setRiders(ridersResponse.data?.results || ridersResponse.data || []);
        setLoading(false);
    };

    useEffect(() => {
        load().catch(() => setLoading(false));
    }, []);

    const activeRiders = useMemo(
        () => riders.filter((rider) => rider.is_active),
        [riders]
    );

    const visibleOrders = orders.filter(
        (order) => deliveryStatus(order) === tab
    );

    const assign = async (orderId) => {
        const riderId = selectedRiders[orderId];
        if (!riderId) {
            toast.warning("Select an active rider first.");
            return;
        }

        setAssigning(orderId);
        try {
            await assignDeliveryRider(orderId, riderId);
            toast.success("Delivery assigned successfully.");
            await load();
        } catch (error) {
            toast.error(
                error.response?.data?.detail ||
                "Failed to assign delivery."
            );
        } finally {
            setAssigning(null);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Delivery Management</h2>
                <p className="text-muted mb-4">
                    Assign active riders to ready orders and monitor delivery progress.
                </p>

                <div className="d-flex flex-wrap gap-2 mb-4">
                    {DELIVERY_TABS.map((status) => (
                        <button
                            key={status}
                            type="button"
                            className={`btn ${tab === status ? "btn-primary" : "btn-outline-primary"}`}
                            onClick={() => setTab(status)}
                        >
                            {status}
                        </button>
                    ))}
                </div>

                <div className="card border-0 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Order</th>
                                    <th>Customer</th>
                                    <th>Status</th>
                                    <th>Rider</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="5">Loading deliveries...</td></tr>
                                ) : visibleOrders.length === 0 ? (
                                    <tr><td colSpan="5">No orders in this delivery state.</td></tr>
                                ) : visibleOrders.map((order) => (
                                    <tr key={order.id}>
                                        <td>#{order.id}</td>
                                        <td>{order.customer_name || order.customer_email || "-"}</td>
                                        <td>{deliveryStatus(order)}</td>
                                        <td>{order.rider_name || "-"}</td>
                                        <td>
                                            {tab === "Ready" ? (
                                                <div className="d-flex gap-2">
                                                    <select
                                                        className="form-select form-select-sm"
                                                        value={selectedRiders[order.id] || ""}
                                                        onChange={(event) => setSelectedRiders({ ...selectedRiders, [order.id]: event.target.value })}
                                                    >
                                                        <option value="">Select active rider</option>
                                                        {activeRiders.map((rider) => <option key={rider.id} value={rider.id}>{rider.first_name || rider.username} {rider.last_name || ""}</option>)}
                                                    </select>
                                                    <button className="btn btn-primary btn-sm" disabled={assigning === order.id} onClick={() => assign(order.id)}>
                                                        {assigning === order.id ? "Assigning..." : "Assign"}
                                                    </button>
                                                </div>
                                            ) : (
                                                <span className="text-muted">Workflow controlled</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default DeliveryManagement;
