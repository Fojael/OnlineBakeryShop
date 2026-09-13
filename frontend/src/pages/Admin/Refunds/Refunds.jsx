import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const STATUS_CLASSES = {
    Pending: "bg-warning text-dark",
    Approved: "bg-info text-dark",
    Rejected: "bg-danger",
    Processing: "bg-primary",
    Completed: "bg-success",
    Failed: "bg-danger",
};

const formatDate = (value) => value ? new Date(value).toLocaleString() : "-";
const money = (value) => `৳${Number(value || 0).toFixed(2)}`;

const RefundDetails = ({
    refund,
    loading,
    error,
    updating,
    adminNote,
    onAdminNoteChange,
    onDecision,
    onClose,
}) => {
    if (!refund && loading) {
        return (
            <div className="modal d-block" role="dialog" aria-modal="true">
                <div className="modal-dialog"><div className="modal-content"><div className="modal-body p-5 text-center">Loading refund details...</div></div></div>
            </div>
        );
    }
    if (!refund) return null;

    const eligible = Number(refund.eligible_amount || refund.refund_amount || 0);
    const fullAmount = Number(refund.calculated_full_amount || eligible);
    const partialAmount = Number(refund.calculated_partial_amount || (eligible * 0.25).toFixed(2));
    const canDecide = refund.status === "Pending";

    return (
        <div className="modal d-block" role="dialog" aria-modal="true">
            <div className="modal-dialog modal-xl modal-dialog-scrollable">
                <div className="modal-content">
                    <div className="modal-header">
                        <div>
                            <h5 className="modal-title">Refund Request #{refund.id}</h5>
                            <span className={`badge ${STATUS_CLASSES[refund.status] || "bg-secondary"}`}>{refund.status}</span>
                        </div>
                        <button type="button" className="btn-close" aria-label="Close" onClick={onClose} />
                    </div>
                    <div className="modal-body">
                        {error && <div className="alert alert-danger">{error}</div>}
                        <div className="row g-4">
                            <section className="col-lg-6">
                                <h6>Request and Customer</h6>
                                <dl className="row mb-0">
                                    <dt className="col-sm-5">Order</dt><dd className="col-sm-7">#{refund.order}</dd>
                                    <dt className="col-sm-5">Requested</dt><dd className="col-sm-7">{formatDate(refund.requested_at)}</dd>
                                    <dt className="col-sm-5">Order date</dt><dd className="col-sm-7">{formatDate(refund.order_date)}</dd>
                                    <dt className="col-sm-5">Customer</dt><dd className="col-sm-7">{refund.customer_name || "-"}</dd>
                                    <dt className="col-sm-5">Email</dt><dd className="col-sm-7">{refund.customer_email || "-"}</dd>
                                    <dt className="col-sm-5">Phone</dt><dd className="col-sm-7">{refund.customer_phone || "-"}</dd>
                                    <dt className="col-sm-5">Address</dt><dd className="col-sm-7">{refund.customer_address || "-"}</dd>
                                </dl>
                            </section>
                            <section className="col-lg-6">
                                <h6>Order and Decision</h6>
                                <dl className="row mb-0">
                                    <dt className="col-sm-5">Order status</dt><dd className="col-sm-7">{refund.order_status || "-"}</dd>
                                    <dt className="col-sm-5">Payment method</dt><dd className="col-sm-7">{refund.payment_method || "-"}</dd>
                                    <dt className="col-sm-5">Payment status</dt><dd className="col-sm-7">{refund.payment_status || "-"}</dd>
                                    <dt className="col-sm-5">Original total</dt><dd className="col-sm-7">{money(refund.original_order_total)}</dd>
                                    <dt className="col-sm-5">Eligible amount</dt><dd className="col-sm-7">{money(eligible)}</dd>
                                    <dt className="col-sm-5">Admin decision</dt><dd className="col-sm-7">{refund.admin_decision || "Pending admin decision"}</dd>
                                    <dt className="col-sm-5">Decision date</dt><dd className="col-sm-7">{formatDate(refund.reviewed_at)}</dd>
                                </dl>
                            </section>
                        </div>

                        <section className="mt-4">
                            <h6>Customer Request</h6>
                            <p className="mb-1"><strong>Reason:</strong> {refund.reason}</p>
                            <p className="mb-0"><strong>Additional details:</strong> {refund.description || "-"}</p>
                        </section>

                        <section className="mt-4">
                            <h6>Requested Products</h6>
                            <div className="table-responsive">
                                <table className="table table-sm align-middle">
                                    <thead><tr><th>Product</th><th>Purchased</th><th>Requested</th><th>Price</th><th>Eligible</th></tr></thead>
                                    <tbody>
                                        {refund.items?.length ? refund.items.map((item) => (
                                            <tr key={item.order_item_id}>
                                                <td>{item.product_name}</td><td>{item.purchased_quantity}</td><td>{item.quantity}</td><td>{money(item.product_price)}</td><td>{money(item.amount)}</td>
                                            </tr>
                                        )) : <tr><td colSpan="5">No item details available.</td></tr>}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        <section className="mt-4">
                            <h6>Product Photos</h6>
                            {refund.photos?.length ? (
                                <div className="d-flex flex-wrap gap-2">
                                    {refund.photos.map((photo) => (
                                        <a href={photo.image} key={photo.id} target="_blank" rel="noreferrer">
                                            <img src={photo.image} alt={`Refund ${refund.id} evidence`} width="96" height="96" className="rounded border object-fit-cover" />
                                        </a>
                                    ))}
                                </div>
                            ) : <p className="text-muted mb-0">No photos uploaded.</p>}
                        </section>

                        <section className="mt-4">
                            <h6>Refund Calculation</h6>
                            <div className="border rounded p-3 bg-light">
                                <div>Eligible Refund Amount: <strong>{money(eligible)}</strong></div>
                                <div>Full Refund (100%): <strong>{money(fullAmount)}</strong></div>
                                <div>Partial Refund (25%): <strong>{money(partialAmount)}</strong></div>
                                {canDecide && <div className="text-muted small mt-2">The backend recalculates and validates the final amount when confirmed.</div>}
                            </div>
                        </section>

                        <section className="mt-4">
                            <h6>Refund Status History</h6>
                            {refund.history?.length ? (
                                <ul className="list-group">
                                    {refund.history.map((entry) => (
                                        <li className="list-group-item d-flex justify-content-between" key={entry.id}>
                                            <span><strong>{entry.status}</strong>{entry.note ? `: ${entry.note}` : ""}</span>
                                            <small className="text-muted">{formatDate(entry.created_at)} by {entry.actor_name || "System"}</small>
                                        </li>
                                    ))}
                                </ul>
                            ) : <p className="text-muted mb-0">No status history available.</p>}
                        </section>

                        {canDecide && (
                            <section className="mt-4 border-top pt-3">
                                <h6>Admin Decision</h6>
                                <textarea className="form-control mb-3" rows="2" placeholder="Required when rejecting" value={adminNote} onChange={(event) => onAdminNoteChange(event.target.value)} />
                                <div className="d-flex flex-wrap gap-2">
                                    <button type="button" className="btn btn-success" disabled={updating} onClick={() => onDecision("approve-full")}>Approve Full Refund</button>
                                    <button type="button" className="btn btn-outline-success" disabled={updating} onClick={() => onDecision("approve-partial")}>Approve Partial Refund 25%</button>
                                    <button type="button" className="btn btn-outline-danger" disabled={updating || !adminNote.trim()} onClick={() => onDecision("reject")}>Reject</button>
                                </div>
                            </section>
                        )}
                        {!canDecide && refund.admin_notes && <div className="alert alert-secondary mt-4 mb-0">Admin decision note: {refund.admin_notes}</div>}
                    </div>
                </div>
            </div>
        </div>
    );
};

