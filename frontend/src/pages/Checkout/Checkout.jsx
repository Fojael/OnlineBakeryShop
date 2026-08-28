import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import { getCart } from "../../services/cartService";
import { getAddresses } from "../../services/addressService";
import { createOrder } from "../../services/orderService";

import {
    createPayment,
    getPaymentRedirectUrl,
    getPaymentId,
    getPaymentErrorMessage,
} from "../../services/paymentService";


const Checkout = () => {

    const navigate = useNavigate();

    // ==========================================================
    // STATE
    // ==========================================================

    const [loading, setLoading] = useState(true);
    const [placingOrder, setPlacingOrder] = useState(false);

    const [cart, setCart] = useState(null);
    const [addresses, setAddresses] = useState([]);

    const [selectedAddress, setSelectedAddress] = useState(null);

    const [paymentMethod, setPaymentMethod] =
        useState("Cash on Delivery");

    const [error, setError] = useState("");


    // ==========================================================
    // LOAD CHECKOUT DATA
    // ==========================================================

    useEffect(() => {

        let mounted = true;

        const loadCheckout = async () => {

            try {

                setLoading(true);
                setError("");

                // --------------------------------------------------
                // LOAD CART
                // --------------------------------------------------

                const cartResponse = await getCart();

                const cartData =
                    cartResponse?.data ?? null;


                // --------------------------------------------------
                // LOAD ADDRESSES
                // --------------------------------------------------

                const addressResponse =
                    await getAddresses();

                const addressList =
                    Array.isArray(addressResponse?.data)
                        ? addressResponse.data
                        : [];


                if (!mounted) {
                    return;
                }


                setCart(cartData);
                setAddresses(addressList);


                // --------------------------------------------------
                // SELECT DEFAULT ADDRESS
                // --------------------------------------------------

                const defaultAddress =
                    addressList.find(
                        (address) =>
                            address.is_default === true
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

                } else {

                    setSelectedAddress(null);

                }

            } catch (err) {

                console.error(
                    "Checkout loading error:",
                    err
                );


                if (mounted) {

                    const message =
                        err?.response?.data?.detail ||
                        err?.response?.data?.message ||
                        "Unable to load checkout information.";

                    setError(message);

                    toast.error(message);
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
    // GET ITEM PRICE
    // ==========================================================

    const getItemPrice = (item) => {

        return Number(
            item?.product_price ??
            item?.price ??
            item?.product?.price ??
            0
        );

    };


    // ==========================================================
    // GET ITEM QUANTITY
    // ==========================================================

    const getItemQuantity = (item) => {

        return Number(
            item?.quantity ?? 0
        );

    };


    // ==========================================================
    // CALCULATE SUBTOTAL
    // ==========================================================

    const subtotal =
        cartItems.reduce(
            (total, item) => {

                const price =
                    getItemPrice(item);

                const quantity =
                    getItemQuantity(item);

                return (
                    total +
                    price * quantity
                );

            },
            0
        );


    // ==========================================================
    // DELIVERY CHARGE
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
                address.id === selectedAddress
        );


    // ==========================================================
    // BUILD SHIPPING ADDRESS
    // ==========================================================

    const buildShippingAddress = () => {

        if (!selectedAddressData) {
            return "";
        }

        const address =
            selectedAddressData;


        return [

            address.full_name,

            address.phone,

            address.address_line,

            address.upazila,

            address.district,

            address.division,

            address.postal_code,

        ]
            .filter(
                (value) =>
                    value !== null &&
                    value !== undefined &&
                    String(value).trim() !== ""
            )
            .join(", ");
    };


    // ==========================================================
    // SAVE PENDING PAYMENT
    // ==========================================================

    const savePendingPayment = ({
        paymentId,
        orderId,
        paymentMethod,
        paymentUrl,
    }) => {

        if (paymentId) {

            sessionStorage.setItem(
                "pending_payment_id",
                String(paymentId)
            );

        }


        if (orderId) {

            sessionStorage.setItem(
                "pending_order_id",
                String(orderId)
            );

        }


        if (paymentMethod) {

            sessionStorage.setItem(
                "pending_payment_method",
                paymentMethod
            );

        }


        if (paymentUrl) {

            sessionStorage.setItem(
                "pending_payment_url",
                paymentUrl
            );

        }

    };


    // ==========================================================
    // PLACE ORDER
    // ==========================================================

    const handlePlaceOrder = async () => {

        // ------------------------------------------------------
        // PREVENT DOUBLE CLICK
        // ------------------------------------------------------

        if (placingOrder) {
            return;
        }


        // ------------------------------------------------------
        // CHECK ADDRESS
        // ------------------------------------------------------

        if (!selectedAddressData) {

            toast.error(
                "Please select a delivery address."
            );

            return;
        }


        // ------------------------------------------------------
        // CHECK CART
        // ------------------------------------------------------

        if (cartItems.length === 0) {

            toast.error(
                "Your cart is empty."
            );

            return;
        }


        // ------------------------------------------------------
        // BUILD SHIPPING ADDRESS
        // ------------------------------------------------------

        const shippingAddress =
            buildShippingAddress();


        if (!shippingAddress) {

            toast.error(
                "Please provide a valid delivery address."
            );

            return;
        }


        try {

            setPlacingOrder(true);
            setError("");


            // ==================================================
            // STEP 1: CREATE ORDER
            // ==================================================

            const orderData = {

                shipping_address:
                    shippingAddress,

                payment_method:
                    paymentMethod,

            };


            console.log(
                "Creating order:",
                orderData
            );


            const orderResponse =
                await createOrder(
                    orderData
                );


            console.log(
                "Order response:",
                orderResponse?.data
            );


            // ==================================================
            // GET ORDER ID
            // ==================================================

            const orderId =
                orderResponse?.data?.order?.id ??
                orderResponse?.data?.order_id ??
                orderResponse?.data?.orderId ??
                orderResponse?.data?.id;


            if (!orderId) {

                throw new Error(
                    "Order was created but no order ID was returned by the server."
                );

            }


            console.log(
                "Created Order ID:",
                orderId
            );


            // ==================================================
            // CASH ON DELIVERY
            // ==================================================

            if (
                paymentMethod ===
                "Cash on Delivery"
            ) {

                toast.success(
                    "🎉 Order placed successfully!"
                );


                navigate(
                    `/orders/${orderId}`
                );


                return;
            }


            // ==================================================
            // ONLINE PAYMENT
            // ==================================================

            toast.info(
                "Creating secure payment session..."
            );


            // ==================================================
            // STEP 2: CREATE PAYMENT
            // IMPORTANT:
            // createPayment(orderId, paymentData)
            // ==================================================

            const paymentData = {

                payment_method:
                    paymentMethod,

            };


            console.log(
                "Creating payment:",
                {
                    orderId,
                    paymentData,
                }
            );


            const paymentResponse =
                await createPayment(
                    orderId,
                    paymentData
                );


            console.log(
                "Payment response:",
                paymentResponse?.data
            );


            // ==================================================
            // STEP 3: GET PAYMENT ID
            // ==================================================

            const paymentId =
                getPaymentId(
                    paymentResponse
                );


            console.log(
                "Payment ID:",
                paymentId
            );


            // ==================================================
            // STEP 4: GET PAYMENT URL
            // ==================================================

            const paymentUrl =
                getPaymentRedirectUrl(
                    paymentResponse
                );


            console.log(
                "Payment URL:",
                paymentUrl
            );


            // ==================================================
            // PAYMENT URL REQUIRED
            // ==================================================

            if (!paymentUrl) {

                throw new Error(
                    "Payment gateway URL was not returned by the server."
                );

            }


            // ==================================================
            // SAVE PENDING PAYMENT
            // ==================================================

            savePendingPayment({

                paymentId,

                orderId,

                paymentMethod,

                paymentUrl,

            });


            // ==================================================
            // REDIRECT TO PAYMENT GATEWAY
            // ==================================================

            console.log(
                "Redirecting to payment gateway..."
            );


            window.location.href =
                paymentUrl;


        } catch (err) {

            console.error(
                "Place order/payment error:",
                err
            );


            const message =
                getPaymentErrorMessage(
                    err
                );


            setError(message);

            toast.error(message);

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

                <div className="card border-0 shadow-sm">

                    <div className="card-body text-center py-5">

                        <h1>
                            🛒
                        </h1>

                        <h3>
                            Your Cart is Empty
                        </h3>

                        <p className="text-muted">
                            Add some bakery products
                            before checkout.
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

            {/* HEADER */}

            <div className="mb-4">

                <h2 className="fw-bold">
                    🛒 Checkout
                </h2>

                <p className="text-muted">
                    Complete your order by selecting
                    your delivery address and payment method.
                </p>

            </div>


            {/* ERROR */}

            {error && (

                <div className="alert alert-danger">

                    <strong>
                        Checkout Error:
                    </strong>{" "}

                    {error}

                </div>

            )}


            <div className="row g-4">


                {/* ==================================================
                    LEFT COLUMN
                ================================================== */}

                <div className="col-lg-8">


                    {/* ADDRESS */}

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

                                <div className="text-center py-4">

                                    <h5>
                                        No Delivery Address
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

                                    {addresses.map(
                                        (address) => (

                                            <div
                                                className="col-md-6"
                                                key={address.id}
                                            >

                                                <div
                                                    className={`card h-100 ${
                                                        selectedAddress === address.id
                                                            ? "border-primary shadow-sm"
                                                            : "border-light"
                                                    }`}
                                                    style={{
                                                        cursor: "pointer",
                                                    }}
                                                    onClick={() =>
                                                        setSelectedAddress(
                                                            address.id
                                                        )
                                                    }
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
                                                                className="form-check-label w-100"
                                                                htmlFor={`address-${address.id}`}
                                                            >

                                                                <div className="d-flex justify-content-between align-items-start">

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

                                                                        {address.upazila &&
                                                                        address.district
                                                                            ? ", "
                                                                            : ""}

                                                                        {
                                                                            address.district
                                                                        }

                                                                    </div>

                                                                    <div>

                                                                        {
                                                                            address.division
                                                                        }

                                                                        {address.division &&
                                                                        address.postal_code
                                                                            ? " - "
                                                                            : ""}

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

                                        )
                                    )}

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


                            {/* COD */}

                            <div
                                className={`card payment-card mb-3 ${
                                    paymentMethod ===
                                    "Cash on Delivery"
                                        ? "border-primary shadow-sm"
                                        : ""
                                }`}
                                style={{
                                    cursor: "pointer",
                                }}
                                onClick={() =>
                                    setPaymentMethod(
                                        "Cash on Delivery"
                                    )
                                }
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


                            {/* BKASH */}

                            <div
                                className={`card payment-card mb-3 ${
                                    paymentMethod === "bKash"
                                        ? "border-primary shadow-sm"
                                        : ""
                                }`}
                                style={{
                                    cursor: "pointer",
                                }}
                                onClick={() =>
                                    setPaymentMethod("bKash")
                                }
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="bkash"
                                            value="bKash"
                                            checked={
                                                paymentMethod ===
                                                "bKash"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="bkash"
                                        >

                                            <strong>
                                                📱 bKash
                                            </strong>

                                            <div className="text-muted small">
                                                Pay using your
                                                bKash account.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>


                            {/* NAGAD */}

                            <div
                                className={`card payment-card mb-3 ${
                                    paymentMethod === "Nagad"
                                        ? "border-primary shadow-sm"
                                        : ""
                                }`}
                                style={{
                                    cursor: "pointer",
                                }}
                                onClick={() =>
                                    setPaymentMethod("Nagad")
                                }
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="nagad"
                                            value="Nagad"
                                            checked={
                                                paymentMethod ===
                                                "Nagad"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="nagad"
                                        >

                                            <strong>
                                                📲 Nagad
                                            </strong>

                                            <div className="text-muted small">
                                                Mobile payment
                                                with Nagad.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>


                            {/* ROCKET */}

                            <div
                                className={`card payment-card mb-3 ${
                                    paymentMethod === "Rocket"
                                        ? "border-primary shadow-sm"
                                        : ""
                                }`}
                                style={{
                                    cursor: "pointer",
                                }}
                                onClick={() =>
                                    setPaymentMethod("Rocket")
                                }
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="rocket"
                                            value="Rocket"
                                            checked={
                                                paymentMethod ===
                                                "Rocket"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="rocket"
                                        >

                                            <strong>
                                                🚀 Rocket
                                            </strong>

                                            <div className="text-muted small">
                                                Pay using Rocket
                                                mobile banking.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>


                            {/* CREDIT CARD */}

                            <div
                                className={`card payment-card ${
                                    paymentMethod ===
                                    "Credit Card"
                                        ? "border-primary shadow-sm"
                                        : ""
                                }`}
                                style={{
                                    cursor: "pointer",
                                }}
                                onClick={() =>
                                    setPaymentMethod(
                                        "Credit Card"
                                    )
                                }
                            >

                                <div className="card-body">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="payment"
                                            id="credit-card"
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
                                            htmlFor="credit-card"
                                        >

                                            <strong>
                                                💳 Credit Card
                                            </strong>

                                            <div className="text-muted small">
                                                Secure online
                                                card payment.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>


                            {/* PAYMENT INFO */}

                            {paymentMethod ===
                            "Cash on Delivery" ? (

                                <div className="alert alert-success mt-3 mb-0">

                                    <strong>
                                        💵 Cash on Delivery
                                    </strong>

                                    <div className="small mt-1">
                                        Your order will be
                                        placed immediately.
                                        Pay when the order is
                                        delivered.
                                    </div>

                                </div>

                            ) : (

                                <div className="alert alert-info mt-3 mb-0">

                                    <strong>
                                        🔐 Secure Online Payment
                                    </strong>

                                    <div className="small mt-1">
                                        After clicking
                                        <strong>
                                            {" "}Pay Now
                                        </strong>
                                        , you will be redirected
                                        to the selected payment
                                        gateway.
                                    </div>

                                </div>

                            )}

                        </div>

                    </div>


                    {/* ADDRESS PREVIEW */}

                    {selectedAddressData && (

                        <div className="alert alert-info">

                            <strong>
                                Delivering To:
                            </strong>

                            <hr className="my-2" />

                            <div>
                                {
                                    selectedAddressData.full_name
                                }
                            </div>

                            <div>
                                {
                                    selectedAddressData.phone
                                }
                            </div>

                            <div>
                                {
                                    selectedAddressData.address_line
                                }
                            </div>

                            <div>

                                {
                                    selectedAddressData.upazila
                                }

                                {selectedAddressData.upazila &&
                                selectedAddressData.district
                                    ? ", "
                                    : ""}

                                {
                                    selectedAddressData.district
                                }

                            </div>

                            <div>

                                {
                                    selectedAddressData.division
                                }

                                {selectedAddressData.division &&
                                selectedAddressData.postal_code
                                    ? " - "
                                    : ""}

                                {
                                    selectedAddressData.postal_code
                                }

                            </div>

                        </div>

                    )}

                </div>


                {/* ==================================================
                    RIGHT COLUMN
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


                            {/* CART ITEMS */}

                            {cartItems.map((item) => {

                                const price =
                                    getItemPrice(item);

                                const quantity =
                                    getItemQuantity(item);


                                return (

                                    <div
                                        key={item.id}
                                        className="d-flex justify-content-between mb-3"
                                    >

                                        <div>

                                            <strong>
                                                {
                                                    item.product_name ??
                                                    item.product?.name ??
                                                    "Product"
                                                }
                                            </strong>

                                            <div className="small text-muted">
                                                Qty: {quantity}
                                            </div>

                                        </div>

                                        <strong>
                                            ৳{" "}
                                            {(
                                                price *
                                                quantity
                                            ).toFixed(2)}
                                        </strong>

                                    </div>

                                );

                            })}


                            <hr />


                            {/* COUPON */}

                            <div className="mt-3">

                                <label className="form-label fw-semibold">
                                    Coupon Code
                                </label>

                                <div className="input-group">

                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Enter coupon code"
                                        disabled
                                    />

                                    <button
                                        type="button"
                                        className="btn btn-outline-secondary"
                                        disabled
                                    >
                                        Apply
                                    </button>

                                </div>

                                <small className="text-muted">
                                    Coupon support coming soon.
                                </small>

                            </div>


                            <hr />


                            {/* SUBTOTAL */}

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Subtotal
                                </span>

                                <strong>
                                    ৳ {subtotal.toFixed(2)}
                                </strong>

                            </div>


                            {/* DELIVERY */}

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Delivery Charge
                                </span>

                                <strong>
                                    ৳ {deliveryCharge.toFixed(2)}
                                </strong>

                            </div>


                            <hr />


                            {/* GRAND TOTAL */}

                            <div className="d-flex justify-content-between">

                                <h5>
                                    Grand Total
                                </h5>

                                <h5 className="text-primary">
                                    ৳ {grandTotal.toFixed(2)}
                                </h5>

                            </div>


                            {/* SECURE CHECKOUT */}

                            <div className="alert alert-success mt-3 mb-0">

                                <strong>
                                    ✓ Secure Checkout
                                </strong>

                                <div className="small mt-1">
                                    Your order information
                                    is processed securely.
                                </div>

                            </div>


                            {/* PLACE ORDER */}

                            <button
                                type="button"
                                className="btn btn-primary btn-lg w-100 mt-4"
                                onClick={
                                    handlePlaceOrder
                                }
                                disabled={
                                    placingOrder ||
                                    !selectedAddress ||
                                    cartItems.length === 0
                                }
                            >

                                {placingOrder ? (

                                    <>

                                        <span
                                            className="spinner-border spinner-border-sm me-2"
                                            role="status"
                                            aria-hidden="true"
                                        />

                                        {paymentMethod ===
                                        "Cash on Delivery"
                                            ? "Placing Order..."
                                            : "Creating Payment..."}

                                    </>

                                ) : (

                                    paymentMethod ===
                                    "Cash on Delivery"

                                        ? (
                                            <>
                                                🛍 Place Order
                                            </>
                                        )

                                        : (
                                            <>
                                                💳 Pay Now
                                            </>
                                        )

                                )}

                            </button>


                            {/* BACK TO CART */}

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