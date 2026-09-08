import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import {
    getCustomerItems,
    getCustomer,
    getCustomers,
    updateCustomerStatus,
} from "../../../services/customerService";

const Customers = () => {
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);

    useEffect(() => {
        let ignore = false;

        const loadCustomers = async () => {
            try {
                const response = await getCustomers({
                    search,
                    ...(status ? { is_active: status } : {}),
                });
                if (!ignore) {
                    setCustomers(getCustomerItems(response));
                }
            } catch (error) {
                console.error(error);
                if (!ignore) {
                    toast.error("Failed to load customers.");
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadCustomers();

        return () => {
            ignore = true;
        };
    }, [search, status]);

    const filteredCustomers = useMemo(() => customers, [customers]);

    const showCustomerDetails = async (customer) => {
        try {
            const response = await getCustomer(customer.id);
            setSelectedCustomer(response.data);
        } catch {
            toast.error("Failed to load customer details.");
        }
    };

    const toggleStatus = async (customer) => {
        setUpdatingId(customer.id);
        try {
            const response = await updateCustomerStatus(
                customer.id,
                !customer.is_active
            );
            const updatedCustomer = response.data;
            setCustomers((current) =>
                current.map((item) =>
                    item.id === customer.id
                        ? { ...item, ...updatedCustomer }
                        : item
                )
            );
            if (selectedCustomer?.id === customer.id) {
                setSelectedCustomer((current) => ({ ...current, ...updatedCustomer }));
            }
            toast.success(
                updatedCustomer.is_active
                    ? "Customer enabled."
                    : "Customer disabled."
            );
        } catch {
            toast.error("Failed to update customer status.");
        } finally {
            setUpdatingId(null);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2 className="fw-bold mb-1">Customer Management</h2>
                        <p className="text-muted mb-0">
                            {filteredCustomers.length} customer{filteredCustomers.length === 1 ? "" : "s"}
                        </p>
                    </div>
                    <button className="btn btn-outline-primary" type="button" onClick={() => window.location.reload()}>
                        Refresh
                    </button>
                </div>

                <div className="row g-2 mb-4">
                    <div className="col-md-8">
                        <input
                            className="form-control"
                            placeholder="Search by name, email, or phone"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                        />
                    </div>
                    <div className="col-md-4">
                        <select className="form-select" value={status} onChange={(event) => setStatus(event.target.value)}>
                            <option value="">All statuses</option>
                            <option value="true">Active</option>
                            <option value="false">Inactive</option>
                        </select>
                    </div>
                </div>

                {selectedCustomer && (
                    <div className="card border-info mb-4">
                        <div className="card-body">
                            <div className="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 className="card-title mb-1">{selectedCustomer.name}</h5>
                                    <p className="text-muted mb-3">{selectedCustomer.email} · {selectedCustomer.phone || "No phone"}</p>
                                </div>
                                <button className="btn-close" type="button" aria-label="Close customer details" onClick={() => setSelectedCustomer(null)} />
                            </div>
                            <div className="row g-3 mb-3">
                                <div className="col-sm-4"><strong>{selectedCustomer.total_orders}</strong><div className="text-muted small">Total orders</div></div>
                                <div className="col-sm-4"><strong>{selectedCustomer.total_spent}</strong><div className="text-muted small">Total spending</div></div>
                                <div className="col-sm-4"><strong>{new Date(selectedCustomer.created_at).toLocaleDateString()}</strong><div className="text-muted small">Registered</div></div>
                            </div>
                            <h6>Purchase history</h6>
                            {selectedCustomer.orders?.length ? (
                                <div className="table-responsive">
                                    <table className="table table-sm mb-0">
                                        <thead><tr><th>Order</th><th>Status</th><th>Total</th><th>Date</th></tr></thead>
                                        <tbody>{selectedCustomer.orders.map((order) => (
                                            <tr key={order.id}><td>#{order.id}</td><td>{order.status}</td><td>{order.total_amount}</td><td>{new Date(order.created_at).toLocaleDateString()}</td></tr>
                                        ))}</tbody>
                                    </table>
                                </div>
                            ) : <p className="text-muted mb-0">No orders yet.</p>}
                        </div>
                    </div>
                )}

                <div className="card shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-dark">
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="6" className="text-center py-4">Loading customers...</td></tr>
                                ) : filteredCustomers.length === 0 ? (
                                    <tr><td colSpan="6" className="text-center py-4 text-muted">No customers found.</td></tr>
                                ) : filteredCustomers.map((customer) => (
                                    <tr key={customer.id}>
                                        <td>{customer.id}</td>
                                        <td>{customer.name}</td>
                                        <td>{customer.email}</td>
                                        <td>{customer.phone || "-"}</td>
                                        <td>
                                            <span className={`badge ${customer.is_active ? "bg-success" : "bg-secondary"}`}>
                                                {customer.is_active ? "Active" : "Inactive"}
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                className="btn btn-outline-primary btn-sm me-2"
                                                type="button"
                                                onClick={() => showCustomerDetails(customer)}
                                            >
                                                View
                                            </button>
                                            <button
                                                className={`btn btn-sm ${customer.is_active ? "btn-warning" : "btn-success"}`}
                                                type="button"
                                                disabled={updatingId === customer.id}
                                                onClick={() => toggleStatus(customer)}
                                            >
                                                {updatingId === customer.id ? "Saving..." : customer.is_active ? "Disable" : "Enable"}
                                            </button>
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

export default Customers;