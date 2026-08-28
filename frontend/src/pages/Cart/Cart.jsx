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
    getCart,
    updateCartItem,
    removeCartItem,
} from "../../services/cartService";

const API_BASE_URL = "http://127.0.0.1:8000";

const FALLBACK_IMAGE =
    "https://placehold.co/80x80?text=No+Image";

const Cart = () => {
    const navigate = useNavigate();

    // =========================================================
    // STATE
    // =========================================================

    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);

    const [updatingId, setUpdatingId] =
        useState(null);

    const [removingId, setRemovingId] =
        useState(null);

    // =========================================================
    // LOAD CART
    // =========================================================

    const fetchCart = useCallback(async () => {
        try {
            const response = await getCart();

            setCart(response.data);
        } catch (error) {
            console.error(
                "Failed to load cart:",
                error
            );

            if (
                error?.response?.status === 401
            ) {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                toast.info(
                    "Please login to continue."
                );

                navigate("/login");
                return;
            }

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to load cart."
            );

            setCart(null);
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    // =========================================================
    // INITIAL CART LOAD
    // =========================================================

    useEffect(() => {
        let cancelled = false;

        const loadCart = async () => {
            try {
                const response = await getCart();

                if (!cancelled) {
                    setCart(response.data);
                }
            } catch (error) {
                console.error(
                    "Failed to load cart:",
                    error
                );

                if (cancelled) {
                    return;
                }

                if (
                    error?.response?.status === 401
                ) {
                    localStorage.removeItem("access");
                    localStorage.removeItem("refresh");

                    toast.info(
                        "Please login to continue."
                    );

                    navigate("/login");
                    return;
                }

                toast.error(
                    error?.response?.data?.detail ||
                        "Failed to load cart."
                );

                setCart(null);
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        loadCart();

        return () => {
            cancelled = true;
        };
    }, [navigate]);

    // =========================================================
    // UPDATE QUANTITY
    // =========================================================

    const handleQuantityChange = async (
        itemId,
        quantity
    ) => {
        if (quantity < 1) {
            return;
        }

        try {
            setUpdatingId(itemId);

            const response =
                await updateCartItem(
                    itemId,
                    quantity
                );

            setCart(response.data);

            toast.success(
                "Cart quantity updated."
            );
        } catch (error) {
            console.error(
                "Failed to update quantity:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to update quantity."
            );

            await fetchCart();
        } finally {
            setUpdatingId(null);
        }
    };

    // =========================================================
    // REMOVE ITEM
    // =========================================================

    const handleRemove = async (itemId) => {
        try {
            setRemovingId(itemId);

            await removeCartItem(itemId);

            toast.success(
                "Item removed from cart."
            );

            await fetchCart();
        } catch (error) {
            console.error(
                "Failed to remove item:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to remove item."
            );
        } finally {
            setRemovingId(null);
        }
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

                <h5 className="mt-3">
                    Loading Cart...
                </h5>
            </div>
        );
    }

    // =========================================================
    // CART ITEMS
    // =========================================================

    const cartItems = Array.isArray(cart?.items)
        ? cart.items
        : [];

    // =========================================================
    // EMPTY CART
    // =========================================================

    if (!cart || cartItems.length === 0) {
        return (
            <div className="container py-5">
                <div className="card shadow-sm">
                    <div className="card-body text-center py-5">
                        <div
                            className="display-4 mb-3"
                            aria-hidden="true"
                        >
                            🛒
                        </div>

                        <h3 className="mb-3">
                            Your Cart is Empty
                        </h3>

                        <p className="text-muted mb-4">
                            Add products to your cart
                            to continue shopping.
                        </p>

                        <Link
                            to="/products"
                            className="btn btn-primary"
                        >
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    // =========================================================
    // RENDER
    // =========================================================

    return (
        <div className="container py-5">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">

                <div>
                    <h2 className="mb-1">
                        Shopping Cart
                    </h2>

                    <p className="text-muted mb-0">
                        {cartItems.length}{" "}
                        {cartItems.length === 1
                            ? "item"
                            : "items"}
                    </p>
                </div>

                <Link
                    to="/products"
                    className="btn btn-outline-primary"
                >
                    Continue Shopping
                </Link>
            </div>

            {/* =================================================
                CART CARD
            ================================================= */}

            <div className="card shadow">

                <div className="card-header bg-primary text-white">
                    <h5 className="mb-0">
                        Cart Items
                    </h5>
                </div>

                <div className="card-body">

                    {cartItems.map((item) => {

                        const product =
                            item.product;

                        // =========================================
                        // IMAGE
                        // =========================================

                        const imageUrl =
                            product?.image
                                ? product.image.startsWith(
                                      "http"
                                  )
                                    ? product.image
                                    : `${API_BASE_URL}${product.image}`
                                : FALLBACK_IMAGE;

                        // =========================================
                        // PRODUCT DATA
                        // =========================================

                        const stockQuantity =
                            Number(
                                product?.stock_quantity ??
                                    0
                            );

                        const quantity =
                            Number(
                                item.quantity ?? 0
                            );

                        const price =
                            Number(
                                product?.price ??
                                    item.product_price ??
                                    item.price ??
                                    0
                            );

                        // =========================================
                        // SUBTOTAL
                        // =========================================

                        const calculatedSubtotal =
                            price * quantity;

                        const subtotal =
                            item.subtotal !==
                                undefined &&
                            item.subtotal !== null
                                ? Number(
                                      item.subtotal
                                  )
                                : calculatedSubtotal;

                        // =========================================
                        // AVAILABILITY
                        // =========================================

                        const isAvailable =
                            product?.is_available ===
                            true;

                        // =========================================
                        // LOADING STATES
                        // =========================================

                        const isUpdating =
                            updatingId === item.id;

                        const isRemoving =
                            removingId === item.id;

                        // =========================================
                        // INCREASE QUANTITY
                        // =========================================

                        const canIncrease =
                            isAvailable &&
                            quantity <
                                stockQuantity;

                        return (
                            <div
                                key={item.id}
                                className="row align-items-center border-bottom py-4"
                            >

                                {/* =================================
                                    PRODUCT
                                ================================= */}

                                <div className="col-md-5 mb-3 mb-md-0">

                                    <div className="d-flex align-items-center">

                                        <img
                                            src={imageUrl}
                                            alt={
                                                product?.name ||
                                                "Product"
                                            }
                                            className="img-thumbnail me-3"
                                            style={{
                                                width: "80px",
                                                height: "80px",
                                                objectFit: "cover",
                                            }}
                                            onError={(event) => {
                                                if (
                                                    event
                                                        .currentTarget
                                                        .src !==
                                                    FALLBACK_IMAGE
                                                ) {
                                                    event.currentTarget.src =
                                                        FALLBACK_IMAGE;
                                                }
                                            }}
                                        />

                                        <div>

                                            <h5 className="mb-1">
                                                {product?.name ||
                                                    "Product"}
                                            </h5>

                                            <p className="text-muted mb-1">
                                                ৳{" "}
                                                {price.toFixed(
                                                    2
                                                )}
                                            </p>

                                            {isAvailable ? (
                                                <span className="badge bg-success">
                                                    In Stock
                                                </span>
                                            ) : (
                                                <span className="badge bg-danger">
                                                    Unavailable
                                                </span>
                                            )}

                                        </div>

                                    </div>

                                </div>

                                {/* =================================
                                    QUANTITY
                                ================================= */}

                                <div className="col-md-3 mb-3 mb-md-0">

                                    <label className="form-label fw-semibold">
                                        Quantity
                                    </label>

                                    <div className="d-flex align-items-center gap-2">

                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                            disabled={
                                                isUpdating ||
                                                isRemoving ||
                                                quantity <=
                                                    1 ||
                                                !isAvailable
                                            }
                                            onClick={() =>
                                                handleQuantityChange(
                                                    item.id,
                                                    quantity -
                                                        1
                                                )
                                            }
                                            aria-label="Decrease quantity"
                                        >
                                            −
                                        </button>

                                        <span
                                            className="fw-bold text-center"
                                            style={{
                                                minWidth:
                                                    "40px",
                                            }}
                                        >
                                            {quantity}
                                        </span>

                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                            disabled={
                                                isUpdating ||
                                                isRemoving ||
                                                !canIncrease
                                            }
                                            onClick={() =>
                                                handleQuantityChange(
                                                    item.id,
                                                    quantity +
                                                        1
                                                )
                                            }
                                            aria-label="Increase quantity"
                                        >
                                            +
                                        </button>

                                    </div>

                                    <small className="text-muted">
                                        Stock:{" "}
                                        {stockQuantity}
                                    </small>

                                    {isUpdating && (
                                        <div className="mt-2">
                                            <span
                                                className="spinner-border spinner-border-sm text-primary me-2"
                                                role="status"
                                            />

                                            Updating...
                                        </div>
                                    )}

                                </div>

                                {/* =================================
                                    SUBTOTAL
                                ================================= */}

                                <div className="col-md-2 mb-3 mb-md-0">

                                    <span className="text-muted d-block">
                                        Subtotal
                                    </span>

                                    <h5 className="mb-0">
                                        ৳{" "}
                                        {subtotal.toFixed(
                                            2
                                        )}
                                    </h5>

                                </div>

                                {/* =================================
                                    REMOVE
                                ================================= */}

                                <div className="col-md-2 text-md-end">

                                    <button
                                        type="button"
                                        className="btn btn-danger btn-sm"
                                        disabled={
                                            isRemoving ||
                                            isUpdating
                                        }
                                        onClick={() =>
                                            handleRemove(
                                                item.id
                                            )
                                        }
                                    >

                                        {isRemoving ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-1"
                                                    role="status"
                                                    aria-hidden="true"
                                                />

                                                Removing...
                                            </>
                                        ) : (
                                            "Remove"
                                        )}

                                    </button>

                                </div>

                            </div>
                        );
                    })}

                    {/* =================================================
                        ORDER TOTAL
                    ================================================= */}

                    <div className="row justify-content-end mt-4">

                        <div className="col-md-5 col-lg-4">

                            <div className="card bg-light">

                                <div className="card-body">

                                    {/* ITEMS */}

                                    <div className="d-flex justify-content-between mb-2">

                                        <span>
                                            Items
                                        </span>

                                        <strong>
                                            {
                                                cartItems.length
                                            }
                                        </strong>

                                    </div>

                                    {/* SUBTOTAL */}

                                    <div className="d-flex justify-content-between">

                                        <span>
                                            Subtotal
                                        </span>

                                        <strong>
                                            ৳{" "}
                                            {Number(
                                                cart.total_amount ??
                                                    0
                                            ).toFixed(
                                                2
                                            )}
                                        </strong>

                                    </div>

                                    <hr />

                                    {/* TOTAL */}

                                    <div className="d-flex justify-content-between align-items-center">

                                        <h5 className="mb-0">
                                            Total
                                        </h5>

                                        <h4 className="mb-0 text-primary">
                                            ৳{" "}
                                            {Number(
                                                cart.total_amount ??
                                                    0
                                            ).toFixed(
                                                2
                                            )}
                                        </h4>

                                    </div>

                                    {/* ACTION BUTTONS */}

                                    <div className="d-grid gap-2 mt-4">

                                        <Link
                                            to="/checkout"
                                            className="btn btn-success btn-lg"
                                        >
                                            Proceed to Checkout
                                        </Link>

                                        <Link
                                            to="/products"
                                            className="btn btn-outline-secondary"
                                        >
                                            Continue Shopping
                                        </Link>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                    {/* =================================================
                        CART INFORMATION
                    ================================================= */}

                    <div className="alert alert-info mt-4 mb-0">

                        <strong>
                            Note:
                        </strong>

                        <ul className="mb-0 mt-2">

                            <li>
                                Quantities cannot exceed
                                available stock.
                            </li>

                            <li>
                                Product prices are verified
                                again during checkout.
                            </li>

                            <li>
                                Stock availability is checked
                                before your order is placed.
                            </li>

                        </ul>

                    </div>

                </div>
            </div>
        </div>
    );
};

export default Cart;