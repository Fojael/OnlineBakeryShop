import { useState } from "react";
import { toast } from "react-toastify";

import { requestRefund } from "../../services/refundService";

const REFUND_REASONS = [
    "Wrong Product",
    "Damaged Product",
    "Expired Product",
    "Missing Item",
    "Poor Quality",
    "Other",
];

const RefundRequestForm = ({ orderId, onSubmitted }) => {
    const [reason, setReason] = useState("");
    const [description, setDescription] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const submitRequest = async (event) => {
        event.preventDefault();
        setSubmitting(true);

        try {
            await requestRefund(orderId, { reason, description });
            toast.success("Refund request submitted.");
            onSubmitted();
        } catch (error) {
            toast.error(
                error.response?.data?.detail ||
                "Unable to submit refund request."
            );
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form className="border rounded p-3 mt-3" onSubmit={submitRequest}>
            <h6>Request Refund</h6>
            <label className="form-label" htmlFor={`refund-reason-${orderId}`}>
                Reason
            </label>
            <select
                id={`refund-reason-${orderId}`}
                className="form-select mb-2"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                required
            >
                <option value="">Select a reason</option>
                {REFUND_REASONS.map((option) => (
                    <option key={option} value={option}>{option}</option>
                ))}
            </select>
            <textarea
                className="form-control mb-2"
                placeholder="Additional details (optional)"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                rows="3"
            />
            <button className="btn btn-warning" type="submit" disabled={submitting}>
                {submitting ? "Submitting..." : "Submit Refund Request"}
            </button>
        </form>
    );
};

export default RefundRequestForm;
