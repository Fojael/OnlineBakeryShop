import { useEffect, useState } from "react";
import {
    Link,
    useNavigate,
    useParams,
} from "react-router-dom";
import { toast } from "react-toastify";

import { getProduct } from "../../services/productService";
import { addToCart as addProductToCart } from "../../services/cartService";

const API_BASE_URL = "http://127.0.0.1:8000";

const ProductDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [quantity, setQuantity] = useState(1);

    // =========================================================
    // PRODUCT IMAGE
    // =========================================================

    const getProductImage = (productData) => {
        if (!productData?.image) {
            return "https://placehold.co/600x500?text=No+Image";
        }

        const image = String(productData.image);

        if (
            image.startsWith("http://") ||
            image.startsWith("https://")
        ) {
            return image;
        }

        return `${API_BASE_URL}${image}`;
    };

    // =========================================================
    // LOAD PRODUCT
    // =========================================================

    useEffect(() => {
        const loadProduct = async () => {
            try {
                setLoading(true);

                const response = await getProduct(id);

                setProduct(response.data);
            } catch (error) {
                console.error(error);

                toast.error(
                    error?.response?.data?.detail ||
                        "Unable to load product."
                );

                setProduct(null);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            loadProduct();
        }
    }, [id]);

    // =========================================================
    // PRODUCT STATUS
    // =========================================================

    const stockQuantity = Number(product?.stock_quantity || 0);

    const isAvailable =
        product?.is_available !== false &&
        stockQuantity > 0;

    const isLoggedIn = Boolean(
        localStorage.getItem("access")
    );

    // =========================================================
    // QUANTITY
    // =========================================================

    const handleQuantityChange = (event) => {
        const value = Number(event.target.value);

        if (Number.isNaN(value) || value < 1) {
            setQuantity(1);
            return;
        }

        if (value > stockQuantity) {
            setQuantity(stockQuantity);
            return;
        }

        setQuantity(value);
    };

    // =========================================================
    // ADD TO CART
    // =========================================================

    const addToCart = async () => {
        if (!isLoggedIn) {
            toast.info(
                "Please login to add products to your cart."
            );

            navigate("/login");

            return;
        }

        if (!product) {
            toast.error("Product not found.");
            return;
        }

        if (!isAvailable) {
            toast.error(
                "This product is currently unavailable."
            );
            return;
        }

        try {
            await addProductToCart(
                product.id,
                quantity
            );

            toast.success(
                `${product.name} added to cart.`
            );
        } catch (error) {
            console.error(error);

            if (error?.response?.status === 401) {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                toast.info(
                    "Please login again."
                );

                navigate("/login");

                return;
            }

            toast.error(
                error?.response?.data?.detail ||
                    "Unable to add product."
            );
        }
    };

    // =========================================================
    // BUY NOW
    // =========================================================

    const handleBuyNow = () => {
        if (!isLoggedIn) {
            toast.info(
                "Please login before purchasing."
            );

            navigate("/login");
            return;
        }

        if (!isAvailable) {
            toast.error(
                "This product is currently unavailable."
            );
            return;
        }

        toast.info(
            "Checkout will be connected next."
        );

        // Later:
        // navigate("/checkout");
    };

    // =========================================================
    // LOADING
    // =========================================================

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

                <h4 className="mt-3">
                    Loading Product Details...
                </h4>
            </div>
        );
    }

    // =========================================================
    // PRODUCT NOT FOUND
    // =========================================================

    if (!product) {
        return (
            <div className="container py-5 text-center">
                <h3>Product Not Found</h3>

                <p className="text-muted">
                    The requested product could not be
                    found.
                </p>

                <Link
                    to="/products"
                    className="btn btn-primary"
                >
                    Browse Products
                </Link>
            </div>
        );
    }

    // =========================================================
    // PAGE
    // =========================================================

    return (
        <div className="container py-5">
            <div className="row g-5">

                {/* IMAGE */}

                <div className="col-md-6">
                    <div className="card shadow-sm border-0">
                        <img
                            src={getProductImage(product)}
                            alt={product.name}
                            className="card-img-top"
                            style={{
                                width: "100%",
                                height: "500px",
                                objectFit: "cover",
                            }}
                            onError={(e) => {
                                e.currentTarget.src =
                                    "https://placehold.co/600x500?text=No+Image";
                            }}
                        />
                    </div>
                </div>

                {/* PRODUCT INFO */}

                <div className="col-md-6">

                    <span className="badge bg-secondary mb-3">
                        {product.category || "Bakery"}
                    </span>

                    <h1 className="fw-bold mb-3">
                        {product.name}
                    </h1>

                    <h2 className="text-primary fw-bold mb-4">
                        ৳{" "}
                        {Number(
                            product.price || 0
                        ).toFixed(2)}
                    </h2>

                    <div className="mb-4">
                        <h5 className="fw-bold">
                            Description
                        </h5>

                        <p className="text-muted">
                            {product.description ||
                                "No description available."}
                        </p>
                    </div>

                    <div className="mb-4">
                        <h6 className="fw-bold">
                            Availability
                        </h6>

                        {isAvailable ? (
                            <span className="badge bg-success">
                                In Stock
                            </span>
                        ) : (
                            <span className="badge bg-danger">
                                Out of Stock
                            </span>
                        )}

                        <p className="mt-2">
                            Available Quantity:
                            <strong>
                                {" "}
                                {stockQuantity}
                            </strong>
                        </p>
                    </div>

                    <div className="mb-4">
                        <label className="form-label fw-bold">
                            Quantity
                        </label>

                        <input
                            type="number"
                            className="form-control"
                            style={{
                                width: "130px",
                            }}
                            value={quantity}
                            min="1"
                            max={
                                stockQuantity || 1
                            }
                            disabled={!isAvailable}
                            onChange={
                                handleQuantityChange
                            }
                        />
                    </div>

                    {/* BUTTONS */}

                    <div className="d-flex flex-wrap gap-2">

                        {isLoggedIn ? (
                            <>
                                <button
                                    className="btn btn-primary btn-lg"
                                    disabled={!isAvailable}
                                    onClick={addToCart}
                                >
                                    Add to Cart
                                </button>

                                <button
                                    className="btn btn-success btn-lg"
                                    disabled={!isAvailable}
                                    onClick={handleBuyNow}
                                >
                                    Buy Now
                                </button>
                            </>
                        ) : (
                            <button
                                className="btn btn-primary btn-lg"
                                onClick={() => {
                                    toast.info(
                                        "Please login to purchase this product."
                                    );

                                    navigate("/login");
                                }}
                            >
                                Login to Purchase
                            </button>
                        )}

                        <Link
                            to="/products"
                            className="btn btn-outline-secondary btn-lg"
                        >
                            Back to Products
                        </Link>
                    </div>

            </div>
        </div>
    </div>
    );
};

export default ProductDetails;