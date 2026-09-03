import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import {
    createSupplierProduct,
    deleteSupplierProduct,
    getSupplierProducts,
    getSupplierProduct,
    updateSupplierProduct,
} from "../../../services/supplierService";

const API_BASE_URL = "http://127.0.0.1:8000";

const categories = [
    "Cake",
    "Bread",
    "Pastry",
    "Cookies",
    "Donut",
    "Cup Cake",
    "Muffin",
    "Brownie",
];

const initialFormState = {
    name: "",
    category: "Cake",
    description: "",
    price: "",
    stock_quantity: "",
    is_available: true,
};

const getProductImage = (product) => {
    if (!product?.image) return null;

    const image = String(product.image);

    if (image.startsWith("http://") || image.startsWith("https://")) {
        return image;
    }

    return `${API_BASE_URL}${image}`;
};

const SupplierProducts = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState(initialFormState);
    const [image, setImage] = useState(null);

    const fetchProducts = async () => {
        try {
            const response = await getSupplierProducts();
            const data = Array.isArray(response) ? response : response?.results || [];
            setProducts(data);
        } catch (error) {
            console.error("Failed to load supplier products:", error);
            toast.error(error?.response?.data?.detail || "Failed to load products.");
            setProducts([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let isMounted = true;

        const loadProducts = async () => {
            try {
                const response = await getSupplierProducts();
                const data = Array.isArray(response) ? response : response?.results || [];

                if (isMounted) {
                    setProducts(data);
                    setLoading(false);
                }
            } catch (error) {
                console.error("Failed to load supplier products:", error);

                if (isMounted) {
                    toast.error(error?.response?.data?.detail || "Failed to load products.");
                    setProducts([]);
                    setLoading(false);
                }
            }
        };

        void loadProducts();

        return () => {
            isMounted = false;
        };
    }, []);

    const handleInputChange = (event) => {
        const { name, value, type, checked } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const resetForm = () => {
        setFormData(initialFormState);
        setImage(null);
        setEditingId(null);
        setShowForm(false);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!formData.name.trim()) {
            toast.warning("Product name is required.");
            return;
        }

        if (!formData.category) {
            toast.warning("Please select a category.");
            return;
        }

        if (!formData.description.trim()) {
            toast.warning("Product description is required.");
            return;
        }

        const price = Number(formData.price);
        const stockQuantity = Number(formData.stock_quantity);

        if (!Number.isFinite(price) || price <= 0) {
            toast.warning("Please enter a valid product price.");
            return;
        }

        if (!Number.isFinite(stockQuantity) || stockQuantity < 0) {
            toast.warning("Please enter a valid stock quantity.");
            return;
        }

        try {
            setSaving(true);

            const payload = new FormData();
            payload.append("name", formData.name.trim());
            payload.append("category", formData.category);
            payload.append("description", formData.description.trim());
            payload.append("price", String(price));
            payload.append("stock_quantity", String(stockQuantity));
            payload.append("is_available", String(formData.is_available));

            if (image) {
                payload.append("image", image);
            }

            if (editingId) {
                await updateSupplierProduct(editingId, payload);
                toast.success("Product updated successfully.");
            } else {
                await createSupplierProduct(payload);
                toast.success("Product created successfully.");
            }

            resetForm();
            await fetchProducts();
        } catch (error) {
            console.error("Failed to save product:", error);
            const serverMessage =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                "Failed to save product.";
            toast.error(serverMessage);
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = async (productId) => {
        try {
            const product = await getSupplierProduct(productId);
            setEditingId(productId);
            setFormData({
                name: product.name || "",
                category: product.category || "Cake",
                description: product.description || "",
                price: product.price ?? "",
                stock_quantity: product.stock_quantity ?? "",
                is_available: Boolean(product.is_available),
            });
            setImage(null);
            setShowForm(true);
        } catch (error) {
            console.error("Failed to load product for edit:", error);
            toast.error("Failed to load product details.");
        }
    };

    const handleDelete = async (productId) => {
        if (!window.confirm("Are you sure you want to delete this product?")) {
            return;
        }

        try {
            await deleteSupplierProduct(productId);
            toast.success("Product deleted successfully.");
            await fetchProducts();
        } catch (error) {
            console.error("Failed to delete product:", error);
            toast.error(error?.response?.data?.detail || "Failed to delete product.");
        }
    };

    if (loading) {
        return (
            <div className="container py-4">
                <div className="text-center py-5">
                    <div className="spinner-border" role="status" />
                    <p className="mt-3 mb-0">Loading your products...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
                <div>
                    <h2 className="fw-bold mb-1">My Products</h2>
                    <p className="text-muted mb-0">Manage only your own product catalog.</p>
                </div>

                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => {
                        resetForm();
                        setShowForm(true);
                    }}
                >
                    + Add Product
                </button>
            </div>

            {showForm && (
                <div className="card shadow-sm border-0 mb-4">
                    <div className="card-body">
                        <h5 className="fw-bold mb-3">
                            {editingId ? "Edit Product" : "Add Product"}
                        </h5>

                        <form onSubmit={handleSubmit}>
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">Product Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        className="form-control"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                    />
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">Category</label>
                                    <select
                                        name="category"
                                        className="form-select"
                                        value={formData.category}
                                        onChange={handleInputChange}
                                    >
                                        {categories.map((category) => (
                                            <option key={category} value={category}>
                                                {category}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="mb-3">
                                <label className="form-label">Description</label>
                                <textarea
                                    name="description"
                                    rows="3"
                                    className="form-control"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <div className="row">
                                <div className="col-md-4 mb-3">
                                    <label className="form-label">Price</label>
                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        name="price"
                                        className="form-control"
                                        value={formData.price}
                                        onChange={handleInputChange}
                                    />
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">Stock Quantity</label>
                                    <input
                                        type="number"
                                        min="0"
                                        name="stock_quantity"
                                        className="form-control"
                                        value={formData.stock_quantity}
                                        onChange={handleInputChange}
                                    />
                                </div>

                                <div className="col-md-4 mb-3 d-flex align-items-end">
                                    <div className="form-check mt-3">
                                        <input
                                            type="checkbox"
                                            name="is_available"
                                            className="form-check-input"
                                            checked={formData.is_available}
                                            onChange={handleInputChange}
                                        />
                                        <label className="form-check-label">Available</label>
                                    </div>
                                </div>
                            </div>

                            <div className="mb-3">
                                <label className="form-label">Product Image</label>
                                <input
                                    type="file"
                                    className="form-control"
                                    accept="image/*"
                                    onChange={(event) => setImage(event.target.files?.[0] || null)}
                                />
                            </div>

                            <div className="d-flex gap-2">
                                <button type="submit" className="btn btn-primary" disabled={saving}>
                                    {saving ? "Saving..." : editingId ? "Update Product" : "Save Product"}
                                </button>
                                <button type="button" className="btn btn-outline-secondary" onClick={resetForm}>
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="card shadow-sm border-0">
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>Image</th>
                                    <th>Product Name</th>
                                    <th>Category</th>
                                    <th>Price</th>
                                    <th>Stock</th>
                                    <th>Availability</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {products.length === 0 ? (
                                    <tr>
                                        <td colSpan="8" className="text-center text-muted py-4">
                                            No products added yet.
                                        </td>
                                    </tr>
                                ) : (
                                    products.map((product) => (
                                        <tr key={product.id}>
                                            <td>
                                                {getProductImage(product) ? (
                                                    <img
                                                        src={getProductImage(product)}
                                                        alt={product.name}
                                                        style={{ width: 60, height: 60, objectFit: "cover", borderRadius: 8 }}
                                                    />
                                                ) : (
                                                    <div
                                                        className="bg-light border rounded d-flex align-items-center justify-content-center"
                                                        style={{ width: 60, height: 60 }}
                                                    >
                                                        No Img
                                                    </div>
                                                )}
                                            </td>
                                            <td>{product.name}</td>
                                            <td>{product.category}</td>
                                            <td>৳{Number(product.price || 0).toFixed(2)}</td>
                                            <td>{product.stock_quantity ?? 0}</td>
                                            <td>
                                                <span className={`badge ${product.is_available ? "bg-success" : "bg-secondary"}`}>
                                                    {product.is_available ? "Available" : "Unavailable"}
                                                </span>
                                            </td>
                                            <td>
                                                <span
                                                    className={`badge ${
                                                        product.stock_quantity === 0
                                                            ? "bg-danger"
                                                            : product.stock_quantity <= 10
                                                                ? "bg-warning text-dark"
                                                                : "bg-info text-dark"
                                                    }`}
                                                >
                                                    {product.stock_quantity === 0
                                                        ? "Out of Stock"
                                                        : product.stock_quantity <= 10
                                                            ? "Low Stock"
                                                            : "In Stock"}
                                                </span>
                                            </td>
                                            <td>
                                                <div className="d-flex gap-2">
                                                    <button type="button" className="btn btn-sm btn-outline-primary" onClick={() => handleEdit(product.id)}>
                                                        Edit
                                                    </button>
                                                    <button type="button" className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(product.id)}>
                                                        Delete
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SupplierProducts;

