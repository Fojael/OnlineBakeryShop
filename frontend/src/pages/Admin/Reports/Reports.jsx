import DashboardLayout from "../../../layouts/DashboardLayout";

const Reports = () => {
    return (
        <DashboardLayout>

            <h2>Reports</h2>

            <hr />

            {/* Reports Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>Report Name</th>
                        <th>Description</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>Daily Sales Report</td>
                        <td>View today's sales information.</td>
                        <td>
                            <button className="btn btn-primary btn-sm">
                                View
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>Monthly Sales Report</td>
                        <td>View monthly sales performance.</td>
                        <td>
                            <button className="btn btn-primary btn-sm">
                                View
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>Inventory Report</td>
                        <td>View available and low stock products.</td>
                        <td>
                            <button className="btn btn-primary btn-sm">
                                View
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>Customer Report</td>
                        <td>View customer activity and statistics.</td>
                        <td>
                            <button className="btn btn-primary btn-sm">
                                View
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>Order Report</td>
                        <td>View customer order details.</td>
                        <td>
                            <button className="btn btn-primary btn-sm">
                                View
                            </button>
                        </td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default Reports;