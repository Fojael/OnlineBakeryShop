import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const Refunds = () => {
    const [refunds, setRefunds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updatingId, setUpdatingId] = useState(null);
    const [expandedId, setExpandedId] = useState(null);
    const [adminNotes, setAdminNotes] = useState({});

    const formatDate = (value) => value
        ? new Date(value).toLocaleString()
        : "-";

    const statusClass = (status) => ({
        Pending: "bg-warning text-dark",
        Approved: "bg-info text-dark",
        Rejected: "bg-danger",
        Processing: "bg-primary",
        Completed: "bg-success",
        Failed: "bg-danger",
    }[status] || "bg-secondary");

    const loadRefunds = async () => {
        try {
            const response = await api.get("orders/refunds/admin/");
            setRefunds(response.data || []);
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to load refund requests."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let mounted = true;

        const fetchRefunds = async () => {
            try {
                const response = await api.get("orders/refunds/admin/");
                if (mounted) {
                    setRefunds(response.data || []);
                }
            } catch (requestError) {
                if (mounted) {
                    setError(
                        requestError.response?.data?.detail ||
                        "Failed to load refund requests."
                    );
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        void fetchRefunds();

        return () => {
            mounted = false;
        };
    }, []);

    const updateRefund = async (refundId, status, approvedAmount) => {
        setUpdatingId(refundId);
        setError("");

        try {
            const payload = { status };
            if (status === "Approved") {
                payload.refund_type = approvedAmount;
            }
            if (status === "Rejected") {
                payload.admin_notes = adminNotes[refundId] || "";
            }
            await api.patch(
                `orders/refunds/admin/${refundId}/update/`,
                payload
            );
            await loadRefunds();
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to update refund."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    const processRefund = async (refundId) => {
        setUpdatingId(refundId);
        setError("");
        try {
            await api.post(`orders/refunds/admin/${refundId}/process/`);
            await loadRefunds();
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to process refund."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Refunds</h2>
                <p className="text-muted mb-4">
                    Review and process customer refund requests.
                </p>

                {error && <div className="alert alert-danger">{error}</div>}

                <div className="card border-0 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Request</th>
                                    <th>Order</th>
                                    <th>Customer</th>
                                    <th>Requested</th>
                                                    <th>Requested products</th>
                                                    <th>Eligible amount</th>
                                    <th>Status</th>
                                    <th>Admin decision</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="8">Loading refunds...</td>
                                    </tr>
                                ) : refunds.length === 0 ? (
                                    <tr>
                                        <td colSpan="8">No refund requests found.</td>
                                    </tr>
                                ) : (
                                    refunds.flatMap((refund) => [
                                        <tr key={refund.id}>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="btn btn-link btn-sm p-0"
                                                    onClick={() => setExpandedId(
                                                        expandedId === refund.id ? null : refund.id,
                                                    )}
                                                >
                                                    #{refund.id}
                                                </button>
                                            </td>
                                            <td>#{refund.order}</td>
                                            <td>
                                                <div>{refund.customer_name || "-"}</div>
                                                <small className="text-muted">{refund.customer_email || "-"}</small>
                                            </td>
                                            <td>{formatDate(refund.requested_at)}</td>
                                            <td>{refund.items?.length || "All selected"}</td>
                                            <td>৳{refund.refund_amount}</td>
                                            <td>
                                                <span className={`badge ${statusClass(refund.status)}`}>
                                                    {refund.status}
                                                </span>
                                            </td>
                                            <td>
                                                {refund.status === "Pending" && (
                                                    <div className="d-flex gap-2">
                                                        <button
                                                            className="btn btn-success btn-sm"
                                                            disabled={updatingId === refund.id}
                                                            onClick={() => updateRefund(
                                                                refund.id,
                                                                "Approved",
                                                                "FULL",
                                                            )}
                                                        >
                                                            Approve Full Refund
                                                        </button>
                                                        <button
                                                            className="btn btn-outline-success btn-sm"
                                                            disabled={updatingId === refund.id}
                                                            onClick={() => updateRefund(
                                                                refund.id,
                                                                "Approved",
                                                                "PARTIAL",
                                                            )}
                                                        >
                                                            Approve 25% Partial
                                                        </button>
                                                        <button
                                                            className="btn btn-outline-danger btn-sm"
                                                            disabled={
                                                                updatingId === refund.id ||
                                                                !adminNotes[refund.id]?.trim()
                                                            }
                                                            onClick={() => updateRefund(refund.id, "Rejected")}
                                                        >
                                                            Reject
                                                        </button>
                                                    </div>
                                                )}
                                                {refund.status === "Approved" && !refund.is_recorded_internally && (
                                                    <button
                                                        className="btn btn-primary btn-sm"
                                                        disabled={updatingId === refund.id}
                                                        onClick={() => processRefund(refund.id)}
                                                    >
                                                        Record Refund
                                                    </button>
                                                )}
                                            </td>
                                        </tr>,
                                        expandedId === refund.id && (
                                            <tr key={`${refund.id}-details`}>
                                                <td colSpan="8" className="bg-light">
                                                    <div className="p-3">
                                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                                            <h5 className="mb-0">Refund request #{refund.id}</h5>
                                                            <span className={`badge ${statusClass(refund.status)}`}>
                                                                Current status: {refund.status}
                                                            </span>
                                                        </div>
                                                        <div className="row g-3">
                                                            <div className="col-lg-6">
                                                                <h6>Customer Request</h6>
                                                                <dl className="row mb-0">
                                                                    <dt className="col-sm-5">Admin decision</dt>
                                                                    <dd className="col-sm-7">{refund.status === "Approved" ? `${refund.refund_type === "PARTIAL" ? "Partial Refund (25%)" : "Full Refund (100%)"}` : "Pending admin decision"}</dd>
                                                                    <dt className="col-sm-5">Reason</dt>
                                                                    <dd className="col-sm-7">{refund.reason}</dd>
                                                                    <dt className="col-sm-5">Description</dt>
                                                                    <dd className="col-sm-7">{refund.description || "-"}</dd>
                                                                    <dt className="col-sm-5">Calculated amount</dt>
                                                                    <dd className="col-sm-7">৳{refund.refund_amount}</dd>
                                                                </dl>
                                                                <h6 className="mt-3">Requested Products</h6>
                                                                {refund.items?.length ? (
                                                                    <ul className="mb-0">
                                                                        {refund.items.map((item) => (
                                                                            <li key={item.order_item_id}>
                                                                                {item.product_name} x {item.quantity} (৳{item.amount})
                                                                            </li>
                                                                        ))}
                                                                    </ul>
                                                                ) : (
                                                                    <p className="text-muted mb-0">All eligible order items.</p>
                                                                )}
                                                            </div>
                                                            <div className="col-lg-6">
                                                                <h6>Order and Payment</h6>
                                                                <dl className="row mb-0">
                                                                    <dt className="col-sm-5">Order</dt>
                                                                    <dd className="col-sm-7">#{refund.order}</dd>
                                                                    <dt className="col-sm-5">Payment method</dt>
                                                                    <dd className="col-sm-7">{refund.payment_method || "-"}</dd>
                                                                    <dt className="col-sm-5">Payment status</dt>
                                                                    <dd className="col-sm-7">{refund.payment_status || "-"}</dd>
                                                                    <dt className="col-sm-5">Internal record</dt>
                                                                    <dd className="col-sm-7">{refund.is_recorded_internally ? "Recorded by Admin" : "Not recorded"}</dd>
                                                                    <dt className="col-sm-5">Requested</dt>
                                                                    <dd className="col-sm-7">{formatDate(refund.requested_at)}</dd>
                                                                </dl>
                                                                <h6 className="mt-3">Product Photos</h6>
                                                                {refund.photos?.length ? (
                                                                    <div className="d-flex flex-wrap gap-2">
                                                                        {refund.photos.map((photo) => (
                                                                            <a
                                                                                href={photo.image}
                                                                                key={photo.id}
                                                                                target="_blank"
                                                                                rel="noreferrer"
                                                                            >
                                                                                <img
                                                                                    src={photo.image}
                                                                                    alt={`Refund ${refund.id} evidence`}
                                                                                    width="92"
                                                                                    height="92"
                                                                                    className="rounded border object-fit-cover"
                                                                                />
                                                                            </a>
                                                                        ))}
                                                                    </div>
                                                                ) : (
                                                                    <p className="text-muted mb-0">No photos uploaded.</p>
                                                                )}
                                                            </div>
                                                        </div>
                                                        <div className="border-top mt-3 pt-3">
                                                            <h6>Admin Decision</h6>
                                                            {refund.status === "Pending" ? (
                                                                <div className="row align-items-end g-2">
                                                                    <div className="col-md-4 text-muted small">Choose exactly one approval decision: Full Refund (100%) or Partial Refund (25%).</div>
                                                                    <div className="col-md-8 text-muted small">
                                                                        <label
                                                                            className="form-label"
                                                                            htmlFor={`admin-note-${refund.id}`}
                                                                        >
                                                                            Rejection reason
                                                                        </label>
                                                                        <textarea
                                                                            id={`admin-note-${refund.id}`}
                                                                            className="form-control"
                                                                            rows="2"
                                                                            placeholder="Required when rejecting"
                                                                            value={adminNotes[refund.id] || ""}
                                                                            onChange={(event) => setAdminNotes({
                                                                                ...adminNotes,
                                                                                [refund.id]: event.target.value,
                                                                            })}
                                                                        />
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <div className="text-muted">
                                                                    <div>Decision recorded as {refund.admin_decision || refund.status}.</div>
                                                                    {refund.approved_amount && (
                                                                        <div>{refund.refund_type === "PARTIAL" ? "Partial Refund (25%)" : "Full Refund (100%)"}: ৳{refund.approved_amount}</div>
                                                                    )}
                                                                    {refund.reviewer_name && (
                                                                        <div>Reviewed by {refund.reviewer_name} on {formatDate(refund.reviewed_at)}</div>
                                                                    )}
                                                                    {refund.admin_notes && (
                                                                        <div>Admin note: {refund.admin_notes}</div>
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        ),
                                    ])
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default Refunds;
