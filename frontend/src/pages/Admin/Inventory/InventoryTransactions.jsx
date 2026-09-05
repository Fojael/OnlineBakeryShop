import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import { getInventory } from "../../../services/inventoryService";

const InventoryTransactions = () => {
    const [inventory, setInventory] = useState([]);
    const [transactions, setTransactions] = useState([]);
    const [form, setForm] = useState({
        inventory: "",
        transaction_type: "STOCK_IN",
        quantity: "",
        reason: "",
    });
    const [error, setError] = useState("");

    const loadData = async () => {
        const [inventoryResponse, transactionResponse] = await Promise.all([
            getInventory(),
            api.get("inventory/transactions/"),
        ]);
        setInventory(inventoryResponse.data || []);
        setTransactions(transactionResponse.data || []);
    };

    useEffect(() => {
        loadData().catch(() => setError("Failed to load stock history."));
    }, []);

    const submit = async (event) => {
        event.preventDefault();
        setError("");
        try {
            await api.post("inventory/transactions/", form);
            setForm({ ...form, quantity: "", reason: "" });
            await loadData();
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to record stock movement."
            );
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2>Stock Movements</h2>
                <p className="text-muted">Record stock in, stock out, and adjustments.</p>
                {error && <div className="alert alert-danger">{error}</div>}
                <form className="row g-2 mb-4" onSubmit={submit}>
                    <div className="col-md-3">
                        <select className="form-select" required value={form.inventory} onChange={(event) => setForm({ ...form, inventory: event.target.value })}>
                            <option value="">Select product</option>
                            {inventory.map((item) => <option key={item.id} value={item.id}>{item.product_name}</option>)}
                        </select>
                    </div>
                    <div className="col-md-2">
                        <select className="form-select" value={form.transaction_type} onChange={(event) => setForm({ ...form, transaction_type: event.target.value })}>
                            <option value="STOCK_IN">Stock In</option>
                            <option value="STOCK_OUT">Stock Out</option>
                            <option value="ADJUSTMENT">Adjustment</option>
                        </select>
                    </div>
                    <div className="col-md-2">
                        <input className="form-control" type="number" required placeholder="Quantity" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: event.target.value })} />
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" placeholder="Reason" value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} />
                    </div>
                    <div className="col-md-2"><button className="btn btn-primary w-100">Record Movement</button></div>
                </form>
                <div className="card border-0 shadow-sm"><div className="table-responsive"><table className="table align-middle mb-0"><thead><tr><th>Product</th><th>Type</th><th>Quantity</th><th>Before</th><th>After</th><th>Reason</th></tr></thead><tbody>{transactions.map((item) => <tr key={item.id}><td>{item.product_name}</td><td>{item.transaction_type}</td><td>{item.quantity}</td><td>{item.previous_stock}</td><td>{item.resulting_stock}</td><td>{item.reason || "-"}</td></tr>)}</tbody></table></div></div>
            </div>
        </DashboardLayout>
    );
};

export default InventoryTransactions;
