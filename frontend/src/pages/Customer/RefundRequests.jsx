import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import DashboardLayout from "../../layouts/DashboardLayout";
import { getRefunds } from "../../services/refundService";

const STATUS_STYLES = {
    Pending: "bg-warning text-dark",
    Approved: "bg-info text-dark",
    Rejected: "bg-danger",
    Completed: "bg-success",
};

const formatDate = (value) => (
    value
        ? new Date(value).toLocaleDateString()
        : "-"
);

const RefundRequests = () => {
    const [refunds, setRefunds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let mounted = true;

        getRefunds()
            .then((response) => {
                if (mounted) setRefunds(response.data || []);
            })
            .catch((requestError) => {
                if (mounted) {
                    setError(
                        requestError.response?.data?.detail ||
                        "Failed to load refund requests."
                    );
                }
            })
            .finally(() => {
                if (mounted) setLoading(false);
            });

        return () => {
            mounted = false;
        };
    }, []);

    return (
        <DashboardLayout>
            <div className="container py-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2 className="mb-1">Refund Requests</h2>
                        <p className="text-muted mb-0">
                            Track every refund from request to completion.
                        </p>
                    </div>
                    <Link className="btn btn-outline-primary" to="/orders">
                        My Orders
                    </Link>
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                {loading ? (
                    <div className="text-center py-5">
                        <div className="spinner-border text-primary" role="status" />
                    </div>
                ) : refunds.length === 0 ? (
                    <div className="alert alert-light border">
                        You have not submitted any refund requests yet.
                    </div>
                ) : (
                    <div className="row g-4">
                        {refunds.map((refund) => (
                            <div className="col-12" key={refund.id}>
                                <article className="card border-0 shadow-sm">
                                    <div className="card-body">
                                        <div className="d-flex flex-wrap justify-content-between gap-3">
                                            <div>
                                                <h5 className="mb-1">
                                                    ORD{String(refund.order).padStart(3, "0")}
                                                </h5>
                                                <div className="text-muted">
                                                    Requested {formatDate(refund.requested_at)}
                                                </div>
                                            </div>
                                            <div className="text-end">
                                                <div className="fs-5 fw-semibold">
                                                    ৳{Number(refund.refund_amount).toFixed(2)}
                                                </div>
                                                <span className={`badge ${STATUS_STYLES[refund.status] || "bg-secondary"}`}>
                                                    {refund.status}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="row mt-4 g-3">
                                            <div className="col-md-6">
                                                <div className="small text-muted">Reason</div>
                                                <div className="fw-semibold">{refund.reason}</div>
                                                {refund.description && (
                                                    <div className="text-muted mt-1">{refund.description}</div>
                                                )}
                                            </div>
                                            <div className="col-md-6">
                                                <div className="small text-muted">Timeline</div>
                                                <div>Approved: {formatDate(refund.approved_at)}</div>
                                                <div>Completed: {formatDate(refund.completed_at)}</div>
                                            </div>
                                        </div>

                                        {refund.status === "Pending" && (
                                            <div className="alert alert-warning mt-4 mb-0">
                                                Your refund request is waiting for admin review.
                                            </div>
                                        )}
                                        {refund.status === "Approved" && (
                                            <div className="alert alert-info mt-4 mb-0">
                                                Your refund has been approved and is being processed.
                                            </div>
                                        )}
                                        {refund.status === "Rejected" && refund.admin_notes && (
                                            <div className="alert alert-danger mt-4 mb-0">
                                                <strong>Admin Note:</strong> {refund.admin_notes}
                                            </div>
                                        )}
                                        {refund.refund_failure_reason && (
                                            <div className="alert alert-warning mt-4 mb-0">
                                                Processing is taking longer than expected. We are retrying your refund.
                                            </div>
                                        )}
                                    </div>
                                </article>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
};

export default RefundRequests;