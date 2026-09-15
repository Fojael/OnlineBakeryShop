import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getApiErrorMessage } from "../../../services/api";
import { createOfflineSale } from "../../../services/offlineSalesService";
import { getProducts } from "../../../services/productService";
import OfflineReceipt from "./OfflineReceipt";

const emptyForm = {
    customer_name: "",
    phone: "",
};

const getProductsFromResponse = (response) => {
    const data = response?.data;
    return Array.isArray(data) ? data : data?.results || [];
};

const OfflineSales = () => {
    const [products, setProducts] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [search, setSearch] = useState("");
    const [selectedProductId, setSelectedProductId] = useState("");
    const [quantity, setQuantity] = useState(1);
    const [items, setItems] = useState([]);
    const [receipt, setReceipt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        let mounted = true;
        getProducts({ availability: "in_stock", page_size: 100 })
            .then((response) => {
                if (mounted) setProducts(getProductsFromResponse(response));
            })
            .catch((error) => {
                if (mounted) {
                    toast.error(getApiErrorMessage(error, "Unable to load products."));
                }
            })
            .finally(() => {
                if (mounted) setLoading(false);
            });
        return () => {
            mounted = false;
        };
    }, []);

    const filteredProducts = useMemo(() => {
        const term = search.trim().toLowerCase();
        return products.filter((product) => (
            !term || product.name.toLowerCase().includes(term)
        ));
    }, [products, search]);

    const selectedProduct = products.find(
        (product) => String(product.id) === String(selectedProductId),
    );

    const previewSubtotal = items.reduce(
        (total, item) => total + Number(item.price) * item.quantity,
        0,
    );

    const updateForm = (event) => {
        setForm((current) => ({
            ...current,
            [event.target.name]: event.target.value,
        }));
    };

    const addItem = () => {
        const requestedQuantity = Number(quantity);
        if (!selectedProduct) {
            toast.warning("Select a product first.");
            return;
        }
        if (!Number.isInteger(requestedQuantity) || requestedQuantity <= 0) {
            toast.warning("Quantity must be a positive whole number.");
            return;
        }
        if (requestedQuantity > Number(selectedProduct.stock_quantity)) {
            toast.warning("Quantity cannot exceed available stock.");
            return;
        }
        if (items.some((item) => item.product_id === selectedProduct.id)) {
            toast.warning("That product is already in the sale.");
            return;
        }

        setItems((current) => [
            ...current,
            {
                product_id: selectedProduct.id,
                name: selectedProduct.name,
                price: selectedProduct.price,
                stock_quantity: selectedProduct.stock_quantity,
                quantity: requestedQuantity,
            },
        ]);
        setSelectedProductId("");
        setQuantity(1);
    };

    const removeItem = (productId) => {
        setItems((current) => current.filter((item) => item.product_id !== productId));
    };

    const changeQuantity = (productId, nextQuantity) => {
        setItems((current) => current.map((item) => (
            item.product_id === productId
                ? { ...item, quantity: Math.max(1, Math.min(Number(nextQuantity), Number(item.stock_quantity))) }
                : item
        )));
    };

    const resetSale = () => {
        setForm(emptyForm);
        setItems([]);
        setReceipt(null);
        setSearch("");
        setSelectedProductId("");
        setQuantity(1);
    };

    const submitSale = async (event) => {
        event.preventDefault();
        if (!form.customer_name.trim() || !form.phone.trim()) {
            toast.warning("Customer name and phone are required.");
            return;
        }
        if (items.length === 0) {
            toast.warning("Add at least one product.");
            return;
        }

        setSubmitting(true);
        try {
            const response = await createOfflineSale({
                customer_name: form.customer_name.trim(),
                phone: form.phone.trim(),
                items: items.map((item) => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                })),
            });
            setReceipt(response.data.order);
            toast.success("Offline sale created successfully.");
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to create offline sale."));
        } finally {
            setSubmitting(false);
        }
    };

    if (receipt) {
        return (
            <DashboardLayout>
                <OfflineReceipt order={receipt} onCreateAnother={resetSale} />
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <div className="mb-4"><h2 className="mb-1">Create Offline Sale</h2><p className="text-muted mb-0">Record a paid counter sale using current inventory.</p></div>
                <form onSubmit={submitSale}>
                    <div className="row g-4">
                        <div className="col-lg-7">
                            <div className="card border-0 shadow-sm mb-4"><div className="card-body"><h5 className="mb-3">Customer Information</h5><div className="row g-3"><div className="col-md-6"><label className="form-label">Customer Name</label><input className="form-control" name="customer_name" value={form.customer_name} onChange={updateForm} required /></div><div className="col-md-6"><label className="form-label">Phone</label><input className="form-control" name="phone" value={form.phone} onChange={updateForm} required /></div></div></div></div>
                            <div className="card border-0 shadow-sm"><div className="card-body"><h5 className="mb-3">Product Selection</h5>{loading ? <div className="text-muted">Loading products...</div> : <><div className="row g-2 align-items-end"><div className="col-md-5"><label className="form-label">Search</label><input className="form-control" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search products" /></div><div className="col-md-4"><label className="form-label">Product</label><select className="form-select" value={selectedProductId} onChange={(event) => setSelectedProductId(event.target.value)}><option value="">Select product</option>{filteredProducts.map((product) => <option key={product.id} value={product.id}>{product.name} · ৳{product.price} · {product.stock_quantity} available</option>)}</select></div><div className="col-md-2"><label className="form-label">Quantity</label><input className="form-control" type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></div><div className="col-md-1"><button type="button" className="btn btn-primary w-100" onClick={addItem} aria-label="Add product">+</button></div></div>{selectedProduct && <div className="small text-muted mt-2">Current price: ৳{selectedProduct.price} · Available stock: {selectedProduct.stock_quantity}</div>}</>}</div></div>
                        </div>
                        <div className="col-lg-5"><div className="card border-0 shadow-sm"><div className="card-body"><h5 className="mb-3">Order Summary</h5>{items.length === 0 ? <p className="text-muted">No products added.</p> : <div className="table-responsive"><table className="table table-sm align-middle"><thead><tr><th>Product</th><th>Qty</th><th className="text-end">Preview</th><th /></tr></thead><tbody>{items.map((item) => <tr key={item.product_id}><td>{item.name}<div className="small text-muted">৳{item.price}</div></td><td><input className="form-control form-control-sm" type="number" min="1" max={item.stock_quantity} value={item.quantity} onChange={(event) => changeQuantity(item.product_id, event.target.value)} /></td><td className="text-end">৳{(Number(item.price) * item.quantity).toFixed(2)}</td><td><button type="button" className="btn btn-sm btn-outline-danger" onClick={() => removeItem(item.product_id)} aria-label={`Remove ${item.name}`}>×</button></td></tr>)}</tbody></table></div>}<div className="d-flex justify-content-between"><span>Preview subtotal</span><strong>৳{previewSubtotal.toFixed(2)}</strong></div><div className="d-flex justify-content-between"><span>Delivery charge</span><strong>৳0.00</strong></div><div className="d-flex justify-content-between border-top mt-2 pt-2"><span>Server total after submit</span><strong>৳{previewSubtotal.toFixed(2)}</strong></div><button className="btn btn-success w-100 mt-4" type="submit" disabled={submitting}>{submitting ? "Creating sale..." : "Confirm and Create Sale"}</button></div></div></div>
                    </div>
                </form>
            </div>
        </DashboardLayout>
    );
};

export default OfflineSales;
