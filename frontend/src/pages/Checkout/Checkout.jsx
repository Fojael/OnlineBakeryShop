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

import { getCart } from "../../services/cartService";
import { createOrder } from "../../services/orderService";

const API_BASE_URL = "http://127.0.0.1:8000";

const Checkout = () => {
    const navigate = useNavigate();

    // =========================================================
    // STATE
    // =========================================================

    const [cart, setCart] = useState(null);

    const [loading, setLoading] = useState(true);

    const [placingOrder, setPlacingOrder] =
        useState(false);

    const [formData, setFormData] = useState({
        shipping_address: "",
        payment_method: "Cash on Delivery",
    });

    // =========================================================
    // LOAD CART
    // =========================================================

    const fetchCart = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getCart();

            setCart(response.data);
        } catch (error) {
            console.error(error);

            if (error?.response?.status === 401) {
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

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchCart();
        }, 0);

        return () => {
            window.clearTimeout(timer);
        };
    }, [fetchCart]);

    // =========================================================
    // FORM CHANGE
    // =========================================================

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    // =========================================================
    // PLACE ORDER
    // =========================================================

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!formData.shipping_address.trim()) {
            toast.warning(
                "Shipping address is required."
            );

            return;
        }

        if (
            !cart ||
            !Array.isArray(cart.items) ||
            cart.items.length === 0
        ) {
            toast.warning("Your cart is empty.");

            navigate("/cart");

            return;
        }

        try {
            setPlacingOrder(true);

            const response = await createOrder({
                shipping_address:
                    formData.shipping_address.trim(),
                payment_method:
                    formData.payment_method,
            });

            toast.success(
                response.data.message ||
                    "Order placed successfully."
            );

            navigate("/orders");
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
                    "Failed to place order."
            );
        } finally {
            setPlacingOrder(false);
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
                    Loading Checkout...
                </h5>
            </div>
        );
    }

    // =========================================================
    // EMPTY CART
    // =========================================================

    if (
        !cart ||
        !Array.isArray(cart.items) ||
        cart.items.length === 0
    ) {
        return (
            <div className="container py-5">
                <div className="card shadow">
                    <div className="card-body text-center py-5">
                        <h3>Your Cart is Empty</h3>

                        <p className="text-muted">
                            Add products before
                            proceeding to checkout.
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

    return (
        <div className="container py-5">
            <div className="row g-4">
                {/* ================================================= */}
                {/* CHECKOUT FORM */}
                {/* ================================================= */}

                <div className="col-lg-7">
                    <div className="card shadow">
                        <div className="card-header bg-primary text-white">
                            <h3 className="mb-0">Checkout</h3>
                        </div>

                        <div className="card-body">
                            <form onSubmit={handleSubmit}>
                                {/* Shipping Address */}

                                <div className="mb-4">
                                    <label
                                        htmlFor="shipping_address"
                                        className="form-label fw-semibold"
                                    >
                                        Shipping Address
                                    </label>

                                    <textarea
                                        id="shipping_address"
                                        name="shipping_address"
                                        className="form-control"
                                        rows={4}
                                        placeholder="Enter your complete delivery address"
                                        value={formData.shipping_address}
                                        onChange={handleChange}
                                        disabled={placingOrder}
                                        required
                                    />
                                </div>

                                {/* Payment Method */}

                                <div className="mb-4">
                                    <label
                                        htmlFor="payment_method"
                                        className="form-label fw-semibold"
                                    >
                                        Payment Method
                                    </label>

                                    <select
                                        id="payment_method"
                                        name="payment_method"
                                        className="form-select"
                                        value={formData.payment_method}
                                        onChange={handleChange}
                                        disabled={placingOrder}
                                    >
                                        <option value="Cash on Delivery">
                                            Cash on Delivery
                                        </option>

                                        <option value="bKash">
                                            bKash
                                        </option>

                                        <option value="Nagad">
                                            Nagad
                                        </option>

                                        <option value="Rocket">
                                            Rocket
                                        </option>

                                        <option value="Credit Card">
                                            Credit Card
                                        </option>
                                    </select>
                                </div>

                                {/* Order Total */}

                                <div className="mb-4">
                                    <label className="form-label fw-semibold">
                                        Order Total
                                    </label>

                                    <div className="form-control bg-light">
                                        <strong>
                                            ৳ {" "}
                                            {Number(
                                                cart.total_amount || 0
                                            ).toFixed(2)}
                                        </strong>
                                    </div>

                                    <small className="text-muted">
                                        Calculated from your current cart.
                                    </small>
                                </div>

                                {/* Buttons */}

                                <div className="d-flex gap-2">
                                    <button
                                        type="submit"
                                        className="btn btn-success"
                                        disabled={placingOrder}
                                    >
                                        {placingOrder ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                />
                                                Placing Order...
                                            </>
                                        ) : (
                                            "Place Order"
                                        )}
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        disabled={placingOrder}
                                        onClick={() => navigate("/cart")}
                                    >
                                        Back to Cart
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                {/* ================================================= */}
                {/* ORDER SUMMARY */}
                {/* ================================================= */}

                <div className="col-lg-5">
                    <div className="card shadow">
                        <div className="card-header bg-dark text-white">
                            <h5 className="mb-0">Order Summary</h5>
                        </div>

                        <div className="card-body">
                            {cart.items.map((item) => {
                                const imageUrl =
                                    item.product?.image
                                        ? item.product.image.startsWith("http")
                                            ? item.product.image
                                            : `${API_BASE_URL}${item.product.image}`
                                        : "https://placehold.co/80x80?text=No+Image";

                                return (
                                    <div
                                        key={item.id}
                                        className="d-flex justify-content-between align-items-center border-bottom py-3"
                                    >
                                        <div className="d-flex">
                                            <img
                                                src={imageUrl}
                                                alt={item.product?.name}
                                                width="70"
                                                height="70"
                                                className="rounded me-3"
                                                style={{
                                                    objectFit: "cover",
                                                }}
                                                onError={(e) => {
                                                    e.currentTarget.src =
                                                        "https://placehold.co/80x80?text=No+Image";
                                                }}
                                            />

                                            <div>
                                                <strong>
                                                    {item.product?.name}
                                                </strong>

                                                <div className="text-muted small">
                                                    Qty: {item.quantity}
                                                </div>

                                                <div className="text-muted small">
                                                    Unit Price: ৳ {" "}
                                                    {Number(
                                                        item.product?.price || 0
                                                    ).toFixed(2)}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="fw-bold">
                                            ৳ {" "}
                                            {Number(
                                                item.subtotal || 0
                                            ).toFixed(2)}
                                        </div>
                                    </div>
                                );
                            })}

                            <div className="mt-4">
                                <div className="d-flex justify-content-between mb-2">
                                    <span>Items</span>

                                    <strong>{cart.items.length}</strong>
                                </div>

                                <div className="d-flex justify-content-between mb-2">
                                    <span>Subtotal</span>

                                    <strong>
                                        ৳ {" "}
                                        {Number(
                                            cart.total_amount || 0
                                        ).toFixed(2)}
                                    </strong>
                                </div>

                                <div className="d-flex justify-content-between mb-2">
                                    <span>Shipping</span>

                                    <strong>Free</strong>
                                </div>

                                <hr />

                                <div className="d-flex justify-content-between">
                                    <h5>Total</h5>

                                    <h5 className="text-primary">
                                        ৳ {" "}
                                        {Number(
                                            cart.total_amount || 0
                                        ).toFixed(2)}
                                    </h5>
                                </div>

                                <small className="text-muted">
                                    Your order total is calculated from the
                                    latest prices in your cart.
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Checkout;