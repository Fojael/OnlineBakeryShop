import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import {
    getCategories,
    deleteCategory,
} from "../../../services/categoryService";

const Categories = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchCategories = async () => {
        try {
            const response = await getCategories();
            setCategories(response.data);
        } catch (error) {
            console.log(error);
            toast.error("Failed to load categories.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        (async () => {
            await fetchCategories();
        })();
    }, []);

    const handleDelete = async (id) => {
        const confirmDelete = window.confirm(
            "Delete this category?"
        );

        if (!confirmDelete) return;

        try {
            await deleteCategory(id);

            toast.success(
                "Category deleted successfully."
            );

            fetchCategories();
        } catch (error) {
            console.log(error);
            toast.error(
                "Unable to delete category."
            );
        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div
                    className="spinner-border text-primary"
                    role="status"
                >
                    <span className="visually-hidden">
                        Loading...
                    </span>
                </div>

                <p className="mt-3">
                    Loading Categories...
                </p>
            </div>
        );
    }

    return (
        <div className="container py-4">

            <div className="d-flex justify-content-between align-items-center mb-4">

                <h2>Category Management</h2>

                <Link
                    to="/admin/categories/add"
                    className="btn btn-success"
                >
                    + Add Category
                </Link>

            </div>

            <div className="card shadow">

                <div className="card-body">

                    <div className="table-responsive">

                        <table className="table table-hover align-middle">

                            <thead className="table-dark">

                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Created</th>
                                    <th width="180">
                                        Actions
                                    </th>
                                </tr>

                            </thead>

                            <tbody>

                                {categories.length > 0 ? (

                                    categories.map((category) => (

                                        <tr key={category.id}>

                                            <td>
                                                {category.id}
                                            </td>

                                            <td>
                                                <strong>
                                                    {category.name}
                                                </strong>
                                            </td>

                                            <td>
                                                {category.description}
                                            </td>

                                            <td>
                                                {category.created_at
                                                    ? new Date(
                                                          category.created_at
                                                      ).toLocaleDateString()
                                                    : "-"}
                                            </td>

                                            <td>

                                                <Link
                                                    to={`/admin/categories/edit/${category.id}`}
                                                    className="btn btn-warning btn-sm me-2"
                                                >
                                                    Edit
                                                </Link>

                                                <button
                                                    className="btn btn-danger btn-sm"
                                                    onClick={() =>
                                                        handleDelete(
                                                            category.id
                                                        )
                                                    }
                                                >
                                                    Delete
                                                </button>

                                            </td>

                                        </tr>

                                    ))

                                ) : (

                                    <tr>

                                        <td
                                            colSpan="5"
                                            className="text-center py-4"
                                        >
                                            No Categories Found
                                        </td>

                                    </tr>

                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Categories;