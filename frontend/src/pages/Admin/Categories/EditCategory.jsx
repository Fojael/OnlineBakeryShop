import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getCategory,
    updateCategory,
} from "../../../services/categoryService";

const EditCategory = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        name: "",
        description: "",
    });

    useEffect(() => {
        const controller = new AbortController();

        (async () => {
            try {
                const response = await getCategory(id, {
                    signal: controller.signal,
                });

                setFormData({
                    name: response.data.name || "",
                    description: response.data.description || "",
                });
            } catch (error) {
                if (
                    error.name !== "CanceledError" &&
                    error.name !== "AbortError"
                ) {
                    console.error(error);

                    toast.error("Failed to load category.");

                    navigate("/admin/categories", {
                        replace: true,
                    });
                }
            } finally {
                setLoading(false);
            }
        })();

        return () => controller.abort();
    }, [id, navigate]);

    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.name.trim()) {
            toast.error("Category name is required.");
            return;
        }

        try {
            setSaving(true);

            await updateCategory(id, {
                name: formData.name.trim(),
                description: formData.description.trim(),
            });

            toast.success("Category updated successfully.");

            navigate("/admin/categories");
        } catch (error) {
            console.error(error);
            toast.error("Failed to update category.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="text-center py-5">
                    <div
                        className="spinner-border text-warning"
                        role="status"
                    >
                        <span className="visually-hidden">
                            Loading...
                        </span>
                    </div>

                    <h5 className="mt-3">
                        Loading Category...
                    </h5>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow">

                        <div className="card-header bg-warning">

                            <h3 className="mb-0">
                                Edit Category
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
                                        value={formData.name}
                                        onChange={handleChange}
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
                                        value={formData.description}
                                        onChange={handleChange}
                                    />

                                </div>

                                <div className="d-flex gap-2">

                                    <button
                                        type="submit"
                                        className="btn btn-warning"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Updating..."
                                            : "Update Category"}
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={() =>
                                            navigate(
                                                "/admin/categories"
                                            )
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
        </DashboardLayout>
    );
};

export default EditCategory;