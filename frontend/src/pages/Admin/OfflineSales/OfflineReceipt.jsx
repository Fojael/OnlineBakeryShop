import "./offlineSales.css";

const OfflineReceipt = ({ order, onCreateAnother }) => {
    if (!order) return null;

    const downloadReceipt = () => {
        const rows = [
            ["Invoice", order.id],
            ["Date", new Date(order.created_at).toLocaleString()],
            ["Sale Type", "Offline Sale"],
            ["Customer", order.customer_name],
            ["Phone", order.offline_customer_phone],
            ["Payment", "CASH / PAID"],
            [],
            ["SL", "Product Name", "Quantity", "Unit Price", "Line Total"],
            ...(order.items || []).map((item, index) => [
                index + 1,
                item.product_name,
                item.quantity,
                item.price,
                item.subtotal,
            ]),
            [],
            ["Subtotal", order.subtotal],
            ["Delivery Charge", order.delivery_charge],
            ["Grand Total", order.total_amount],
        ];
        const csv = rows
            .map((row) => row.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(","))
            .join("\n");
        const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = `offline-invoice-${order.id}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="offline-receipt-page">
            <div className="offline-receipt-actions d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
                <div>
                    <h2 className="mb-1">Offline Sale Receipt</h2>
                    <p className="text-muted mb-0">Invoice #{order.id}</p>
                </div>
                <div className="d-flex gap-2">
                    <button type="button" className="btn btn-primary" onClick={() => window.print()}>Print Receipt</button>
                    <button type="button" className="btn btn-outline-secondary" onClick={downloadReceipt}>Download Receipt</button>
                    <button type="button" className="btn btn-outline-success" onClick={onCreateAnother}>Create Another Sale</button>
                </div>
            </div>
            <article className="offline-receipt-sheet">
                <header className="offline-receipt-header">
                    <div>
                        <h1>Online Bakery Shop</h1>
                        <p className="mb-0">Offline Counter Sale Receipt</p>
                    </div>
                    <div className="text-end">
                        <strong>Invoice #{order.id}</strong>
                        <div>{new Date(order.created_at).toLocaleDateString()}</div>
                        <div>{new Date(order.created_at).toLocaleTimeString()}</div>
                    </div>
                </header>
                <div className="offline-receipt-meta row g-3 mb-4">
                    <div className="col-md-4"><strong>Sale Type</strong><div>Offline Sale</div></div>
                    <div className="col-md-4"><strong>Customer</strong><div>{order.customer_name}</div><div>{order.offline_customer_phone}</div></div>
                    <div className="col-md-4"><strong>Created By</strong><div>{order.created_by_name || "Admin"}</div></div>
                </div>
                <table className="table offline-receipt-items">
                    <thead><tr><th>SL</th><th>Product Name</th><th>Quantity</th><th>Unit Price</th><th className="text-end">Line Total</th></tr></thead>
                    <tbody>{(order.items || []).map((item, index) => <tr key={item.id || `${item.product_id}-${index}`}><td>{index + 1}</td><td>{item.product_name}</td><td>{item.quantity}</td><td>৳{item.price}</td><td className="text-end">৳{item.subtotal}</td></tr>)}</tbody>
                </table>
                <div className="offline-receipt-summary">
                    <div><span>Subtotal</span><strong>৳{order.subtotal}</strong></div>
                    <div><span>Delivery Charge</span><strong>৳{order.delivery_charge}</strong></div>
                    <div className="grand-total"><span>Grand Total</span><strong>৳{order.total_amount}</strong></div>
                </div>
                <footer className="offline-receipt-footer">
                    <div><strong>Payment</strong><div>CASH / OFFLINE</div><div>PAID</div></div>
                    <p className="mb-0">Thank you for shopping with Online Bakery Shop.</p>
                </footer>
            </article>
        </div>
    );
};

export default OfflineReceipt;