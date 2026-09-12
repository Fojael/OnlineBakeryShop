const TIMELINE_STEPS = [
    {
        key: "placed",
        label: "Order Placed",
        description: "Your order has been received.",
        historyStatus: "Pending",
    },
    {
        key: "accepted",
        label: "Accepted",
        description: "The bakery has accepted your order.",
        historyStatus: "Accepted",
    },
    {
        key: "ready",
        label: "Ready",
        description: "Your order is ready for delivery assignment.",
        historyStatus: "Ready",
    },
    {
        key: "assigned",
        label: "Rider Assigned",
        description: "A delivery rider has been assigned.",
        timestamp: "assigned_at",
    },
    {
        key: "out_for_delivery",
        label: "Out for Delivery",
        description: "Your order is on its way.",
        timestamp: "out_for_delivery_at",
        deliveryStatus: "OUT_FOR_DELIVERY",
    },
    {
        key: "delivered",
        label: "Delivered",
        description: "Your order has been delivered.",
        historyStatus: "Delivered",
        timestamp: "delivered_at",
    },
];

const formatDateTime = (value) => (
    value ? new Date(value).toLocaleString() : "Not reached yet"
);

const CustomerOrderTimeline = ({ order }) => {
    const historyByStatus = (order.history || []).reduce((entries, entry) => {
        entries.set(entry.new_status, entry);
        return entries;
    }, new Map());
    const deliveryTimestamps = order.delivery_timestamps || {};
    const completedSteps = TIMELINE_STEPS.map((step) => {
        const historyEntry = step.historyStatus
            ? historyByStatus.get(step.historyStatus)
            : null;
        const timestamp = step.key === "placed"
            ? order.created_at
            : step.timestamp
            ? deliveryTimestamps[step.timestamp]
            : historyEntry?.changed_at;
        const isCompleted = Boolean(timestamp);

        return {
            ...step,
            historyEntry,
            timestamp,
            isCompleted,
        };
    });
    const currentIndex = completedSteps.reduce(
        (lastIndex, step, index) => (step.isCompleted ? index : lastIndex),
        -1,
    );
    const currentDeliveryStatus = order.delivery_status;
    const currentStepIndex = completedSteps.findIndex(
        (step) => step.deliveryStatus === currentDeliveryStatus,
    );
    const activeIndex = currentStepIndex >= 0 ? currentStepIndex : currentIndex;

    return (
        <section className="card border-0 shadow-sm mt-4" aria-labelledby="tracking-title">
            <div className="card-body">
                <h5 id="tracking-title" className="mb-1">Order tracking</h5>
                <p className="text-muted small mb-4">
                    Progress is updated from the bakery and delivery service.
                </p>
                <ol className="list-unstyled mb-0">
                    {completedSteps.map((step, index) => {
                        const isCurrent = index === activeIndex;
                        const isComplete = step.isCompleted;
                        const stateClass = isCurrent
                            ? "border-primary bg-primary-subtle"
                            : isComplete
                                ? "border-success bg-success-subtle"
                                : "border-light bg-light";

                        return (
                            <li className="d-flex gap-3 mb-3" key={step}>
                                <div
                                    className={`border rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 ${stateClass}`}
                                    style={{ width: "2rem", height: "2rem" }}
                                    aria-label={isCurrent ? "Current step" : isComplete ? "Completed step" : "Upcoming step"}
                                >
                                    {isComplete ? "✓" : index + 1}
                                </div>
                                <div className="flex-grow-1">
                                    <div className="d-flex flex-wrap justify-content-between gap-2">
                                        <strong>{step.label}</strong>
                                        <small className="text-muted">
                                            {isComplete ? formatDateTime(step.timestamp) : "Not reached yet"}
                                        </small>
                                    </div>
                                    <div className="small text-muted">
                                        {isCurrent ? "Current step" : isComplete ? "Completed" : "Upcoming"}
                                    </div>
                                    <div className="small mt-1">{step.description}</div>
                                    {isCurrent && order.rider_name && index >= 4 && (
                                        <div className="small mt-1">
                                            Rider: {order.rider_name}
                                        </div>
                                    )}
                                </div>
                            </li>
                        );
                    })}
                </ol>
                {order.status === "Cancelled" && (
                    <div className="alert alert-danger mt-3 mb-0">
                        This order was cancelled. No further delivery steps will be completed.
                    </div>
                )}
            </div>
        </section>
    );
};

export default CustomerOrderTimeline;