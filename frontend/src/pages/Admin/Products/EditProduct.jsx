import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import {
    getProduct,
    updateProduct,
} from "../../../services/productService";

const EditProduct = () => {

    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [name, setName] = useState("");
    const [category, setCategory] = useState("Cake");
    const [description, setDescription] = useState("");
    const [price, setPrice] = useState("");
    const [stockQuantity, setStockQuantity] = useState("");
    const [isAvailable, setIsAvailable] = useState(true);
    const [featured, setFeatured] = useState(false);

    const [image, setImage] = useState(null);
    const [preview, setPreview] = useState("");

    useEffect(() => {
        const loadProduct = async () => {
            try {
                const response = await getProduct(id);

                const product = response.data;

                setName(product.name);
                setCategory(product.category);
                setDescription(product.description);
                setPrice(product.price);
                setStockQuantity(product.stock_quantity);
                setIsAvailable(product.is_available);
                setFeatured(product.featured);

                setPreview(product.image);
            } catch (error) {
                console.error(error);
                toast.error("Failed to load product.");
            } finally {
                setLoading(false);
            }
        };

        loadProduct();
    }, [id]);

    const handleSubmit = async (e) => {

        e.preventDefault();

        if (
            !name ||
            !description ||
            !price ||
            !stockQuantity
        ) {
            toast.warning("Please fill all required fields.");
            return;
        }

        try {

            setSaving(true);

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

            await updateProduct(id, formData);

            toast.success("Product Updated Successfully");

            navigate("/admin/products");

        } catch (error) {

            console.error(error);
            toast.error("Update failed.");

        } finally {

            setSaving(false);

        }

    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <h3>Loading...</h3>
            </div>
        );
    }

    return (

        <div className="container py-4">

            <h2 className="mb-4">
                Edit Product
            </h2>

            <form onSubmit={handleSubmit}>

                <div className="mb-3">

                    <label>Name</label>

                    <input
                        className="form-control"
                        value={name}
                        onChange={(e)=>setName(e.target.value)}
                    />

                </div>

                <div className="mb-3">

                    <label>Category</label>

                    <select
                        className="form-select"
                        value={category}
                        onChange={(e)=>setCategory(e.target.value)}
                    >

                        <option>Cake</option>
                        <option>Bread</option>
                        <option>Pastry</option>
                        <option>Cookies</option>
                        <option>Donut</option>
                        <option>Cup Cake</option>
                        <option>Muffin</option>
                        <option>Brownie</option>

                    </select>

                </div>

                <div className="mb-3">

                    <label>Description</label>

                    <textarea
                        rows="4"
                        className="form-control"
                        value={description}
                        onChange={(e)=>setDescription(e.target.value)}
                    />

                </div>

                <div className="row">

                    <div className="col-md-6 mb-3">

                        <label>Price</label>

                        <input
                            type="number"
                            className="form-control"
                            value={price}
                            onChange={(e)=>setPrice(e.target.value)}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Stock Quantity</label>

                        <input
                            type="number"
                            className="form-control"
                            value={stockQuantity}
                            onChange={(e)=>setStockQuantity(e.target.value)}
                        />

                    </div>

                </div>

                <div className="form-check mb-3">

                    <input
                        type="checkbox"
                        className="form-check-input"
                        checked={isAvailable}
                        onChange={(e)=>setIsAvailable(e.target.checked)}
                    />

                    <label className="form-check-label">
                        Available
                    </label>

                </div>

                <div className="form-check mb-3">

                    <input
                        type="checkbox"
                        className="form-check-input"
                        checked={featured}
                        onChange={(e)=>setFeatured(e.target.checked)}
                    />

                    <label className="form-check-label">
                        Featured Product
                    </label>

                </div>

                <div className="mb-3">

                    <label>Product Image</label>

                    <input
                        type="file"
                        className="form-control"
                        accept="image/*"
                        onChange={(e)=>{

                            const file=e.target.files[0];

                            setImage(file);

                            if(file){
                                setPreview(
                                    URL.createObjectURL(file)
                                );
                            }

                        }}
                    />

                </div>

                {preview && (

                    <img
                        src={preview}
                        alt="Preview"
                        className="img-thumbnail mb-4"
                        width="220"
                    />

                )}

                <div>

                    <button
                        className="btn btn-primary"
                        disabled={saving}
                    >
                        {saving
                            ? "Updating..."
                            : "Update Product"}
                    </button>

                    <button
                        type="button"
                        className="btn btn-secondary ms-2"
                        onClick={()=>
                            navigate("/admin/products")
                        }
                    >
                        Cancel
                    </button>

                </div>

            </form>

        </div>

    );

};

export default EditProduct;