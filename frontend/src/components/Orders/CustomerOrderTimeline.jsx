const ORDER_STEPS = [
    "Pending",
    "Accepted",
    "Processing",
    "Ready",
    "Assigned",
    "Out for Delivery",
    "Delivered",
];

const formatDateTime = (value) => (
    value ? new Date(value).toLocaleString() : "Not reached yet"
);

const CustomerOrderTimeline = ({ order }) => {
    const historyByStatus = new Map(
        (order.history || []).map((entry) => [entry.new_status, entry])
    );
    const currentIndex = ORDER_STEPS.indexOf(order.status);
    const riderVisible = currentIndex >= ORDER_STEPS.indexOf("Assigned");

    return (
        <section className="card border-0 shadow-sm mt-4" aria-labelledby="tracking-title">
            <div className="card-body">
                <h5 id="tracking-title" className="mb-4">Delivery tracking</h5>
                <ol className="list-unstyled mb-0">
                    {ORDER_STEPS.map((step, index) => {
                        const historyEntry = historyByStatus.get(step);
                        const isCurrent = step === order.status;
                        const isComplete = index < currentIndex || Boolean(historyEntry && !isCurrent);
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
                                        <strong>{step}</strong>
                                        <small className="text-muted">
                                            {formatDateTime(historyEntry?.changed_at)}
                                        </small>
                                    </div>
                                    <div className="small text-muted">
                                        {isCurrent ? "Current step" : isComplete ? "Completed" : "Upcoming"}
                                    </div>
                                    {isCurrent && riderVisible && order.rider_name && (
                                        <div className="small mt-1">
                                            Rider: {order.rider_name}
                                        </div>
                                    )}
                                </div>
                            </li>
                        );
                    })}
                </ol>
            </div>
        </section>
    );
};

export default CustomerOrderTimeline;