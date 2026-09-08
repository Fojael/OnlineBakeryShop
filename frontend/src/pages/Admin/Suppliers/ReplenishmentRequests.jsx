import { useEffect, useState } from "react";
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

const ReplenishmentRequests = () => {
    const [requests, setRequests] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [form, setForm] = useState({
        supplier: "",
        product: "",
        requested_quantity: "",
        notes: "",
    });

    const loadData = async () => {
        try {
            setLoading(true);
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
            toast.error(
                error?.response?.data?.detail ||
                "Failed to load replenishment data.",
            );
        } finally {
            setLoading(false);
        }
    };

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

                <div className="card shadow-sm">
                    <div className="card-header fw-bold">Replenishment Requests</div>
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>Product</th>
                                    <th>Supplier</th>
                                    <th>Quantity</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {!loading && requests.length === 0 && (
                                    <tr>
                                        <td colSpan="5" className="text-center py-4">
                                            No replenishment requests found.
                                        </td>
                                    </tr>
                                )}
                                {requests.map((request) => (
                                    <tr key={request.id}>
                                        <td>{request.product_name}</td>
                                        <td>{request.supplier_name}</td>
                                        <td>{request.requested_quantity}</td>
                                        <td>
                                            <span className="badge bg-secondary">
                                                {request.status}
                                            </span>
                                        </td>
                                        <td>
                                            {request.created_at
                                                ? new Date(request.created_at).toLocaleDateString()
                                                : "-"}
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
