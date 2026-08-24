import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import { getCart } from "../../services/cartService";
import { getAddresses } from "../../services/addressService";
import { createOrder } from "../../services/orderService";

const Checkout = () => {
    const navigate = useNavigate();

    // ==========================================================
    // STATE
    // ==========================================================

    const [loading, setLoading] = useState(true);

    const [placingOrder, setPlacingOrder] =
        useState(false);

    const [cart, setCart] = useState(null);

    const [addresses, setAddresses] =
        useState([]);

    const [selectedAddress, setSelectedAddress] =
        useState(null);

    const [paymentMethod, setPaymentMethod] =
        useState("Cash on Delivery");

    const [error, setError] =
        useState("");

    // ==========================================================
    // LOAD CHECKOUT
    // ==========================================================

    useEffect(() => {
        let mounted = true;

        const loadCheckout = async () => {
            try {
                setLoading(true);
                setError("");

                const cartResponse =
                    await getCart();

                const addressResponse =
                    await getAddresses();

                if (!mounted) return;

                const cartData =
                    cartResponse.data;

                const addressList =
                    Array.isArray(
                        addressResponse.data
                    )
                        ? addressResponse.data
                        : [];

                setCart(cartData);
                setAddresses(addressList);

                const defaultAddress =
                    addressList.find(
                        (a) => a.is_default
                    );

                if (defaultAddress) {
                    setSelectedAddress(
                        defaultAddress.id
                    );
                } else if (
                    addressList.length > 0
                ) {
                    setSelectedAddress(
                        addressList[0].id
                    );
                }
            } catch (err) {
                console.error(err);

                if (mounted) {
                    setError(
                        "Unable to load checkout."
                    );

                    toast.error(
                        err?.response?.data
                            ?.detail ||
                            "Unable to load checkout."
                    );
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadCheckout();

        return () => {
            mounted = false;
        };
    }, []);

    // ==========================================================
    // CART ITEMS
    // ==========================================================

    const cartItems =
        Array.isArray(cart?.items)
            ? cart.items
            : [];

    // ==========================================================
    // SUBTOTAL
    // ==========================================================

    const subtotal = cartItems.reduce(
        (total, item) => {
            const price = Number(
                item.product_price ??
                    item.price ??
                    item.product?.price ??
                    0
            );

            return (
                total +
                price *
                    Number(item.quantity)
            );
        },
        0
    );

    // ==========================================================
    // DELIVERY
    // ==========================================================

    const deliveryCharge =
        subtotal > 0 ? 60 : 0;

    // ==========================================================
    // GRAND TOTAL
    // ==========================================================

    const grandTotal =
        subtotal + deliveryCharge;

    // ==========================================================
    // SELECTED ADDRESS
    // ==========================================================

    const selectedAddressData =
        addresses.find(
            (address) =>
                address.id ===
                selectedAddress
        );
            // ==========================================================
    // PLACE ORDER
    // ==========================================================

    const handlePlaceOrder = async () => {
        // ------------------------------------------------------
        // Validate Address
        // ------------------------------------------------------

        if (!selectedAddressData) {
            toast.error(
                "Please select a delivery address."
            );
            return;
        }

        // ------------------------------------------------------
        // Validate Cart
        // ------------------------------------------------------

        if (cartItems.length === 0) {
            toast.error("Your cart is empty.");
            return;
        }

        // ------------------------------------------------------
        // Build Shipping Address
        // ------------------------------------------------------

        const shippingAddress = `
${selectedAddressData.full_name}
${selectedAddressData.phone}
${selectedAddressData.address_line}
${selectedAddressData.upazila}, ${selectedAddressData.district}
${selectedAddressData.division} - ${selectedAddressData.postal_code}
        `.trim();

        // ------------------------------------------------------
        // Request Body
        // Must match Django backend exactly
        // ------------------------------------------------------

        const orderData = {
            shipping_address: shippingAddress,
            payment_method: paymentMethod,
        };

        try {
            setPlacingOrder(true);

            const response =
                await createOrder(orderData);

            toast.success(
                response.data.message ||
                    "Order placed successfully."
            );

            // ----------------------------------------------
            // Redirect
            // ----------------------------------------------

            if (
                response.data.order &&
                response.data.order.id
            ) {
                navigate("/orders");
            } else {
                navigate("/orders");
            }
        } catch (error) {
            console.error(error);

            const backendError =
                error?.response?.data;

            if (backendError?.detail) {
                toast.error(
                    backendError.detail
                );
            } else {
                toast.error(
                    "Unable to place order."
                );
            }
        } finally {
            setPlacingOrder(false);
        }
    };

    // ==========================================================
    // LOADING
    // ==========================================================

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

    // ==========================================================
    // EMPTY CART
    // ==========================================================

    if (cartItems.length === 0) {
        return (
            <div className="container py-5">
                <div className="card shadow-sm border-0">
                    <div className="card-body text-center py-5">
                        <h1>🛒</h1>

                        <h3>
                            Your Cart is Empty
                        </h3>

                        <p className="text-muted">
                            Add some bakery
                            products before
                            checkout.
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
        // ==========================================================
    // PAGE
    // ==========================================================

    return (
        <div className="container py-5">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="mb-4">

                <h2 className="fw-bold">
                    🛒 Checkout
                </h2>

                <p className="text-muted">
                    Complete your order by selecting your
                    delivery address and payment method.
                </p>

            </div>

            {/* ==================================================
                ERROR
            ================================================== */}

            {error && (
                <div className="alert alert-danger">
                    {error}
                </div>
            )}

            <div className="row g-4">

                {/* ==================================================
                    LEFT SIDE
                ================================================== */}

                <div className="col-lg-8">

                    {/* ==================================================
                        DELIVERY ADDRESS
                    ================================================== */}

                    <div className="card border-0 shadow-sm mb-4">

                        <div className="card-header bg-white">

                            <div className="d-flex justify-content-between align-items-center">

                                <h4 className="mb-0">
                                    📍 Delivery Address
                                </h4>

                                <Link
                                    to="/address/add"
                                    className="btn btn-sm btn-outline-primary"
                                >
                                    + Add Address
                                </Link>

                            </div>

                        </div>

                        <div className="card-body">

                            {addresses.length === 0 ? (

                                <div className="text-center py-5">

                                    <h5>
                                        No saved addresses
                                    </h5>

                                    <p className="text-muted">
                                        Please add a delivery
                                        address before placing
                                        your order.
                                    </p>

                                    <Link
                                        to="/address/add"
                                        className="btn btn-primary"
                                    >
                                        Add Address
                                    </Link>

                                </div>

                            ) : (

                                <div className="row g-3">

                                    {addresses.map((address) => (

                                        <div
                                            className="col-md-6"
                                            key={address.id}
                                        >

                                            <div
                                                className={`card h-100 ${
                                                    selectedAddress ===
                                                    address.id
                                                        ? "border-primary shadow"
                                                        : ""
                                                }`}
                                            >

                                                <div className="card-body">

                                                    <div className="form-check">

                                                        <input
                                                            className="form-check-input"
                                                            type="radio"
                                                            name="address"
                                                            id={`address-${address.id}`}
                                                            checked={
                                                                selectedAddress ===
                                                                address.id
                                                            }
                                                            onChange={() =>
                                                                setSelectedAddress(
                                                                    address.id
                                                                )
                                                            }
                                                        />

                                                        <label
                                                            htmlFor={`address-${address.id}`}
                                                            className="form-check-label w-100"
                                                        >

                                                            <div className="d-flex justify-content-between">

                                                                <strong>
                                                                    {
                                                                        address.full_name
                                                                    }
                                                                </strong>

                                                                {address.is_default && (
                                                                    <span className="badge bg-success">
                                                                        Default
                                                                    </span>
                                                                )}

                                                            </div>

                                                            <div className="mt-2 small">

                                                                <div>
                                                                    📞{" "}
                                                                    {
                                                                        address.phone
                                                                    }
                                                                </div>

                                                                <div>
                                                                    📍{" "}
                                                                    {
                                                                        address.address_line
                                                                    }
                                                                </div>

                                                                <div>
                                                                    {
                                                                        address.upazila
                                                                    }
                                                                    ,{" "}
                                                                    {
                                                                        address.district
                                                                    }
                                                                </div>

                                                                <div>
                                                                    {
                                                                        address.division
                                                                    }
                                                                    {" - "}
                                                                    {
                                                                        address.postal_code
                                                                    }
                                                                </div>

                                                            </div>

                                                        </label>

                                                    </div>

                                                </div>

                                            </div>

                                        </div>

                                    ))}

                                </div>

                            )}

                        </div>

                    </div>
                                        {/* ==================================================
                        PAYMENT METHOD
                    ================================================== */}

                    <div className="card border-0 shadow-sm mb-4">

                        <div className="card-header bg-white">

                            <h4 className="mb-0">
                                💳 Payment Method
                            </h4>

                        </div>

                        <div className="card-body">

                            {/* Cash on Delivery */}

                            <div
                                className={`card mb-3 ${
                                    paymentMethod ===
                                    "Cash on Delivery"
                                        ? "border-primary"
                                        : ""
                                }`}
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="cod"
                                            value="Cash on Delivery"
                                            checked={
                                                paymentMethod ===
                                                "Cash on Delivery"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="cod"
                                        >

                                            <strong>
                                                💵 Cash on Delivery
                                            </strong>

                                            <div className="text-muted small">
                                                Pay after receiving
                                                your order.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>

                            {/* Credit Card */}

                            <div
                                className={`card ${
                                    paymentMethod ===
                                    "Credit Card"
                                        ? "border-primary"
                                        : ""
                                }`}
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="card"
                                            value="Credit Card"
                                            checked={
                                                paymentMethod ===
                                                "Credit Card"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="card"
                                        >

                                            <strong>
                                                💳 Credit Card
                                            </strong>

                                            <div className="text-muted small">
                                                Secure online payment.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                    {/* ==================================================
                        ADDRESS PREVIEW
                    ================================================== */}

                    {selectedAddressData && (

                        <div className="alert alert-info">

                            <strong>
                                Delivering To:
                            </strong>

                            <br />

                            {selectedAddressData.full_name}

                            <br />

                            {selectedAddressData.phone}

                            <br />

                            {selectedAddressData.address_line}

                            <br />

                            {selectedAddressData.upazila},{" "}
                            {selectedAddressData.district}

                            <br />

                            {selectedAddressData.division}
                            {" - "}
                            {selectedAddressData.postal_code}

                        </div>

                    )}

                </div>

                {/* ==================================================
                    ORDER SUMMARY
                ================================================== */}

                <div className="col-lg-4">

                    <div
                        className="card border-0 shadow-sm"
                        style={{
                            position: "sticky",
                            top: "20px",
                        }}
                    >

                        <div className="card-header bg-primary text-white">

                            <h4 className="mb-0">
                                📦 Order Summary
                            </h4>

                        </div>

                        <div className="card-body">

                            {cartItems.map((item) => {

                                const price = Number(
                                    item.product_price ??
                                    item.price ??
                                    item.product?.price ??
                                    0
                                );

                                return (

                                    <div
                                        key={item.id}
                                        className="d-flex justify-content-between mb-3"
                                    >

                                        <div>

                                            <strong>
                                                {
                                                    item.product_name ??
                                                    item.product?.name
                                                }
                                            </strong>

                                            <div className="small text-muted">
                                                Qty: {item.quantity}
                                            </div>

                                        </div>

                                        <strong>
                                            ৳
                                            {(
                                                price *
                                                item.quantity
                                            ).toFixed(2)}
                                        </strong>

                                    </div>

                                );

                            })}

                            <hr />

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Subtotal
                                </span>

                                <strong>
                                    ৳
                                    {subtotal.toFixed(2)}
                                </strong>

                            </div>

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Delivery
                                </span>

                                <strong>
                                    ৳
                                    {deliveryCharge.toFixed(2)}
                                </strong>

                            </div>

                            <hr />

                            <div className="d-flex justify-content-between">

                                <h5>
                                    Total
                                </h5>

                                <h5 className="text-primary">
                                    ৳
                                    {grandTotal.toFixed(2)}
                                </h5>

                            </div>

                            <button
                                className="btn btn-primary w-100 mt-4"
                                onClick={
                                    handlePlaceOrder
                                }
                                disabled={
                                    placingOrder ||
                                    !selectedAddress
                                }
                            >

                                {placingOrder
                                    ? "Placing Order..."
                                    : "🛍 Place Order"}

                            </button>

                            <Link
                                to="/cart"
                                className="btn btn-outline-secondary w-100 mt-2"
                            >
                                ← Back to Cart
                            </Link>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Checkout;