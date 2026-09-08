const formatDateTime = (value) => {
    if (!value) {
        return "Unknown time";
    }

    return new Date(value).toLocaleString();
};

const OrderStatusHistory = ({ history = [] }) => {
    return (
        <div className="card border-0 shadow-sm mt-4">
            <div className="card-header fw-bold">Order Status History</div>
            <div className="card-body">
                {history.length === 0 ? (
                    <p className="text-muted mb-0">No status history available.</p>
                ) : (
                    <div className="list-group list-group-flush">
                        {history.map((entry) => (
                            <div
                                className="list-group-item px-0"
                                key={entry.id}
                            >
                                <div className="d-flex justify-content-between gap-3">
                                    <strong>{entry.new_status}</strong>
                                    <small className="text-muted">
                                        {formatDateTime(entry.changed_at)}
                                    </small>
                                </div>
                                <div className="small text-muted">
                                    {entry.previous_status
                                        ? `${entry.previous_status} -> ${entry.new_status}`
                                        : "Initial order status"}
                                    {entry.changed_by_name
                                        ? ` | Changed by ${entry.changed_by_name}`
                                        : ""}
                                </div>
                                {entry.note && (
                                    <div className="small mt-1">{entry.note}</div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default OrderStatusHistory;
