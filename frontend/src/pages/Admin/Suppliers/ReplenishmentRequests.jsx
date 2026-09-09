import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getProducts } from "../../../services/productService";
import { getSuppliers } from "../../../services/supplierService";
import {
    createReplenishmentRequest,
    getReplenishmentRequests,
} from "../../../services/replenishmentService";

const normalizeList = (response) => {
    const data = response?.data ?? response;

    if (Array.isArray(data)) {
        return data;
    }

    return data?.results || data?.products || data?.suppliers || [];
};

const statusLabels = {
    PENDING: "Pending",
    PROCESSING: "Processing",
    READY: "Ready",
    DELIVERED: "Delivered",
};

const formatDate = (value) => (
    value ? new Date(value).toLocaleString() : "-"
);

const ReplenishmentRequests = () => {
    const [requests, setRequests] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [filters, setFilters] = useState({
        supplier: "",
        product: "",
        status: "",
    });
    const [form, setForm] = useState({
        supplier: "",
        product: "",
        requested_quantity: "",
        notes: "",
    });

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [requestsResponse, suppliersResponse, productsResponse] =
                await Promise.all([
                    getReplenishmentRequests(),
                    getSuppliers(),
                    getProducts(),
                ]);
            setRequests(normalizeList(requestsResponse));
            setSuppliers(normalizeList(suppliersResponse));
            setProducts(normalizeList(productsResponse));
        } catch (error) {
            setError(
                error?.response?.data?.detail ||
                "Failed to load replenishment data."
            );
            toast.error(
                error?.response?.data?.detail ||
                "Failed to load replenishment data.",
            );
        } finally {
            setLoading(false);
        }
    };

    const filteredRequests = useMemo(() => (
        requests.filter((request) => (
            (!filters.supplier || String(request.supplier) === filters.supplier)
            && (!filters.product || String(request.product) === filters.product)
            && (!filters.status || request.status === filters.status)
        ))
    ), [filters, requests]);

    useEffect(() => {
        const timer = setTimeout(() => {
            void loadData();
        }, 0);

        return () => clearTimeout(timer);
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm((previous) => ({ ...previous, [name]: value }));
    };

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        setFilters((previous) => ({ ...previous, [name]: value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            setSaving(true);
            await createReplenishmentRequest({
                ...form,
                requested_quantity: Number(form.requested_quantity),
            });
            toast.success("Replenishment request created.");
            setForm({
                supplier: "",
                product: "",
                requested_quantity: "",
                notes: "",
            });
            await loadData();
        } catch (error) {
            toast.error(
                error?.response?.data?.detail ||
                "Failed to create replenishment request.",
            );
        } finally {
            setSaving(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-3">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2 className="mb-1">Stock Replenishment</h2>
                        <p className="text-muted mb-0">
                            Request products from suppliers for bakery inventory.
                        </p>
                    </div>
                </div>

                {error && (
                    <div className="alert alert-danger" role="alert">
                        {error}
                    </div>
                )}

                <div className="card shadow-sm mb-4">
                    <div className="card-header fw-bold">Create Request</div>
                    <div className="card-body">
                        <form onSubmit={handleSubmit}>
                            <div className="row g-3">
                                <div className="col-md-4">
                                    <label className="form-label">Supplier</label>
                                    <select
                                        className="form-select"
                                        name="supplier"
                                        value={form.supplier}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select supplier</option>
                                        {suppliers.map((supplier) => (
                                            <option key={supplier.id} value={supplier.id}>
                                                {supplier.company || supplier.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Product</label>
                                    <select
                                        className="form-select"
                                        name="product"
                                        value={form.product}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select product</option>
                                        {products.map((product) => (
                                            <option key={product.id} value={product.id}>
                                                {product.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Requested quantity</label>
                                    <input
                                        className="form-control"
                                        type="number"
                                        min="1"
                                        name="requested_quantity"
                                        value={form.requested_quantity}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="col-12">
                                    <label className="form-label">Notes</label>
                                    <textarea
                                        className="form-control"
                                        rows="2"
                                        name="notes"
                                        value={form.notes}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-12">
                                    <button
                                        className="btn btn-primary"
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving ? "Creating..." : "Create Request"}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="card shadow-sm mb-4">
                    <div className="card-header fw-bold">Filter Requests</div>
                    <div className="card-body">
                        <div className="row g-3">
                            <div className="col-md-4">
                                <label className="form-label" htmlFor="supplier-filter">
                                    Supplier
                                </label>
                                <select
                                    id="supplier-filter"
                                    className="form-select"
                                    name="supplier"
                                    value={filters.supplier}
                                    onChange={handleFilterChange}
                                >
                                    <option value="">All suppliers</option>
                                    {suppliers.map((supplier) => (
                                        <option key={supplier.id} value={supplier.id}>
                                            {supplier.company || supplier.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label" htmlFor="product-filter">
                                    Product
                                </label>
                                <select
                                    id="product-filter"
                                    className="form-select"
                                    name="product"
                                    value={filters.product}
                                    onChange={handleFilterChange}
                                >
                                    <option value="">All products</option>
                                    {products.map((product) => (
                                        <option key={product.id} value={product.id}>
                                            {product.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label" htmlFor="status-filter">
                                    Status
                                </label>
                                <select
                                    id="status-filter"
                                    className="form-select"
                                    name="status"
                                    value={filters.status}
                                    onChange={handleFilterChange}
                                >
                                    <option value="">All statuses</option>
                                    {Object.entries(statusLabels).map(([value, label]) => (
                                        <option key={value} value={value}>
                                            {label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card shadow-sm">
                    <div className="card-header fw-bold d-flex justify-content-between">
                        <span>Supplier Replenishment Requests</span>
                        <span className="text-muted fw-normal">
                            {filteredRequests.length} shown
                        </span>
                    </div>
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>Request</th>
                                    <th>Product</th>
                                    <th>Supplier</th>
                                    <th>Quantity</th>
                                    <th>Request date</th>
                                    <th>Status</th>
                                    <th>Delivered date</th>
                                    <th>Inventory</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading && (
                                    <tr>
                                        <td colSpan="9" className="text-center py-4">
                                            Loading replenishment requests...
                                        </td>
                                    </tr>
                                )}
                                {!loading && filteredRequests.length === 0 && (
                                    <tr>
                                        <td colSpan="9" className="text-center py-4">
                                            {requests.length === 0
                                                ? "No replenishment requests found."
                                                : "No requests match the selected filters."
                                            }
                                        </td>
                                    </tr>
                                )}
                                {!loading && filteredRequests.map((request) => (
                                    <tr key={request.id}>
                                        <td>#{request.id}</td>
                                        <td>{request.product_name}</td>
                                        <td>{request.supplier_name}</td>
                                        <td>{request.requested_quantity} units</td>
                                        <td>{formatDate(request.created_at)}</td>
                                        <td>
                                            <span className="badge bg-secondary">
                                                {statusLabels[request.status] || request.status}
                                            </span>
                                        </td>
                                        <td>{formatDate(request.delivered_at)}</td>
                                        <td>
                                            {request.inventory_applied_at ? (
                                                <span className="text-success">
                                                    Applied {formatDate(request.inventory_applied_at)}
                                                </span>
                                            ) : (
                                                <span className="text-muted">Not applied</span>
                                            )}
                                        </td>
                                        <td>
                                            <details>
                                                <summary>View details</summary>
                                                <div className="small mt-2" style={{ minWidth: "14rem" }}>
                                                    <div><strong>Notes:</strong> {request.notes || "-"}</div>
                                                    <div><strong>Created by:</strong> {request.created_by_name || "-"}</div>
                                                    <div className="mt-2"><strong>History</strong></div>
                                                    {request.history?.length ? (
                                                        <ul className="mb-0 ps-3">
                                                            {request.history.map((entry) => (
                                                                <li key={entry.id}>
                                                                    {statusLabels[entry.new_status] || entry.new_status}
                                                                    {" - "}
                                                                    {formatDate(entry.changed_at)}
                                                                    {entry.changed_by_name
                                                                        ? ` by ${entry.changed_by_name}`
                                                                        : ""
                                                                    }
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    ) : (
                                                        <div className="text-muted">No status history yet.</div>
                                                    )}
                                                </div>
                                            </details>
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

export default ReplenishmentRequests;
