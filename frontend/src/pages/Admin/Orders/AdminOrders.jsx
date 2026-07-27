import DashboardLayout from "../../../layouts/DashboardLayout";

const AdminOrders = () => {
    return (
        <DashboardLayout>

            <h2>Order Management</h2>

            <hr />

            {/* Orders Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Customer Name</th>
                        <th>Total Amount</th>
                        <th>Payment Status</th>
                        <th>Order Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>#1001</td>
                        <td>John Doe</td>
                        <td>৳850</td>
                        <td>Paid</td>
                        <td>Delivered</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-warning btn-sm"
                            >
                                Update
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>#1002</td>
                        <td>Sarah Khan</td>
                        <td>৳450</td>
                        <td>Pending</td>
                        <td>Processing</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-warning btn-sm"
                            >
                                Update
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>#1003</td>
                        <td>Ahmed Ali</td>
                        <td>৳1200</td>
                        <td>Paid</td>
                        <td>Pending</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-warning btn-sm"
                            >
                                Update
                            </button>
                        </td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default AdminOrders;