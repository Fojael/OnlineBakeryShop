import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import {
    getReplenishmentRequests,
    updateReplenishmentStatus,
} from "../../../services/replenishmentService";

const nextStatus = {
    PENDING: "PROCESSING",
    PROCESSING: "READY",
    READY: "DELIVERED",
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

const SupplierReplenishments = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);
    const [error, setError] = useState("");

    const loadRequests = async () => {
        try {
            setLoading(true);
            setError("");
            const response = await getReplenishmentRequests();
            const data = response?.data;
            setRequests(
                Array.isArray(data)
                    ? data
                    : data?.results || [],
            );
        } catch (error) {
            setError(
                error?.response?.data?.detail ||
                "Failed to load replenishment requests."
            );
            toast.error(
                error?.response?.data?.detail ||
                "Failed to load replenishment requests.",
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            void loadRequests();
        }, 0);

        return () => clearTimeout(timer);
    }, []);

    const handleStatusUpdate = async (requestId, status) => {
        try {
            setUpdatingId(requestId);
            await updateReplenishmentStatus(requestId, status);
            toast.success("Replenishment status updated.");
            await loadRequests();
        } catch (error) {
            toast.error(
                error?.response?.data?.detail ||
                "Failed to update replenishment status.",
            );
        } finally {
            setUpdatingId(null);
        }
    };

    const requestCounts = Object.keys(statusLabels).reduce(
        (counts, status) => {
            counts[status] = requests.filter(
                (request) => request.status === status
            ).length;
            return counts;
        },
        {},
    );

    return (
        <div className="container-fluid py-4">
            <div className="mb-4">
                <h2>Replenishment Requests</h2>
                <p className="text-muted mb-0">
                    Process stock requests assigned to your supplier account.
                </p>
            </div>

            {error && (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}

            <div className="row g-3 mb-4">
                {Object.entries(statusLabels).map(([status, label]) => (
                    <div className="col-6 col-xl-3" key={status}>
                        <div className="card h-100 shadow-sm">
                            <div className="card-body">
                                <div className="small text-muted">{label}</div>
                                <div className="fs-3 fw-bold">
                                    {requestCounts[status] || 0}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="card shadow-sm">
                <div className="table-responsive">
                    <table className="table table-hover align-middle mb-0">
                        <thead className="table-light">
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Request date</th>
                                <th>Status</th>
                                <th>Delivered date</th>
                                <th>Notes</th>
                                <th>History</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {!loading && requests.length === 0 && (
                                <tr>
                                        <td colSpan="8" className="text-center py-4">
                                        No replenishment requests assigned to you.
                                    </td>
                                </tr>
                            )}
                                {loading && (
                                    <tr>
                                        <td colSpan="8" className="text-center py-4">
                                            Loading replenishment requests...
                                        </td>
                                    </tr>
                                )}
                            {requests.map((request) => {
                                const status = nextStatus[request.status];
                                const isUpdating = updatingId === request.id;

                                return (
                                    <tr key={request.id}>
                                        <td>{request.product_name}</td>
                                        <td>{request.requested_quantity}</td>
                                        <td>{formatDate(request.created_at)}</td>
                                        <td>
                                            <span className="badge bg-secondary">
                                                {statusLabels[request.status] || request.status}
                                            </span>
                                        </td>
                                        <td>{formatDate(request.delivered_at)}</td>
                                        <td>{request.notes || "-"}</td>
                                        <td>
                                            {request.history?.length ? (
                                                <details>
                                                    <summary>
                                                        {request.history.length} event{request.history.length === 1 ? "" : "s"}
                                                    </summary>
                                                    <ul className="small text-muted ps-3 mb-0 mt-2">
                                                        {request.history.map((entry) => (
                                                            <li key={entry.id}>
                                                                {statusLabels[entry.new_status] || entry.new_status}
                                                                {" - "}
                                                                {formatDate(entry.changed_at)}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </details>
                                            ) : (
                                                <span className="text-muted">No history</span>
                                            )}
                                        </td>
                                        <td>
                                            {status ? (
                                                <button
                                                    type="button"
                                                    className="btn btn-primary btn-sm"
                                                    disabled={isUpdating}
                                                    onClick={() =>
                                                        handleStatusUpdate(
                                                            request.id,
                                                            status,
                                                        )
                                                    }
                                                >
                                                    {isUpdating
                                                        ? "Updating..."
                                                        : `Mark ${status}`}
                                                </button>
                                            ) : (
                                                <span className="text-muted">
                                                    Delivered
                                                </span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default SupplierReplenishments;
