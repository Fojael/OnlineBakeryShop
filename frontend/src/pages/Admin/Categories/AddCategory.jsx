import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { createCategory } from "../../../services/categoryService";

const AddCategory = () => {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: "",
        description: "",
    });

    const [saving, setSaving] = useState(false);

    const handleChange = useCallback((e) => {
        const { name, value } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    }, []);

    const handleSubmit = useCallback(
        async (e) => {
            e.preventDefault();

            if (saving) return;

            if (!formData.name.trim()) {
                toast.error("Category name is required.");
                return;
            }

            try {
                setSaving(true);

                await createCategory({
                    name: formData.name.trim(),
                    description: formData.description.trim(),
                });

                toast.success("Category added successfully.");

                navigate("/admin/categories");
            } catch (error) {
                console.error(error);

                toast.error(
                    error.response?.data?.message ||
                    error.response?.data?.detail ||
                    "Failed to add category."
                );
            } finally {
                setSaving(false);
            }
        },
        [formData, navigate, saving]
    );

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">

                <div className="row justify-content-center">

                    <div className="col-lg-8">

                        <div className="card shadow">

                            <div className="card-header bg-dark text-white">

                                <h3 className="mb-0">
                                    Add New Category
                                </h3>

                            </div>

                            <div className="card-body">

                                <form onSubmit={handleSubmit}>

                                    <div className="mb-3">

                                        <label className="form-label">
                                            Category Name
                                        </label>

                                        <input
                                            type="text"
                                            name="name"
                                            className="form-control"
                                            placeholder="Enter category name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            autoComplete="off"
                                            required
                                        />

                                    </div>

                                    <div className="mb-4">

                                        <label className="form-label">
                                            Description
                                        </label>

                                        <textarea
                                            rows="4"
                                            name="description"
                                            className="form-control"
                                            placeholder="Category description..."
                                            value={formData.description}
                                            onChange={handleChange}
                                        />

                                    </div>

                                    <div className="d-flex gap-2">

                                        <button
                                            type="submit"
                                            className="btn btn-success"
                                            disabled={saving}
                                        >
                                            {saving
                                                ? "Saving..."
                                                : "Save Category"}
                                        </button>

                                        <button
                                            type="button"
                                            className="btn btn-secondary"
                                            disabled={saving}
                                            onClick={() =>
                                                navigate("/admin/categories")
                                            }
                                        >
                                            Cancel
                                        </button>

                                    </div>

                                </form>

                            </div>

                        </div>

                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
};

export default AddCategory;