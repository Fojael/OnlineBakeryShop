import DashboardLayout from "../../../layouts/DashboardLayout";

const Categories = () => {
    return (
        <DashboardLayout>

            <h2>Manage Categories</h2>

            <hr />

            {/* Add Category Button */}
            <button
                className="btn btn-primary mb-3"
            >
                Add Category
            </button>

            {/* Categories Table */}
            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Category Name</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>Cakes</td>
                        <td>All bakery cakes.</td>
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
                        <td>Pastries</td>
                        <td>Fresh pastries.</td>
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

export default Categories;