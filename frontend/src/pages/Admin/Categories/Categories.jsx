import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getCategories,
    deleteCategory,
} from "../../../services/categoryService";

const Categories = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    // Initial Load
    useEffect(() => {
        let ignore = false;

        async function loadCategories() {
            try {
                const response = await getCategories();

                if (!ignore) {
                    setCategories(response.data || []);
                }
            } catch (error) {
                console.error(error);

                if (!ignore) {
                    toast.error("Failed to load categories.");
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        }

        loadCategories();

        return () => {
            ignore = true;
        };
    }, []);

    // Reload list after delete
    const reloadCategories = async () => {
        try {
            const response = await getCategories();
            setCategories(response.data || []);
        } catch (error) {
            console.error(error);
            toast.error("Failed to refresh categories.");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this category?")) {
            return;
        }

        try {
            await deleteCategory(id);

            toast.success("Category deleted successfully.");

            await reloadCategories();
        } catch (error) {
            console.error(error);
            toast.error("Unable to delete category.");
        }
    };

    return (
        <DashboardLayout>
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

                {loading ? (
                    <div className="text-center py-5">
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
                ) : (
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
                                            <th width="180">Actions</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {categories.length > 0 ? (
                                            categories.map((category) => (
                                                <tr key={category.id}>
                                                    <td>{category.id}</td>

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
                )}
            </div>
        </DashboardLayout>
    );
};

export default Categories;