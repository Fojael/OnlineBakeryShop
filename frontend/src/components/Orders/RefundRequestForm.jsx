import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import {
    requestRefund,
    uploadRefundPhotos,
} from "../../services/refundService";

const REFUND_REASONS = [
    "Wrong Product",
    "Damaged Product",
    "Expired Product",
    "Missing Item",
    "Poor Quality",
    "Other",
];

const RefundRequestForm = ({ orderId, order, onSubmitted }) => {
    const [reason, setReason] = useState("");
    const [description, setDescription] = useState("");
    const [selectedItems, setSelectedItems] = useState({});
    const [photos, setPhotos] = useState([]);
    const [pendingRefundId, setPendingRefundId] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const photoPreviews = useMemo(
        () => photos.map((photo) => URL.createObjectURL(photo)),
        [photos],
    );

    useEffect(() => () => {
        photoPreviews.forEach((preview) => URL.revokeObjectURL(preview));
    }, [photoPreviews]);

    const submitRequest = async (event) => {
        event.preventDefault();

        const items = Object.entries(selectedItems)
            .filter(([, quantity]) => Number(quantity) > 0)
            .map(([orderItemId, quantity]) => ({
                order_item_id: Number(orderItemId),
                quantity: Number(quantity),
            }));

        if (items.length === 0) {
            toast.error("Select at least one product and quantity.");
            return;
        }

        setSubmitting(true);

        try {
            let refundId = pendingRefundId;

            if (!refundId) {
                const response = await requestRefund(orderId, {
                    reason,
                    description,
                    items,
                });
                refundId = response.data.refund.id;
                setPendingRefundId(refundId);
            }

            if (photos.length > 0) {
                await uploadRefundPhotos(refundId, photos);
            }

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
            <div className="mb-2">
                <span className="form-label d-block">Products and quantities</span>
                {(order?.items || []).map((item) => (
                    <div className="input-group mb-2" key={item.id}>
                        <span className="input-group-text flex-grow-1">
                            {item.product_name} (max {item.quantity})
                        </span>
                        <input
                            className="form-control"
                            type="number"
                            min="0"
                            max={item.quantity}
                            value={selectedItems[item.id] || ""}
                            onChange={(event) => setSelectedItems({
                                ...selectedItems,
                                [item.id]: event.target.value,
                            })}
                        />
                    </div>
                ))}
            </div>
            <label className="form-label" htmlFor={`refund-photos-${orderId}`}>
                Product photos (up to 5)
            </label>
            <input
                id={`refund-photos-${orderId}`}
                className="form-control mb-2"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                multiple
                onChange={(event) => {
                    const selectedPhotos = Array.from(event.target.files || []);
                    if (selectedPhotos.length > 5) {
                        toast.error("You can upload up to 5 photos.");
                        event.target.value = "";
                        return;
                    }
                    setPhotos(selectedPhotos);
                    event.target.value = "";
                }}
            />
            {photos.length > 0 && (
                <div className="d-flex flex-wrap gap-2 mb-2">
                    {photos.map((photo, index) => (
                        <div className="position-relative" key={`${photo.name}-${index}`}>
                            <img
                                src={photoPreviews[index]}
                                alt={photo.name}
                                width="72"
                                height="72"
                                className="rounded border object-fit-cover"
                            />
                            <button
                                type="button"
                                className="btn btn-sm btn-dark position-absolute top-0 end-0"
                                aria-label={`Remove ${photo.name}`}
                                onClick={() => setPhotos(
                                    photos.filter((_, photoIndex) => photoIndex !== index),
                                )}
                            >
                                x
                            </button>
                        </div>
                    ))}
                </div>
            )}
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
