import {
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    Link,
    useNavigate,
    useParams,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    getProduct,
} from "../../services/productService";

import {
    addToCart,
} from "../../services/cartService";

import {
    getWishlist,
    addToWishlist,
    removeFromWishlist,
} from "../../services/wishlistService";

// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";

const FALLBACK_IMAGE =
    "https://placehold.co/600x500?text=No+Image";

// ============================================================
// COMPONENT
// ============================================================

const ProductDetails = () => {

    const { id } = useParams();

    const navigate = useNavigate();

    // ========================================================
    // STATE
    // ========================================================

    const [product, setProduct] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [quantity, setQuantity] =
        useState(1);

    const [wishlist, setWishlist] =
        useState([]);

    const [
        cartLoading,
        setCartLoading,
    ] = useState(false);

    const [
        wishlistLoading,
        setWishlistLoading,
    ] = useState(false);

    // ========================================================
    // AUTH
    // ========================================================

    const isLoggedIn = Boolean(
        localStorage.getItem("access")
    );

    // ========================================================
    // LOAD PRODUCT
    // ========================================================

    const loadProduct = useCallback(async () => {

        try {

            const response =
                await getProduct(id);

            setProduct(response.data);

        } catch (error) {

            console.error(error);

            toast.error(
                error?.response?.data?.detail ||
                "Unable to load product."
            );

            setProduct(null);

        }

    }, [id]);

    // ========================================================
    // LOAD WISHLIST
    // ========================================================

    const loadWishlist = useCallback(async () => {

        if (!isLoggedIn) {
            setWishlist([]);
            return;
        }

        try {

            const response =
                await getWishlist();

            setWishlist(
                Array.isArray(response.data.items)
                    ? response.data.items
                    : []
            );

        } catch (error) {

            console.error(error);

            setWishlist([]);

        }

    }, [isLoggedIn]);

    // ========================================================
    // INITIAL LOAD
    // ========================================================

    useEffect(() => {

        let mounted = true;

        const initialize = async () => {

            try {

                setLoading(true);

                await Promise.all([
                    loadProduct(),
                    loadWishlist(),
                ]);

            } finally {

                if (mounted) {
                    setLoading(false);
                }

            }

        };

        initialize();

        return () => {
            mounted = false;
        };

    }, [
        loadProduct,
        loadWishlist,
    ]);
    // ========================================================
// PRODUCT IMAGE
// ========================================================

const getProductImage = () => {

    if (!product?.image) {
        return FALLBACK_IMAGE;
    }

    if (
        product.image.startsWith("http://") ||
        product.image.startsWith("https://")
    ) {
        return product.image;
    }

    return `${API_BASE_URL}${product.image}`;
};

// ========================================================
// STOCK
// ========================================================

const stockQuantity = Number(
    product?.stock_quantity || 0
);

const isAvailable =
    product?.is_available &&
    stockQuantity > 0;

// ========================================================
// WISHLIST
// ========================================================

const wishlistItem = wishlist.find(
    (item) =>
        item.product.id === Number(id)
);

const isWishlisted = Boolean(
    wishlistItem
);

// ========================================================
// QUANTITY
// ========================================================

const handleQuantityChange = (event) => {

    const value = Number(
        event.target.value
    );

    if (Number.isNaN(value)) {
        return;
    }

    if (value < 1) {
        setQuantity(1);
        return;
    }

    if (value > stockQuantity) {
        setQuantity(stockQuantity);
        return;
    }

    setQuantity(value);
};

// ========================================================
// ADD TO WISHLIST
// ========================================================

const handleAddWishlist = async () => {

    if (!isLoggedIn) {

        toast.info(
            "Please login to use wishlist."
        );

        navigate("/login");

        return;
    }

    try {

        setWishlistLoading(true);

        await addToWishlist(product.id);

        await loadWishlist();

        toast.success(
            "Added to wishlist."
        );

    } catch (error) {

        console.error(error);

        toast.error(
            error?.response?.data?.detail ||
            "Unable to add to wishlist."
        );

    } finally {

        setWishlistLoading(false);

    }

};

// ========================================================
// REMOVE FROM WISHLIST
// ========================================================

const handleRemoveWishlist = async () => {

    if (!wishlistItem) return;

    try {

        setWishlistLoading(true);

        await removeFromWishlist(
            wishlistItem.id
        );

        setWishlist((previous) =>
            previous.filter(
                (item) =>
                    item.id !== wishlistItem.id
            )
        );

        toast.success(
            "Removed from wishlist."
        );

    } catch (error) {

        console.error(error);

        toast.error(
            error?.response?.data?.detail ||
            "Unable to remove from wishlist."
        );

    } finally {

        setWishlistLoading(false);

    }

};

// ========================================================
// TOGGLE WISHLIST
// ========================================================

const toggleWishlist = async () => {

    if (isWishlisted) {

        await handleRemoveWishlist();

    } else {

        await handleAddWishlist();

    }

};
// ========================================================
// ADD TO CART
// ========================================================

const handleAddToCart = async () => {

    if (!isLoggedIn) {

        toast.info(
            "Please login to add products to your cart."
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

    try {

        setCartLoading(true);

        await addToCart(
            product.id,
            quantity
        );

        toast.success(
            `${product.name} added to cart successfully.`
        );

    } catch (error) {

        console.error(error);

        toast.error(
            error?.response?.data?.detail ||
            "Unable to add product to cart."
        );

    } finally {

        setCartLoading(false);

    }

};

// ========================================================
// BUY NOW
// ========================================================

const handleBuyNow = async () => {

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

    try {

        setCartLoading(true);

        await addToCart(
            product.id,
            quantity
        );

        toast.success(
            "Proceeding to checkout..."
        );

        navigate("/checkout");

    } catch (error) {

        console.error(error);

        toast.error(
            error?.response?.data?.detail ||
            "Unable to proceed to checkout."
        );

    } finally {

        setCartLoading(false);

    }

};

// ========================================================
// LOADING
// ========================================================

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
                Loading Product...
            </h4>

        </div>

    );

}

// ========================================================
// PRODUCT NOT FOUND
// ========================================================

if (!product) {

    return (

        <div className="container py-5 text-center">

            <h2>
                Product Not Found
            </h2>

            <p className="text-muted">
                The requested product does not exist.
            </p>

            <Link
                to="/products"
                className="btn btn-primary mt-3"
            >
                Back to Products
            </Link>

        </div>

    );

}
// ========================================================
// PAGE
// ========================================================

return (
    <div className="container py-5">

        <div className="row g-5">

            {/* ================================================= */}
            {/* PRODUCT IMAGE */}
            {/* ================================================= */}

            <div className="col-lg-6">

                <div className="card shadow border-0">

                    <img
                        src={getProductImage()}
                        alt={product.name}
                        className="card-img-top"
                        style={{
                            height: "500px",
                            objectFit: "cover",
                        }}
                        onError={(e) => {
                            e.target.src = FALLBACK_IMAGE;
                        }}
                    />

                </div>

            </div>

            {/* ================================================= */}
            {/* PRODUCT DETAILS */}
            {/* ================================================= */}

            <div className="col-lg-6">

                <span className="badge bg-secondary mb-3">
                    {product.category}
                </span>

                <h1 className="fw-bold">
                    {product.name}
                </h1>

                <h2 className="text-primary fw-bold my-3">
                    ৳
                    {Number(product.price).toFixed(2)}
                </h2>

                <p className="text-muted">
                    {product.description}
                </p>

                <hr />

                {/* Stock */}

                <div className="mb-3">

                    {isAvailable ? (

                        <span className="badge bg-success fs-6">
                            {stockQuantity} In Stock
                        </span>

                    ) : (

                        <span className="badge bg-danger fs-6">
                            Out of Stock
                        </span>

                    )}

                </div>

                {/* Quantity */}

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
                        max={stockQuantity}
                        disabled={!isAvailable}
                        onChange={handleQuantityChange}
                    />

                </div>

                {/* ============================================= */}
                {/* ACTION BUTTONS */}
                {/* ============================================= */}

                <div className="d-grid gap-2">

                    {/* Add To Cart */}

                    <button
                        className="btn btn-primary btn-lg"
                        disabled={
                            cartLoading ||
                            !isAvailable
                        }
                        onClick={handleAddToCart}
                    >

                        {cartLoading ? (

                            <>
                                <span className="spinner-border spinner-border-sm me-2"></span>
                                Adding...
                            </>

                        ) : (

                            <>🛒 Add to Cart</>

                        )}

                    </button>

                    {/* Buy Now */}

                    <button
                        className="btn btn-success btn-lg"
                        disabled={
                            cartLoading ||
                            !isAvailable
                        }
                        onClick={handleBuyNow}
                    >
                        ⚡ Buy Now
                    </button>

                    {/* Wishlist */}

                    <button
                        className={`btn btn-lg ${
                            isWishlisted
                                ? "btn-danger"
                                : "btn-outline-danger"
                        }`}
                        disabled={wishlistLoading}
                        onClick={toggleWishlist}
                    >

                        {wishlistLoading ? (

                            <>
                                <span className="spinner-border spinner-border-sm me-2"></span>
                                Processing...
                            </>

                        ) : isWishlisted ? (

                            <>❤️ Remove from Wishlist</>

                        ) : (

                            <>🤍 Add to Wishlist</>

                        )}

                    </button>

                    {/* Back */}

                    <Link
                        to="/products"
                        className="btn btn-outline-secondary btn-lg"
                    >
                        ← Back to Products
                    </Link>

                </div>

            </div>

        </div>

    </div>
);

};

export default ProductDetails;