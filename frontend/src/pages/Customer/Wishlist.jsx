import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    Link,
    useNavigate,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    getWishlist,
    removeFromWishlist,
} from "../../services/wishlistService";

import {
    addToCart,
} from "../../services/cartService";

const API_BASE_URL =
    "http://127.0.0.1:8000";

const FALLBACK_IMAGE =
    "https://placehold.co/120x120?text=No+Image";

const Wishlist = () => {

    const navigate = useNavigate();

    const [wishlist, setWishlist] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [removingId, setRemovingId] =
        useState(null);

    const [addingId, setAddingId] =
        useState(null);

    // =====================================
    // LOAD
    // =====================================

    const loadWishlist =
        useCallback(async () => {

            try {

                setLoading(true);

                const response =
                    await getWishlist();

                setWishlist(
                    response.data
                );

            } catch (error) {

                console.error(error);

                if (
                    error.response?.status ===
                    401
                ) {

                    localStorage.removeItem(
                        "access"
                    );

                    localStorage.removeItem(
                        "refresh"
                    );

                    navigate("/login");

                    return;
                }

                toast.error(
                    error.response?.data
                        ?.detail ||
                        "Unable to load wishlist."
                );

            } finally {

                setLoading(false);

            }

        }, [navigate]);

    useEffect(() => {

        const timer =
            setTimeout(() => {

                loadWishlist();

            }, 0);

        return () =>
            clearTimeout(timer);

    }, [loadWishlist]);

    // =====================================
    // REMOVE
    // =====================================

    const handleRemove =
        async (itemId) => {

            try {

                setRemovingId(itemId);

                const response =
                    await removeFromWishlist(
                        itemId
                    );

                setWishlist(
                    response.data
                );

                toast.success(
                    "Removed from wishlist."
                );

            } catch (error) {

                toast.error(
                    error.response?.data
                        ?.detail ||
                        "Remove failed."
                );

            } finally {

                setRemovingId(null);

            }

        };

    // =====================================
    // ADD TO CART
    // =====================================

    const handleAddToCart =
        async (item) => {

            try {

                setAddingId(item.id);

                await addToCart(
                    item.product.id,
                    1
                );

                toast.success(
                    "Added to cart."
                );

            } catch (error) {

                toast.error(
                    error.response?.data
                        ?.detail ||
                        "Unable to add to cart."
                );

            } finally {

                setAddingId(null);

            }

        };

    // =====================================
    // LOADING
    // =====================================

    if (loading) {

        return (

            <div className="container py-5 text-center">

                <div className="spinner-border text-primary"/>

                <h5 className="mt-3">
                    Loading Wishlist...
                </h5>

            </div>

        );

    }

    const items =
        wishlist?.items || [];

    // =====================================
    // EMPTY
    // =====================================

    if (items.length === 0) {

        return (

            <div className="container py-5">

                <div className="card shadow">

                    <div className="card-body text-center py-5">

                        <h3>
                            Wishlist is Empty
                        </h3>

                        <p className="text-muted">

                            You haven't added any
                            products yet.

                        </p>

                        <Link
                            to="/products"
                            className="btn btn-primary"
                        >

                            Browse Products

                        </Link>

                    </div>

                </div>

            </div>

        );

    }

    return (

        <div className="container py-5">

            <h2 className="mb-4">
                ❤️ My Wishlist
            </h2>

            <div className="row g-4">

                {items.map((item) => {

                    const image =
                        item.product.image
                            ? item.product.image.startsWith(
                                  "http"
                              )
                                ? item.product.image
                                : `${API_BASE_URL}${item.product.image}`
                            : FALLBACK_IMAGE;

                    return (

                        <div
                            className="col-md-6 col-lg-4"
                            key={item.id}
                        >

                            <div className="card shadow h-100">

                                <img
                                    src={image}
                                    className="card-img-top"
                                    style={{
                                        height:
                                            "220px",
                                        objectFit:
                                            "cover",
                                    }}
                                    alt={
                                        item.product.name
                                    }
                                    onError={(
                                        e
                                    ) => {

                                        e.currentTarget.src =
                                            FALLBACK_IMAGE;

                                    }}
                                />

                                <div className="card-body">

                                    <h5>
                                        {
                                            item.product
                                                .name
                                        }
                                    </h5>

                                    <p className="text-muted">

                                        {
                                            item.product
                                                .category
                                        }

                                    </p>

                                    <h4 className="text-primary">

                                        ৳
                                        {Number(
                                            item
                                                .product
                                                .price
                                        ).toFixed(
                                            2
                                        )}

                                    </h4>

                                </div>

                                <div className="card-footer bg-white d-grid gap-2">

                                    <button
                                        className="btn btn-success"
                                        disabled={
                                            addingId ===
                                            item.id
                                        }
                                        onClick={() =>
                                            handleAddToCart(
                                                item
                                            )
                                        }
                                    >

                                        {addingId ===
                                        item.id
                                            ? "Adding..."
                                            : "Add to Cart"}

                                    </button>

                                    <button
                                        className="btn btn-outline-danger"
                                        disabled={
                                            removingId ===
                                            item.id
                                        }
                                        onClick={() =>
                                            handleRemove(
                                                item.id
                                            )
                                        }
                                    >

                                        {removingId ===
                                        item.id
                                            ? "Removing..."
                                            : "Remove"}

                                    </button>

                                </div>

                            </div>

                        </div>

                    );

                })}

            </div>

        </div>

    );

};

export default Wishlist;