import DashboardLayout from "../../../layouts/DashboardLayout";

const Inventory = () => {
    return (
        <DashboardLayout>

            <h2>Inventory Management</h2>

            <hr />

            {/* Update Stock Button */}
            <button
                className="btn btn-primary mb-3"
            >
                Update Inventory
            </button>

            {/* Inventory Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Available Stock</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>Chocolate Cake</td>
                        <td>25</td>
                        <td>In Stock</td>
                        <td>
                            <button
                                className="btn btn-warning btn-sm me-2"
                            >
                                Update
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>2</td>
                        <td>Cup Cake</td>
                        <td>5</td>
                        <td>Low Stock</td>
                        <td>
                            <button
                                className="btn btn-warning btn-sm me-2"
                            >
                                Update
                            </button>
                        </td>
                    </tr>

                    <tr>
                        <td>3</td>
                        <td>Bread</td>
                        <td>0</td>
                        <td>Out of Stock</td>
                        <td>
                            <button
                                className="btn btn-warning btn-sm me-2"
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

export default Inventory;