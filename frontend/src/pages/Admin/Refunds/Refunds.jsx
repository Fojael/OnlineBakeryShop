import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const REFUND_STATUSES = [
    "Approved",
    "Rejected",
    "Completed",
];

const Refunds = () => {
    const [refunds, setRefunds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updatingId, setUpdatingId] = useState(null);

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
        loadRefunds();
    }, []);

    const updateRefund = async (refundId, status) => {
        setUpdatingId(refundId);
        setError("");

        try {
            await api.patch(
                `orders/refunds/admin/${refundId}/update/`,
                { status }
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
                                    <th>Order</th>
                                    <th>Customer</th>
                                    <th>Reason</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="6">Loading refunds...</td>
                                    </tr>
                                ) : refunds.length === 0 ? (
                                    <tr>
                                        <td colSpan="6">No refund requests found.</td>
                                    </tr>
                                ) : (
                                    refunds.map((refund) => (
                                        <tr key={refund.id}>
                                            <td>#{refund.order}</td>
                                            <td>{refund.customer_email || "-"}</td>
                                            <td>{refund.reason}</td>
                                            <td>{refund.refund_amount}</td>
                                            <td>{refund.status}</td>
                                            <td>
                                                <select
                                                    className="form-select form-select-sm"
                                                    value={refund.status}
                                                    disabled={updatingId === refund.id}
                                                    onChange={(event) =>
                                                        updateRefund(
                                                            refund.id,
                                                            event.target.value
                                                        )
                                                    }
                                                >
                                                    <option value={refund.status}>
                                                        {refund.status}
                                                    </option>
                                                    {REFUND_STATUSES.filter(
                                                        (status) => status !== refund.status
                                                    ).map((status) => (
                                                        <option key={status} value={status}>
                                                            {status}
                                                        </option>
                                                    ))}
                                                </select>
                                            </td>
                                        </tr>
                                    ))
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