const Refunds = () => {
    const [refunds, setRefunds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedRefund, setSelectedRefund] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [detailsError, setDetailsError] = useState("");
    const [updating, setUpdating] = useState(false);
    const [adminNote, setAdminNote] = useState("");

    const loadRefunds = async () => {
        try {
            const response = await api.get("orders/refunds/admin/");
            setRefunds(response.data || []);
        } catch (requestError) {
            setError(requestError.response?.data?.detail || "Failed to load refund requests.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let mounted = true;

        const fetchRefunds = async () => {
            try {
                const response = await api.get("orders/refunds/admin/");
                if (mounted) setRefunds(response.data || []);
            } catch (requestError) {
                if (mounted) {
                    setError(requestError.response?.data?.detail || "Failed to load refund requests.");
                }
            } finally {
                if (mounted) setLoading(false);
            }
        };

        void fetchRefunds();
        return () => {
            mounted = false;
        };
    }, []);

    const openDetails = async (refundId) => {
        setDetailsLoading(true);
        setDetailsError("");
        setSelectedRefund(null);
        try {
            const response = await api.get(`orders/refunds/admin/${refundId}/`);
            setSelectedRefund(response.data);
            setAdminNote("");
        } catch (requestError) {
            setDetailsError(requestError.response?.data?.detail || "Failed to load refund details.");
        } finally {
            setDetailsLoading(false);
        }
    };

    const decideRefund = async (decision) => {
        if (!selectedRefund) return;
        const eligible = Number(selectedRefund.eligible_amount || 0);
        const amount = decision === "approve-partial" ? (eligible * 0.25).toFixed(2) : eligible.toFixed(2);
        const prompt = decision === "reject"
            ? `Reject refund request #${selectedRefund.id}?`
            : `Eligible Refund Amount: ৳${eligible.toFixed(2)}\n${decision === "approve-partial" ? "Partial Refund (25%)" : "Full Refund (100%)"}: ৳${amount}\n\nConfirm this admin decision?`;
        if (!window.confirm(prompt)) return;

        setUpdating(true);
        setDetailsError("");
        try {
            await api.post(`orders/refunds/admin/${selectedRefund.id}/${decision}/`, decision === "reject" ? { admin_notes: adminNote } : {});
            await loadRefunds();
            await openDetails(selectedRefund.id);
        } catch (requestError) {
            setDetailsError(requestError.response?.data?.detail || "Failed to update refund.");
        } finally {
            setUpdating(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Refunds</h2>
                <p className="text-muted mb-4">Review customer refund requests and record admin decisions.</p>
                {error && <div className="alert alert-danger">{error}</div>}
                <div className="card border-0 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead><tr><th>Request</th><th>Order</th><th>Customer</th><th>Requested Products</th><th>Eligible Amount</th><th>Status</th><th>Admin Decision</th><th>Action</th></tr></thead>
                            <tbody>
                                {loading ? <tr><td colSpan="8">Loading refunds...</td></tr> : refunds.length === 0 ? <tr><td colSpan="8">No refund requests found.</td></tr> : refunds.map((refund) => (
                                    <tr key={refund.id}>
                                        <td>#{refund.id}</td><td>#{refund.order}</td>
                                        <td><div>{refund.customer_name || "-"}</div><small className="text-muted">{refund.customer_email || "-"}</small></td>
                                        <td>{refund.items?.length || 0}</td><td>{money(refund.eligible_amount)}</td>
                                        <td><span className={`badge ${STATUS_CLASSES[refund.status] || "bg-secondary"}`}>{refund.status}</span></td>
                                        <td>{refund.admin_decision || "Pending admin decision"}</td>
                                        <td><button type="button" className="btn btn-outline-primary btn-sm" onClick={() => openDetails(refund.id)}>Details</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {(selectedRefund || detailsLoading || detailsError) && <RefundDetails refund={selectedRefund} loading={detailsLoading} error={detailsError} updating={updating} adminNote={adminNote} onAdminNoteChange={setAdminNote} onDecision={decideRefund} onClose={() => { setSelectedRefund(null); setDetailsError(""); }} />}
        </DashboardLayout>
    );
};

export default Refunds;
