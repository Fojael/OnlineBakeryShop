import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import { getInventory } from "../../../services/inventoryService";

const ProductionBatches = () => {
    const [inventory, setInventory] = useState([]);
    const [batches, setBatches] = useState([]);
    const [form, setForm] = useState({
        product: "",
        batch_number: "",
        production_date: "",
        expiry_date: "",
        quantity: "",
    });
    const [error, setError] = useState("");

    const loadData = async () => {
        const [inventoryResponse, batchResponse] = await Promise.all([
            getInventory(),
            api.get("inventory/batches/"),
        ]);
        setInventory(inventoryResponse.data || []);
        setBatches(batchResponse.data || []);
    };

    useEffect(() => {
        loadData().catch(() => setError("Failed to load production batches."));
    }, []);

    const submit = async (event) => {
        event.preventDefault();
        setError("");
        try {
            await api.post("inventory/batches/", form);
            setForm({ ...form, batch_number: "", production_date: "", expiry_date: "", quantity: "" });
            await loadData();
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to create production batch."
            );
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2>Production Batches</h2>
                <p className="text-muted">Track bakery batch numbers, production dates, expiry dates, and quantities.</p>
                {error && <div className="alert alert-danger">{error}</div>}
                <form className="row g-2 mb-4" onSubmit={submit}>
                    <div className="col-md-3"><select className="form-select" required value={form.product} onChange={(event) => setForm({ ...form, product: event.target.value })}><option value="">Select product</option>{inventory.map((item) => <option key={item.product} value={item.product}>{item.product_name}</option>)}</select></div>
                    <div className="col-md-2"><input className="form-control" required placeholder="Batch number" value={form.batch_number} onChange={(event) => setForm({ ...form, batch_number: event.target.value })} /></div>
                    <div className="col-md-2"><input className="form-control" required type="date" value={form.production_date} onChange={(event) => setForm({ ...form, production_date: event.target.value })} /></div>
                    <div className="col-md-2"><input className="form-control" required type="date" value={form.expiry_date} onChange={(event) => setForm({ ...form, expiry_date: event.target.value })} /></div>
                    <div className="col-md-1"><input className="form-control" required type="number" min="1" placeholder="Qty" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: event.target.value })} /></div>
                    <div className="col-md-2"><button className="btn btn-primary w-100">Add Batch</button></div>
                </form>
                <div className="card border-0 shadow-sm"><div className="table-responsive"><table className="table align-middle mb-0"><thead><tr><th>Product</th><th>Batch</th><th>Produced</th><th>Expires</th><th>Quantity</th><th>Remaining</th></tr></thead><tbody>{batches.map((batch) => <tr key={batch.id}><td>{batch.product_name}</td><td>{batch.batch_number}</td><td>{batch.production_date}</td><td>{batch.expiry_date}</td><td>{batch.quantity}</td><td>{batch.remaining_quantity}</td></tr>)}</tbody></table></div></div>
            </div>
        </DashboardLayout>
    );
};

export default ProductionBatches;
