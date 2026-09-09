import {
    useEffect,
    useMemo,
    useState,
    useCallback,
} from "react";

import {
    Link,
    useNavigate,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    getProducts,
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
    "https://placehold.co/400x300?text=No+Image";

// ============================================================
// COMPONENT
// ============================================================

const Products = () => {

    const navigate = useNavigate();

    // ========================================================
    // PRODUCTS
    // ========================================================

    const [products, setProducts] = useState([]);

    const [loading, setLoading] =
        useState(true);

    // ========================================================
    // WISHLIST
    // ========================================================

    const [wishlist, setWishlist] =
        useState([]);

    const [
        wishlistLoadingId,
        setWishlistLoadingId,
    ] = useState(null);

    // ========================================================
    // CART
    // ========================================================

    const [
        cartLoadingId,
        setCartLoadingId,
    ] = useState(null);

    // ========================================================
    // FILTERS
    // ========================================================

    const [search, setSearch] =
        useState("");

    const [category, setCategory] =
        useState("All");

    const [sort, setSort] =
        useState("default");

    const [minPrice, setMinPrice] = useState("");
    const [maxPrice, setMaxPrice] = useState("");
    const [availability, setAvailability] = useState("in_stock");
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(1);

    // ========================================================
    // AUTH
    // ========================================================

    const isLoggedIn = Boolean(
        localStorage.getItem("access")
    );

    // ========================================================
    // LOAD PRODUCTS
    // ========================================================

    const loadProducts = useCallback(
        async () => {
            try {
                const response =
                    await getProducts({
                        search,
                        category: category === "All" ? "" : category,
                        min_price: minPrice || undefined,
                        max_price: maxPrice || undefined,
                        availability,
                        ordering: sort === "default"
                            ? "-created_at"
                            : sort === "lowToHigh"
                                ? "price"
                                : sort === "highToLow"
                                    ? "-price"
                                    : "name",
                        page,
                    });

                const data = response.data;
                setProducts(Array.isArray(data) ? data : data.results || []);
                setPageCount(data.count ? Math.max(1, Math.ceil(data.count / 12)) : 1);
            } catch (error) {
                console.error(error);

                toast.error(
                    error?.response?.data?.detail ||
                        "Unable to load products."
                );

                setProducts([]);
            }
        },
        [availability, category, maxPrice, minPrice, page, search, sort]
    );

    // ========================================================
    // LOAD WISHLIST
    // ========================================================

    const loadWishlist = useCallback(
        async () => {
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
        },
        [isLoggedIn]
    );

    // ========================================================
    // INITIAL LOAD
    // ========================================================

    useEffect(() => {
        let mounted = true;

        const initialize = async () => {
            try {
                setLoading(true);

                await Promise.all([
                    loadProducts(),
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
        loadProducts,
        loadWishlist,
    ]);

    // ========================================================
    // WISHLIST IDS
    // ========================================================

    const wishlistIds = useMemo(() => {
        return new Set(
            wishlist.map(
                (item) => item.product.id
            )
        );
    }, [wishlist]);

    // ========================================================
    // FILTERED PRODUCTS
    // ========================================================

    const filteredProducts = products;

    const clearFilters = () => {
        setSearch("");
        setCategory("All");
        setMinPrice("");
        setMaxPrice("");
        setAvailability("in_stock");
        setSort("default");
        setPage(1);
    };
    // ========================================================
// IMAGE URL
// ========================================================

const getImage = (product) => {
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
// GET WISHLIST ITEM
// ========================================================

const getWishlistItem = (productId) => {
    return wishlist.find(
        (item) => item.product.id === productId
    );
};

// ========================================================
// ADD TO CART
// ========================================================

const handleAddToCart = async (productId) => {

    if (!isLoggedIn) {
        toast.info(
            "Please login to add products to your cart."
        );

        navigate("/login");

        return;
    }

    try {

        setCartLoadingId(productId);

        await addToCart(productId, 1);

        toast.success(
            "Product added to cart successfully."
        );

    } catch (error) {

        console.error(error);

        toast.error(
            error?.response?.data?.detail ||
            "Unable to add product."
        );

    } finally {

        setCartLoadingId(null);

    }
};

// ========================================================
// ADD TO WISHLIST
// ========================================================

const handleAddWishlist = async (productId) => {

    if (!isLoggedIn) {

        toast.info(
            "Please login to use wishlist."
        );

        navigate("/login");

        return;
    }

    try {

        setWishlistLoadingId(productId);

        await addToWishlist(productId);

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

        setWishlistLoadingId(null);

    }
};

// ========================================================
// REMOVE FROM WISHLIST
// ========================================================

const handleRemoveWishlist = async (
    wishlistItemId,
    productId
) => {

    try {

        setWishlistLoadingId(productId);

        await removeFromWishlist(
            wishlistItemId
        );

        setWishlist((previous) =>
            previous.filter(
                (item) =>
                    item.id !== wishlistItemId
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

        setWishlistLoadingId(null);

    }
};

// ========================================================
// TOGGLE WISHLIST
// ========================================================

const toggleWishlist = async (productId) => {

    const wishlistItem =
        getWishlistItem(productId);

    if (wishlistItem) {

        await handleRemoveWishlist(
            wishlistItem.id,
            productId
        );

    } else {

        await handleAddWishlist(
            productId
        );

    }
};

// ========================================================
// LOADING SCREEN
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
                Loading Products...
            </h4>

        </div>
    );
}
// ========================================================
// PAGE
// ========================================================

return (
    <div className="container py-5">

        {/* ========================================= */}
        {/* PAGE TITLE */}
        {/* ========================================= */}

        <div className="text-center mb-5">

            <h1 className="fw-bold">
                🥐 Our Fresh Bakery Collection
            </h1>

            <p className="text-muted">
                Freshly baked cakes, breads, pastries,
                cookies and desserts delivered
                to your doorstep.
            </p>

        </div>

        {/* ========================================= */}
        {/* SEARCH + FILTER */}
        {/* ========================================= */}

        <div className="row g-3 mb-5">

            {/* Search */}

            <div className="col-lg-4">

                <input
                    type="text"
                    className="form-control"
                    placeholder="Search bakery products..."
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setPage(1);
                    }}
                />

            </div>

            {/* Category */}

            <div className="col-lg-4">

                <select
                    className="form-select"
                    value={category}
                    onChange={(e) => {
                        setCategory(e.target.value);
                        setPage(1);
                    }}
                >
                    <option value="All">
                        All Categories
                    </option>

                    <option value="Cake">
                        Cake
                    </option>

                    <option value="Bread">
                        Bread
                    </option>

                    <option value="Cookies">
                        Cookies
                    </option>

                    <option value="Pastry">
                        Pastry
                    </option>

                    <option value="Donut">
                        Donut
                    </option>

                    <option value="Muffin">
                        Muffin
                    </option>

                    <option value="Cup Cake">
                        Cup Cake
                    </option>

                </select>

            </div>

            {/* Sorting */}

            <div className="col-lg-4">

                <select
                    className="form-select"
                    value={sort}
                    onChange={(e) => {
                        setSort(e.target.value);
                        setPage(1);
                    }}
                >

                    <option value="default">
                        Default Sorting
                    </option>

                    <option value="lowToHigh">
                        Price: Low → High
                    </option>

                    <option value="highToLow">
                        Price: High → Low
                    </option>

                    <option value="name">
                        Name (A-Z)
                    </option>

                </select>

            </div>

            <div className="col-md-3">
                <input
                    type="number"
                    min="0"
                    className="form-control"
                    placeholder="Min price"
                    value={minPrice}
                    onChange={(event) => {
                        setMinPrice(event.target.value);
                        setPage(1);
                    }}
                />
            </div>

            <div className="col-md-3">
                <input
                    type="number"
                    min="0"
                    className="form-control"
                    placeholder="Max price"
                    value={maxPrice}
                    onChange={(event) => {
                        setMaxPrice(event.target.value);
                        setPage(1);
                    }}
                />
            </div>

            <div className="col-md-3">
                <select
                    className="form-select"
                    value={availability}
                    onChange={(event) => {
                        setAvailability(event.target.value);
                        setPage(1);
                    }}
                >
                    <option value="in_stock">In Stock</option>
                    <option value="low_stock">Low Stock</option>
                </select>
            </div>

            <div className="col-md-3">
                <button type="button" className="btn btn-outline-secondary w-100" onClick={clearFilters}>
                    Clear Filters
                </button>
            </div>

        </div>

        {/* ========================================= */}
        {/* PRODUCTS */}
        {/* ========================================= */}

        <div className="row">

            {filteredProducts.length === 0 ? (

                <div className="col-12 text-center py-5">

                    <h3>No Products Found</h3>

                    <p className="text-muted">
                        Try another search or category.
                    </p>

                </div>

            ) : (

                filteredProducts.map((product) => {

                    const stock =
                        Number(product.stock_quantity);

                    const available =
                        product.is_available &&
                        stock > 0;

                    return (

                        <div
                            key={product.id}
                            className="col-xl-3 col-lg-4 col-md-6 mb-4"
                        >

                            <div className="card shadow-sm border-0 h-100">

                                {/* Product Image */}

                                <div className="position-relative">

                                    <img
                                        src={getImage(product)}
                                        alt={product.name}
                                        className="card-img-top"
                                        style={{
                                            height: "250px",
                                            objectFit: "cover",
                                        }}
                                        onError={(e) => {
                                            e.currentTarget.src =
                                                FALLBACK_IMAGE;
                                        }}
                                    />

                                    {/* Wishlist Heart */}

                                    <button
                                        type="button"
                                        className={`btn position-absolute top-0 end-0 m-2 rounded-circle shadow ${
                                            wishlistIds.has(product.id)
                                                ? "btn-danger"
                                                : "btn-light"
                                        }`}
                                        disabled={
                                            wishlistLoadingId ===
                                            product.id
                                        }
                                        onClick={() =>
                                            toggleWishlist(product.id)
                                        }
                                    >

                                        {wishlistLoadingId ===
                                        product.id ? (
                                            <span className="spinner-border spinner-border-sm" />
                                        ) : wishlistIds.has(
                                              product.id
                                          ) ? (
                                            "♥"
                                        ) : (
                                            "♡"
                                        )}

                                    </button>

                                </div>

                                {/* Card Body */}

                                <div className="card-body d-flex flex-column">

                                    <span className="badge bg-secondary mb-2 align-self-start">
                                        {product.category}
                                    </span>

                                    <h5 className="fw-bold">
                                        {product.name}
                                    </h5>

                                    <p
                                        className="text-muted small flex-grow-1"
                                        style={{
                                            minHeight: "70px",
                                        }}
                                    >
                                        {product.description}
                                    </p>

                                    <h4 className="text-primary fw-bold">
                                        ৳
                                        {Number(
                                            product.price
                                        ).toFixed(2)}
                                    </h4>

                                    {available ? (
                                        <span className="badge bg-success mb-3">
                                            {stock} Available
                                        </span>
                                    ) : (
                                        <span className="badge bg-danger mb-3">
                                            Out of Stock
                                        </span>
                                    )}
                                                                        {/* ===================================== */}
                                    {/* ACTION BUTTONS */}
                                    {/* ===================================== */}

                                    <div className="mt-auto d-grid gap-2">

                                        {/* Add to Cart */}

                                        <button
                                            className="btn btn-primary"
                                            disabled={
                                                !available ||
                                                cartLoadingId === product.id
                                            }
                                            onClick={() =>
                                                handleAddToCart(product.id)
                                            }
                                        >
                                            {cartLoadingId === product.id ? (
                                                <>
                                                    <span
                                                        className="spinner-border spinner-border-sm me-2"
                                                        role="status"
                                                    />
                                                    Adding...
                                                </>
                                            ) : (
                                                <>🛒 Add to Cart</>
                                            )}
                                        </button>

                                        {/* View Details */}

                                        <Link
                                            to={`/products/${product.id}`}
                                            className="btn btn-outline-dark"
                                        >
                                            👁 View Details
                                        </Link>

                                    </div>

                                    {pageCount > 1 && (
                                        <div className="d-flex justify-content-center align-items-center gap-3 mt-3">
                                            <button
                                                type="button"
                                                className="btn btn-outline-primary"
                                                disabled={page <= 1}
                                                onClick={() => setPage((current) => current - 1)}
                                            >
                                                Previous
                                            </button>
                                            <span className="text-muted">Page {page} of {pageCount}</span>
                                            <button
                                                type="button"
                                                className="btn btn-outline-primary"
                                                disabled={page >= pageCount}
                                                onClick={() => setPage((current) => current + 1)}
                                            >
                                                Next
                                            </button>
                                        </div>
                                    )}

                                </div>
                                {/* End Card Body */}

                            </div>
                            {/* End Card */}

                        </div>
                    );

                })

            )}

        </div>
        {/* End Product Grid */}

    </div>
    /* End Container */
);

};

export default Products;