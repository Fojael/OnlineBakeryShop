import DashboardLayout from "../../../layouts/DashboardLayout";

const Customers = () => {
    return (
        <DashboardLayout>

            <h2>Customer Management</h2>

            <hr />

            {/* Customers Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>Customer ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>John Doe</td>
                        <td>john@gmail.com</td>
                        <td>017XXXXXXXX</td>
                        <td>Active</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-warning btn-sm"
                            >
                                Disable
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>2</td>
                        <td>Sarah Khan</td>
                        <td>sarah@gmail.com</td>
                        <td>018XXXXXXXX</td>
                        <td>Active</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-warning btn-sm"
                            >
                                Disable
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>3</td>
                        <td>Ahmed Ali</td>
                        <td>ahmed@gmail.com</td>
                        <td>019XXXXXXXX</td>
                        <td>Inactive</td>
                        <td>
                            <button
                                className="btn btn-primary btn-sm me-2"
                            >
                                View
                            </button>

                            <button
                                className="btn btn-success btn-sm"
                            >
                                Enable
                            </button>
                        </td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default Customers;