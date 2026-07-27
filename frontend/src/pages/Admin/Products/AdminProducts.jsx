import DashboardLayout from "../../../layouts/DashboardLayout";

const AdminProducts = () => {
    return (
        <DashboardLayout>
            <h2>Manage Products</h2>

            <hr />

            <button
                className="btn btn-primary mb-3"
            >
                Add Product
            </button>

            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Image</th>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>Image</td>
                        <td>Chocolate Cake</td>
                        <td>Cakes</td>
                        <td>৳650</td>
                        <td>25</td>
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
                        <td>Image</td>
                        <td>Cup Cake</td>
                        <td>Cup Cakes</td>
                        <td>৳120</td>
                        <td>40</td>
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

export default AdminProducts;