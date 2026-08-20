import {
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import DashboardLayout from "../../layouts/DashboardLayout";
import { createProduct } from "../../services/productService";


const AddProduct = () => {

    const navigate = useNavigate();


    // =========================================================
    // CATEGORY CHOICES
    // =========================================================

    const categories = [
        "Cake",
        "Bread",
        "Pastry",
        "Cookies",
        "Donut",
        "Cup Cake",
        "Muffin",
        "Brownie",
    ];


    // =========================================================
    // FORM DATA
    // =========================================================

    const [formData, setFormData] = useState({
        name: "",
        category: "",
        description: "",
        price: "",
        stock_quantity: "",
        is_available: true,
        featured: false,
    });


    // =========================================================
    // IMAGE
    // =========================================================

    const [image, setImage] = useState(null);


    // =========================================================
    // SAVING
    // =========================================================

    const [saving, setSaving] = useState(false);


    // =========================================================
    // HANDLE INPUT
    // =========================================================

    const handleChange = (event) => {

        const {
            name,
            value,
            type,
            checked,
        } = event.target;


        setFormData((previous) => ({

            ...previous,

            [name]:
                type === "checkbox"
                    ? checked
                    : value,

        }));

    };


    // =========================================================
    // HANDLE IMAGE
    // =========================================================

    const handleImageChange = (event) => {

        const file =
            event.target.files?.[0] || null;


        setImage(file);

    };


    // =========================================================
    // SUBMIT
    // =========================================================

    const handleSubmit = async (event) => {

        event.preventDefault();


        // =====================================================
        // CLEAN DATA
        // =====================================================

        const productName =
            formData.name.trim();


        const description =
            formData.description.trim();


        const price =
            Number(formData.price);


        const stockQuantity =
            Number(formData.stock_quantity);


        // =====================================================
        // VALIDATION
        // =====================================================

        if (!productName) {

            toast.warning(
                "Product name is required."
            );

            return;
        }


        if (!formData.category) {

            toast.warning(
                "Please select a category."
            );

            return;
        }


        if (!description) {

            toast.warning(
                "Product description is required."
            );

            return;
        }


        if (
            formData.price === "" ||
            Number.isNaN(price) ||
            price <= 0
        ) {

            toast.warning(
                "Please enter a valid product price."
            );

            return;
        }


        if (
            formData.stock_quantity === "" ||
            Number.isNaN(stockQuantity) ||
            stockQuantity < 0
        ) {

            toast.warning(
                "Please enter a valid stock quantity."
            );

            return;
        }


        // =====================================================
        // FORM DATA
        // =====================================================

        const productData =
            new FormData();


        productData.append(
            "name",
            productName
        );


        productData.append(
            "category",
            formData.category
        );


        productData.append(
            "description",
            description
        );


        productData.append(
            "price",
            price.toString()
        );


        productData.append(
            "stock_quantity",
            stockQuantity.toString()
        );


        productData.append(
            "is_available",
            formData.is_available
                ? "true"
                : "false"
        );


        productData.append(
            "featured",
            formData.featured
                ? "true"
                : "false"
        );


        // =====================================================
        // IMAGE
        // =====================================================

        if (image) {

            productData.append(
                "image",
                image
            );

        }


        // =====================================================
        // SEND
        // =====================================================

        try {

            setSaving(true);


            const response =
                await createProduct(
                    productData
                );


            console.log(
                "Created product:",
                response.data
            );


            toast.success(
                "Product added successfully."
            );


            navigate(
                "/admin/products"
            );


        } catch (error) {

            console.error(
                "Failed to create product:",
                error
            );


            console.error(
                "Response:",
                error?.response?.data
            );


            const responseData =
                error?.response?.data;


            // =================================================
            // DJANGO VALIDATION ERRORS
            // =================================================

            if (
                responseData &&
                typeof responseData === "object"
            ) {

                const messages = [];


                Object.entries(
                    responseData
                ).forEach(
                    ([field, errors]) => {

                        if (
                            Array.isArray(errors)
                        ) {

                            errors.forEach(
                                (message) => {

                                    messages.push(
                                        `${field}: ${message}`
                                    );

                                }
                            );

                        } else {

                            messages.push(
                                `${field}: ${errors}`
                            );

                        }

                    }
                );


                if (
                    messages.length > 0
                ) {

                    messages.forEach(
                        (message) => {

                            toast.error(
                                message
                            );

                        }
                    );

                } else {

                    toast.error(
                        "Failed to add product."
                    );

                }

            } else {

                toast.error(
                    "Failed to add product."
                );

            }

        } finally {

            setSaving(false);

        }

    };


    // =========================================================
    // PAGE
    // =========================================================

    return (

        <DashboardLayout>

            <div className="container-fluid py-4">

                <div className="card shadow">


                    {/* HEADER */}

                    <div className="card-header bg-success text-white">

                        <h2 className="mb-0">
                            Add New Product
                        </h2>

                    </div>


                    {/* FORM */}

                    <div className="card-body">

                        <form
                            onSubmit={handleSubmit}
                        >


                            {/* PRODUCT NAME */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-name"
                                    className="form-label fw-semibold"
                                >
                                    Product Name
                                </label>


                                <input
                                    id="product-name"
                                    type="text"
                                    name="name"
                                    className="form-control"
                                    value={
                                        formData.name
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter product name"
                                    required
                                />

                            </div>


                            {/* CATEGORY */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-category"
                                    className="form-label fw-semibold"
                                >
                                    Category
                                </label>


                                <select
                                    id="product-category"
                                    name="category"
                                    className="form-select"
                                    value={
                                        formData.category
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    required
                                >

                                    <option value="">
                                        Select Category
                                    </option>


                                    {categories.map(
                                        (category) => (

                                            <option
                                                key={
                                                    category
                                                }
                                                value={
                                                    category
                                                }
                                            >
                                                {
                                                    category
                                                }
                                            </option>

                                        )
                                    )}

                                </select>

                            </div>


                            {/* DESCRIPTION */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-description"
                                    className="form-label fw-semibold"
                                >
                                    Description
                                </label>


                                <textarea
                                    id="product-description"
                                    name="description"
                                    className="form-control"
                                    rows="5"
                                    value={
                                        formData.description
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter product description"
                                    required
                                />

                            </div>


                            {/* PRICE */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-price"
                                    className="form-label fw-semibold"
                                >
                                    Price (৳)
                                </label>


                                <input
                                    id="product-price"
                                    type="number"
                                    name="price"
                                    className="form-control"
                                    value={
                                        formData.price
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter price"
                                    min="0.01"
                                    step="0.01"
                                    required
                                />

                            </div>


                            {/* STOCK */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-stock"
                                    className="form-label fw-semibold"
                                >
                                    Stock Quantity
                                </label>


                                <input
                                    id="product-stock"
                                    type="number"
                                    name="stock_quantity"
                                    className="form-control"
                                    value={
                                        formData.stock_quantity
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter stock quantity"
                                    min="0"
                                    step="1"
                                    required
                                />

                            </div>


                            {/* IMAGE */}

                            <div className="mb-4">

                                <label
                                    htmlFor="product-image"
                                    className="form-label fw-semibold"
                                >
                                    Product Image
                                </label>


                                <input
                                    id="product-image"
                                    type="file"
                                    name="image"
                                    className="form-control"
                                    accept="image/*"
                                    onChange={
                                        handleImageChange
                                    }
                                />


                                {image && (

                                    <div className="mt-2">

                                        <small className="text-muted">

                                            Selected file:{" "}

                                            {
                                                image.name
                                            }

                                        </small>

                                    </div>

                                )}

                            </div>


                            {/* AVAILABLE */}

                            <div className="form-check mb-3">

                                <input
                                    id="product-available"
                                    type="checkbox"
                                    name="is_available"
                                    className="form-check-input"
                                    checked={
                                        formData.is_available
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />


                                <label
                                    htmlFor="product-available"
                                    className="form-check-label"
                                >
                                    Available
                                </label>

                            </div>


                            {/* FEATURED */}

                            <div className="form-check mb-4">

                                <input
                                    id="product-featured"
                                    type="checkbox"
                                    name="featured"
                                    className="form-check-input"
                                    checked={
                                        formData.featured
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />


                                <label
                                    htmlFor="product-featured"
                                    className="form-check-label"
                                >
                                    Featured Product
                                </label>

                            </div>


                            {/* BUTTONS */}

                            <div className="d-flex gap-2">

                                <button
                                    type="submit"
                                    className="btn btn-success"
                                    disabled={saving}
                                >

                                    {saving ? (

                                        <>

                                            <span
                                                className="spinner-border spinner-border-sm me-2"
                                                role="status"
                                                aria-hidden="true"
                                            />

                                            Saving Product...

                                        </>

                                    ) : (

                                        "Add Product"

                                    )}

                                </button>


                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    disabled={saving}
                                    onClick={() =>
                                        navigate(
                                            "/admin/products"
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

        </DashboardLayout>

    );
};


export default AddProduct;