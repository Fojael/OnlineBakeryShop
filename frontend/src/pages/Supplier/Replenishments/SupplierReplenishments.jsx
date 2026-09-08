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

const SupplierReplenishments = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);

    const loadRequests = async () => {
        try {
            setLoading(true);
            const response = await getReplenishmentRequests();
            const data = response?.data;
            setRequests(
                Array.isArray(data)
                    ? data
                    : data?.results || [],
            );
        } catch (error) {
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

    return (
        <div className="container-fluid py-4">
            <div className="mb-4">
                <h2>Replenishment Requests</h2>
                <p className="text-muted mb-0">
                    Process stock requests assigned to your supplier account.
                </p>
            </div>

            <div className="card shadow-sm">
                <div className="table-responsive">
                    <table className="table table-hover align-middle mb-0">
                        <thead className="table-light">
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Status</th>
                                <th>Notes</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {!loading && requests.length === 0 && (
                                <tr>
                                    <td colSpan="5" className="text-center py-4">
                                        No replenishment requests assigned to you.
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
                                        <td>
                                            <span className="badge bg-secondary">
                                                {request.status}
                                            </span>
                                        </td>
                                        <td>{request.notes || "-"}</td>
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
                                                    Inventory received
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
