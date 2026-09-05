import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const Payments = () => {
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const updateStatus = async (paymentId, status) => {
        try {
            await api.patch(
                `payments/admin/${paymentId}/status/`,
                { status }
            );

            setPayments((currentPayments) =>
                currentPayments.map((payment) =>
                    payment.id === paymentId
                        ? {
                            ...payment,
                            status,
                            display_status: status === "Success"
                                ? "Paid"
                                : status,
                        }
                        : payment
                )
            );
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Failed to update payment status."
            );
        }
    };

    useEffect(() => {
        let ignore = false;

        const loadPayments = async () => {
            try {
                const response = await api.get("payments/admin/");
                if (!ignore) {
                    setPayments(response.data?.results || []);
                }
            } catch (requestError) {
                if (!ignore) {
                    setError(
                        requestError.response?.data?.detail ||
                        "Failed to load payments."
                    );
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadPayments();

        return () => {
            ignore = true;
        };
    }, []);

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Payments</h2>
                <p className="text-muted mb-4">
                    Review payment records and gateway status.
                </p>

                {error && <div className="alert alert-danger">{error}</div>}

                <div className="card border-0 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Payment ID</th>
                                    <th>Order ID</th>
                                    <th>Customer</th>
                                    <th>Amount</th>
                                    <th>Method</th>
                                    <th>Transaction ID</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="8">Loading payments...</td>
                                    </tr>
                                ) : payments.length === 0 ? (
                                    <tr>
                                        <td colSpan="8">No payment records found.</td>
                                    </tr>
                                ) : (
                                    payments.map((payment) => (
                                        <tr key={payment.id}>
                                            <td>#{payment.id}</td>
                                            <td>#{payment.order_id}</td>
                                            <td>{payment.customer_name || payment.customer_email || "-"}</td>
                                            <td>{payment.amount} {payment.currency}</td>
                                            <td>{payment.payment_method || "-"}</td>
                                            <td>{payment.transaction_id || "-"}</td>
                                            <td>
                                                <select
                                                    className="form-select form-select-sm"
                                                    value={payment.status}
                                                    onChange={(event) =>
                                                        updateStatus(
                                                            payment.id,
                                                            event.target.value
                                                        )
                                                    }
                                                >
                                                    <option value="Pending">Pending</option>
                                                    <option value="Success">Paid</option>
                                                    <option value="Failed">Failed</option>
                                                    <option value="Cancelled">Cancelled</option>
                                                    <option value="Refunded">Refunded</option>
                                                </select>
                                            </td>
                                            <td>{new Date(payment.created_at).toLocaleString()}</td>
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

export default Payments;
