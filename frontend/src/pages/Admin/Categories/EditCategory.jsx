import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import {
    getCategory,
    updateCategory,
} from "../../../services/categoryService";

const EditCategory = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    useEffect(() => {
        const loadCategory = async () => {
            try {
                const response = await getCategory(id);

                setName(response.data.name);
                setDescription(response.data.description || "");
            } catch (error) {
                console.log(error);

                toast.error("Failed to load category.");

                navigate("/admin/categories");
            } finally {
                setLoading(false);
            }
        };

        loadCategory();
    }, [id, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!name.trim()) {
            toast.error("Category name is required.");
            return;
        }

        try {
            setSaving(true);

            await updateCategory(id, {
                name,
                description,
            });

            toast.success("Category updated successfully.");

            navigate("/admin/categories");

        } catch (error) {

            console.log(error);

            toast.error("Failed to update category.");

        } finally {

            setSaving(false);

        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <h4>Loading Category...</h4>
            </div>
        );
    }

    return (
        <div className="container py-4">

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
                                        className="form-control"
                                        value={name}
                                        onChange={(e) =>
                                            setName(e.target.value)
                                        }
                                        required
                                    />

                                </div>

                                <div className="mb-4">

                                    <label className="form-label">
                                        Description
                                    </label>

                                    <textarea
                                        rows="4"
                                        className="form-control"
                                        value={description}
                                        onChange={(e) =>
                                            setDescription(
                                                e.target.value
                                            )
                                        }
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

        </div>
    );
};

export default EditCategory;