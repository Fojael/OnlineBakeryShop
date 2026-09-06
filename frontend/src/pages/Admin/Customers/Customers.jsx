import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import {
    getCustomerItems,
    getCustomers,
    updateCustomerStatus,
} from "../../../services/customerService";

const Customers = () => {
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState("");
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);

    useEffect(() => {
        let ignore = false;

        const loadCustomers = async () => {
            try {
                const response = await getCustomers();
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
    }, []);

    const filteredCustomers = useMemo(() => {
        const query = search.toLowerCase().trim();
        return customers.filter((customer) =>
            [customer.name, customer.email, customer.phone]
                .filter(Boolean)
                .some((value) => value.toLowerCase().includes(query))
        );
    }, [customers, search]);

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
                    item.id === customer.id ? updatedCustomer : item
                )
            );
            if (selectedCustomer?.id === customer.id) {
                setSelectedCustomer(updatedCustomer);
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
                    <button
                        className="btn btn-outline-primary"
                        type="button"
                        onClick={() => window.location.reload()}
                    >
                        Refresh
                    </button>
                </div>

                <input
                    className="form-control mb-4"
                    placeholder="Search by name, email, or phone"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                />

                {selectedCustomer && (
                    <div className="alert alert-info d-flex justify-content-between align-items-center">
                        <span>
                            <strong>{selectedCustomer.name}</strong> · {selectedCustomer.email}
                        </span>
                        <button
                            className="btn-close"
                            type="button"
                            aria-label="Close customer details"
                            onClick={() => setSelectedCustomer(null)}
                        />
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
                                                onClick={() => setSelectedCustomer(customer)}
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