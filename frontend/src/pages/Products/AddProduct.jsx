import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { createProduct } from "../../services/productService";

const AddProduct = () => {
    const navigate = useNavigate();

    const [name, setName] = useState("");
    const [category, setCategory] = useState("Cake");
    const [description, setDescription] = useState("");
    const [price, setPrice] = useState("");
    const [stockQuantity, setStockQuantity] = useState("");
    const [isAvailable, setIsAvailable] = useState(true);
    const [featured, setFeatured] = useState(false);

    const [image, setImage] = useState(null);
    const [preview, setPreview] = useState(null);

    const [saving, setSaving] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validation
        if (
            !name ||
            !description ||
            !price ||
            !stockQuantity
        ) {
           toast.warning("Please fill all required fields.");
            return;
        }

        setSaving(true);

        try {
            const formData = new FormData();

            formData.append("name", name);
            formData.append("category", category);
            formData.append("description", description);
            formData.append("price", price);
            formData.append("stock_quantity", stockQuantity);
            formData.append("is_available", isAvailable);
            formData.append("featured", featured);

            if (image) {
                formData.append("image", image);
            }

            await createProduct(formData);

            // Later replace with toast.success(...)
            toast.success("Product added successfully!");
            navigate("/admin/products");
        } catch (error) {
            console.log(error);

            if (error.response?.data) {
                console.log(error.response.data);
            }

           toast.error("Failed to add product.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="container py-5">

            <div className="card shadow">

                <div className="card-header bg-success text-white">
                    <h3 className="mb-0">
                        Add New Product
                    </h3>
                </div>

                <div className="card-body">

                    <form onSubmit={handleSubmit}>

                        {/* Product Name */}

                        <div className="mb-3">
                            <label className="form-label">
                                Product Name
                            </label>

                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) =>
                                    setName(e.target.value)
                                }
                            />
                        </div>

                        {/* Category */}

                        <div className="mb-3">

                            <label className="form-label">
                                Category
                            </label>

                            <select
                                className="form-select"
                                value={category}
                                onChange={(e) =>
                                    setCategory(e.target.value)
                                }
                            >
                                <option value="Cake">Cake</option>
                                <option value="Bread">Bread</option>
                                <option value="Pastry">Pastry</option>
                                <option value="Cookies">Cookies</option>
                                <option value="Donut">Donut</option>
                                <option value="Cup Cake">Cup Cake</option>
                                <option value="Muffin">Muffin</option>
                                <option value="Brownie">Brownie</option>
                            </select>

                        </div>

                        {/* Description */}

                        <div className="mb-3">

                            <label className="form-label">
                                Description
                            </label>

                            <textarea
                                rows="4"
                                className="form-control"
                                value={description}
                                onChange={(e) =>
                                    setDescription(e.target.value)
                                }
                            />

                        </div>

                        {/* Price */}

                        <div className="mb-3">

                            <label className="form-label">
                                Price (৳)
                            </label>

                            <input
                                type="number"
                                className="form-control"
                                value={price}
                                onChange={(e) =>
                                    setPrice(e.target.value)
                                }
                            />

                        </div>

                        {/* Stock */}

                        <div className="mb-3">

                            <label className="form-label">
                                Stock Quantity
                            </label>

                            <input
                                type="number"
                                className="form-control"
                                value={stockQuantity}
                                onChange={(e) =>
                                    setStockQuantity(e.target.value)
                                }
                            />

                        </div>

                        {/* Image */}

                        <div className="mb-3">

                            <label className="form-label">
                                Product Image
                            </label>

                            <input
                                type="file"
                                accept="image/*"
                                className="form-control"
                                onChange={(e) => {

                                    const file =
                                        e.target.files[0];

                                    setImage(file);

                                    if (file) {
                                        setPreview(
                                            URL.createObjectURL(file)
                                        );
                                    }
                                }}
                            />

                            {preview && (

                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="img-thumbnail mt-3"
                                    width="220"
                                />

                            )}

                        </div>

                        {/* Checkboxes */}

                        <div className="form-check mb-2">

                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={isAvailable}
                                onChange={(e) =>
                                    setIsAvailable(
                                        e.target.checked
                                    )
                                }
                            />

                            <label className="form-check-label">
                                Available
                            </label>

                        </div>

                        <div className="form-check mb-4">

                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={featured}
                                onChange={(e) =>
                                    setFeatured(
                                        e.target.checked
                                    )
                                }
                            />

                            <label className="form-check-label">
                                Featured Product
                            </label>

                        </div>

                        {/* Buttons */}

                        <button
                            className="btn btn-success"
                            disabled={saving}
                        >
                            {saving
                                ? "Saving..."
                                : "Save Product"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-secondary ms-2"
                            onClick={() =>
                                navigate("/admin/products")
                            }
                        >
                            Cancel
                        </button>

                    </form>

                </div>

            </div>

        </div>
    );
};

export default AddProduct;