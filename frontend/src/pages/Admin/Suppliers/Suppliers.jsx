import DashboardLayout from "../../../layouts/DashboardLayout";

const Suppliers = () => {
    return (
        <DashboardLayout>

            <h2>Supplier Management</h2>

            <hr />

            {/* Add Supplier Button */}
            <button
                className="btn btn-primary mb-3"
            >
                Add Supplier
            </button>

            {/* Suppliers Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Supplier Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>ABC Bakery Ingredients Ltd.</td>
                        <td>abc@gmail.com</td>
                        <td>017XXXXXXXX</td>
                        <td>Active</td>
                        <td>
                            <button
                                className="btn btn-warning btn-sm me-2"
                            >
                                Edit
                            </button>

                            <button
                                className="btn btn-danger btn-sm"
                            >
                                Delete
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>2</td>
                        <td>Fresh Dairy Supplier</td>
                        <td>fresh@gmail.com</td>
                        <td>018XXXXXXXX</td>
                        <td>Active</td>
                        <td>
                            <button
                                className="btn btn-warning btn-sm me-2"
                            >
                                Edit
                            </button>

                            <button
                                className="btn btn-danger btn-sm"
                            >
                                Delete
                            </button>
                        </td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default Suppliers;