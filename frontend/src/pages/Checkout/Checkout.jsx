```jsx
import {
    useCallback,
    useEffect,
    useState,
} from "react";

import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import {
    getCart,
} from "../../services/cartService";

import {
    createOrder,
} from "../../services/orderService";


const Checkout = () => {
    const navigate = useNavigate();

    const [cart, setCart] = useState(null);

    const [loading, setLoading] = useState(true);

    const [placingOrder, setPlacingOrder] =
        useState(false);

    const [formData, setFormData] = useState({
        shipping_address: "",
        payment_method: "Cash on Delivery",
    });


    // =========================================================
    // GET REAL CART
    // =========================================================

    const fetchCart = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getCart();

            setCart(response.data);

        } catch (error) {
            console.error(
                "Failed to load cart:",
                error
            );

            toast.error(
                error.response?.data?.detail ||
                "Failed to load cart."
            );

            setCart(null);

        } finally {
            setLoading(false);
        }
    }, []);


    // =========================================================
    // LOAD CART
    // =========================================================

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

    const handleChange = (e) => {
        const {
            name,
            value,
        } = e.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    };


    // =========================================================
    // PLACE ORDER
    // =========================================================

    const handleSubmit = async (e) => {
        e.preventDefault();


        // -----------------------------------------------------
        // Validate shipping address
        // -----------------------------------------------------

        if (!formData.shipping_address.trim()) {
            toast.warning(
                "Shipping address is required."
            );

            return;
        }


        // -----------------------------------------------------
        // Validate cart
        // -----------------------------------------------------

        if (
            !cart ||
            !Array.isArray(cart.items) ||
            cart.items.length === 0
        ) {
            toast.warning(
                "Your cart is empty."
            );

            navigate("/cart");

            return;
        }


        // -----------------------------------------------------
        // Validate cart total
        // -----------------------------------------------------

        const totalAmount = Number(
            cart.total_amount || 0
        );

        if (totalAmount <= 0) {
            toast.warning(
                "Cart total must be greater than zero."
            );

            return;
        }


        // -----------------------------------------------------
        // IMPORTANT:
        // Do NOT send total_amount.
        //
        // Django calculates the real total
        // from the customer's cart.
        // -----------------------------------------------------

        const orderData = {
            shipping_address:
                formData.shipping_address.trim(),

            payment_method:
                formData.payment_method,
        };


        try {
            setPlacingOrder(true);

            await createOrder(orderData);

            toast.success(
                "Order placed successfully."
            );

            navigate("/orders");

        } catch (error) {
            console.error(
                "Failed to place order:",
                error
            );

            const message =
                error.response?.data?.detail ||
                "Failed to place order.";

            toast.error(message);

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

                        <h3>
                            Your Cart is Empty
                        </h3>

                        <p className="text-muted">
                            Add products before
                            proceeding to checkout.
                        </p>

                        <button
                            type="button"
                            className="btn btn-primary"
                            onClick={() =>
                                navigate("/products")
                            }
                        >
                            Continue Shopping
                        </button>

                    </div>

                </div>

            </div>
        );
    }


    // =========================================================
    // CHECKOUT PAGE
    // =========================================================

    return (
        <div className="container py-5">

            <div className="row g-4">

                {/* =================================================
                    CHECKOUT FORM
                ================================================= */}

                <div className="col-lg-7">

                    <div className="card shadow">

                        <div className="card-header bg-primary text-white">

                            <h3 className="mb-0">
                                Checkout
                            </h3>

                        </div>


                        <div className="card-body">

                            <form
                                onSubmit={handleSubmit}
                            >

                                {/* =================================
                                    SHIPPING ADDRESS
                                ================================= */}

                                <div className="mb-4">

                                    <label
                                        htmlFor="shipping_address"
                                        className="form-label fw-semibold"
                                    >
                                        Shipping Address
                                    </label>

                                    <textarea
                                        id="shipping_address"
                                        className="form-control"
                                        rows="4"
                                        name="shipping_address"
                                        value={
                                            formData.shipping_address
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        placeholder="Enter your complete delivery address"
                                        required
                                    />

                                </div>


                                {/* =================================
                                    PAYMENT METHOD
                                ================================= */}

                                <div className="mb-4">

                                    <label
                                        htmlFor="payment_method"
                                        className="form-label fw-semibold"
                                    >
                                        Payment Method
                                    </label>

                                    <select
                                        id="payment_method"
                                        className="form-select"
                                        name="payment_method"
                                        value={
                                            formData.payment_method
                                        }
                                        onChange={
                                            handleChange
                                        }
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


                                {/* =================================
                                    REAL CART TOTAL
                                ================================= */}

                                <div className="mb-4">

                                    <label className="form-label fw-semibold">
                                        Order Total
                                    </label>

                                    <div className="form-control bg-light">

                                        <strong>
                                            ৳
                                            {Number(
                                                cart.total_amount || 0
                                            ).toFixed(2)}
                                        </strong>

                                    </div>

                                    <small className="text-muted">
                                        Calculated from your
                                        current cart.
                                    </small>

                                </div>


                                {/* =================================
                                    BUTTONS
                                ================================= */}

                                <div className="d-flex gap-2">

                                    <button
                                        type="submit"
                                        className="btn btn-success"
                                        disabled={
                                            placingOrder
                                        }
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
                                        disabled={
                                            placingOrder
                                        }
                                        onClick={() =>
                                            navigate("/cart")
                                        }
                                    >
                                        Back to Cart
                                    </button>

                                </div>

                            </form>

                        </div>

                    </div>

                </div>


                {/* =================================================
                    ORDER SUMMARY
                ================================================= */}

                <div className="col-lg-5">

                    <div className="card shadow">

                        <div className="card-header bg-dark text-white">

                            <h5 className="mb-0">
                                Order Summary
                            </h5>

                        </div>


                        <div className="card-body">

                            {cart.items.map(
                                (item) => (

                                    <div
                                        key={item.id}
                                        className="d-flex justify-content-between border-bottom py-3"
                                    >

                                        <div>

                                            <strong>
                                                {
                                                    item.product?.name
                                                }
                                            </strong>

                                            <div className="text-muted small">
                                                Qty:{" "}
                                                {
                                                    item.quantity
                                                }
                                            </div>

                                        </div>


                                        <div className="fw-semibold">

                                            ৳
                                            {Number(
                                                item.subtotal || 0
                                            ).toFixed(2)}

                                        </div>

                                    </div>
                                )
                            )}


                            {/* =================================
                                TOTAL
                            ================================= */}

                            <div className="d-flex justify-content-between mt-4">

                                <h5>
                                    Total
                                </h5>

                                <h5 className="text-primary">

                                    ৳
                                    {Number(
                                        cart.total_amount || 0
                                    ).toFixed(2)}

                                </h5>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};


export default Checkout;
```
