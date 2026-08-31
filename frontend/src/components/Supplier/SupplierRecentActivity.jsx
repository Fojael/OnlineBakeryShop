const SupplierRecentActivity = ({
    activities = [],
}) => {

    return (

        <div className="card border-0 shadow-sm">

            <div className="card-body">

                <div className="d-flex justify-content-between align-items-center mb-4">

                    <h5 className="fw-bold mb-0">
                        Recent Activity
                    </h5>

                </div>


                {activities.length === 0 ? (

                    <div className="text-center py-4">

                        <p className="text-muted mb-0">
                            No recent activity.
                        </p>

                    </div>

                ) : (

                    <div className="list-group list-group-flush">

                        {activities.map(
                            (activity, index) => (

                                <div
                                    key={
                                        activity.id ||
                                        index
                                    }
                                    className="list-group-item px-0"
                                >

                                    <div className="d-flex justify-content-between">

                                        <div>

                                            <h6 className="mb-1">
                                                {
                                                    activity.title
                                                }
                                            </h6>

                                            <small className="text-muted">
                                                {
                                                    activity.description
                                                }
                                            </small>

                                        </div>


                                        <small className="text-muted">

                                            {
                                                activity.date
                                            }

                                        </small>

                                    </div>

                                </div>

                            )
                        )}

                    </div>

                )}

            </div>

        </div>

    );
};


export default SupplierRecentActivity;