import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import { createCategory } from "../../../services/categoryService";

const AddCategory = () => {
    const navigate = useNavigate();

    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    const [saving, setSaving] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!name.trim()) {
            toast.error("Category name is required.");
            return;
        }

        try {
            setSaving(true);

            await createCategory({
                name,
                description,
            });

            toast.success("Category added successfully.");

            navigate("/admin/categories");

        } catch (error) {

            console.log(error);

            if (error.response?.data) {
                toast.error("Failed to add category.");
            } else {
                toast.error("Server connection failed.");
            }

        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="container py-4">

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

                                {/* Category Name */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Category Name
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Enter category name"
                                        value={name}
                                        onChange={(e) =>
                                            setName(e.target.value)
                                        }
                                        required
                                    />

                                </div>

                                {/* Description */}

                                <div className="mb-4">

                                    <label className="form-label">
                                        Description
                                    </label>

                                    <textarea
                                        rows="4"
                                        className="form-control"
                                        placeholder="Category description..."
                                        value={description}
                                        onChange={(e) =>
                                            setDescription(
                                                e.target.value
                                            )
                                        }
                                    />

                                </div>

                                {/* Buttons */}

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

        </div>
    );
};

export default AddCategory;