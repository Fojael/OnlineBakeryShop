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
        useState("cod");

    const [error, setError] =
        useState("");


    // ==========================================================
    // LOAD CHECKOUT DATA
    // ==========================================================

    useEffect(() => {
        let mounted = true;

        const loadCheckout = async () => {
            try {
                setLoading(true);
                setError("");

                // ==================================================
                // LOAD CART
                // ==================================================

                const cartResponse =
                    await getCart();

                const cartData =
                    cartResponse.data;


                // ==================================================
                // LOAD ADDRESSES
                // ==================================================

                const addressResponse =
                    await getAddresses();

                const addressList =
                    Array.isArray(
                        addressResponse.data
                    )
                        ? addressResponse.data
                        : [];


                if (!mounted) {
                    return;
                }


                setCart(cartData);

                setAddresses(
                    addressList
                );


                // ==================================================
                // SELECT DEFAULT ADDRESS
                // ==================================================

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

                    // No default address.
                    // Select the first available address.

                    setSelectedAddress(
                        addressList[0].id
                    );

                } else {

                    // No addresses available.

                    setSelectedAddress(
                        null
                    );
                }

            } catch (error) {

                console.error(
                    "Checkout loading error:",
                    error
                );


                if (mounted) {

                    setError(
                        "Unable to load checkout information."
                    );

                    toast.error(
                        error?.response?.data?.detail ||
                        "Unable to load checkout information."
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
    // CALCULATE SUBTOTAL
    // ==========================================================

    const subtotal =
        cartItems.reduce(
            (total, item) => {

                const price =
                    Number(
                        item.product_price ??
                        item.price ??
                        item.product?.price ??
                        0
                    );

                const quantity =
                    Number(
                        item.quantity ?? 0
                    );

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
        subtotal > 0
            ? 60
            : 0;


    // ==========================================================
    // GRAND TOTAL
    // ==========================================================

    const grandTotal =
        subtotal +
        deliveryCharge;


    // ==========================================================
    // SELECTED ADDRESS
    // ==========================================================

    const selectedAddressData =
        addresses.find(
            (address) =>
                address.id === selectedAddress
        );


    // ==========================================================
    // PLACE ORDER
    // ==========================================================

    const handlePlaceOrder = async () => {

        // ==================================================
        // CHECK ADDRESS
        // ==================================================

        if (!selectedAddress) {

            toast.error(
                "Please select a delivery address."
            );

            return;
        }


        // ==================================================
        // CHECK CART
        // ==================================================

        if (cartItems.length === 0) {

            toast.error(
                "Your cart is empty."
            );

            return;
        }


        // ==================================================
        // CHECK PAYMENT
        // ==================================================

        if (!paymentMethod) {

            toast.error(
                "Please select a payment method."
            );

            return;
        }


        try {

            setPlacingOrder(true);


            // ==================================================
            // ORDER DATA
            // ==================================================

            const orderData = {
                address_id: selectedAddress,
                payment_method: paymentMethod,
            };


            console.log(
                "Creating order:",
                orderData
            );


            // ==================================================
            // CREATE ORDER
            // ==================================================

            const response =
                await createOrder(
                    orderData
                );


            console.log(
                "Order response:",
                response.data
            );


            toast.success(
                "Order placed successfully!"
            );


            // ==================================================
            // REDIRECT
            // ==================================================

            if (response?.data?.id) {

                navigate(
                    `/orders/${response.data.id}`
                );

            } else {

                navigate(
                    "/orders"
                );

            }

        } catch (error) {

            console.error(
                "Place order error:",
                error
            );


            const backendError =
                error?.response?.data;


            // ==================================================
            // BACKEND ERROR
            // ==================================================

            if (
                backendError?.detail
            ) {

                toast.error(
                    backendError.detail
                );

            } else if (
                typeof backendError === "object"
            ) {

                const firstError =
                    Object.values(
                        backendError
                    )[0];


                if (
                    Array.isArray(
                        firstError
                    )
                ) {

                    toast.error(
                        firstError[0]
                    );

                } else {

                    toast.error(
                        String(firstError)
                    );

                }

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

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="mb-4">

                <h2 className="fw-bold">
                    🛒 Checkout
                </h2>

                <p className="text-muted">
                    Complete your order by selecting
                    your delivery address and payment method.
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
                        ADDRESS
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

                                <div className="text-center py-4">

                                    <h5>
                                        No Delivery Address
                                    </h5>

                                    <p className="text-muted">
                                        Please add a delivery address
                                        before placing your order.
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
                                                key={
                                                    address.id
                                                }
                                            >

                                                <div
                                                    className={`card h-100 ${
                                                        selectedAddress ===
                                                        address.id
                                                            ? "border-primary"
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
                                                                className="form-check-label w-100"
                                                                htmlFor={`address-${address.id}`}
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

                                        )
                                    )}

                                </div>

                            )}

                        </div>

                    </div>


                    {/* ==================================================
                        PAYMENT
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
                                className={`card mb-3 ${
                                    paymentMethod === "cod"
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
                                            id="payment-cod"
                                            value="cod"
                                            checked={
                                                paymentMethod ===
                                                "cod"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="payment-cod"
                                        >

                                            <strong>
                                                💵 Cash on Delivery
                                            </strong>

                                            <div className="text-muted small">
                                                Pay when your order is delivered.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>


                            {/* SSLCommerz */}

                            <div
                                className={`card ${
                                    paymentMethod === "sslcommerz"
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
                                            id="payment-ssl"
                                            value="sslcommerz"
                                            checked={
                                                paymentMethod ===
                                                "sslcommerz"
                                            }
                                            onChange={(e) =>
                                                setPaymentMethod(
                                                    e.target.value
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="payment-ssl"
                                        >

                                            <strong>
                                                💳 Online Payment
                                            </strong>

                                            <div className="text-muted small">
                                                Pay securely using SSLCommerz.
                                            </div>

                                        </label>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>


                    {/* ==================================================
                        SELECTED ADDRESS PREVIEW
                    ================================================== */}

                    {selectedAddressData && (

                        <div className="alert alert-info">

                            <strong>
                                Delivery to:
                            </strong>

                            <br />

                            {
                                selectedAddressData.full_name
                            }

                            <br />

                            {
                                selectedAddressData.address_line
                            }

                            ,{" "}
                            {
                                selectedAddressData.district
                            }

                        </div>

                    )}

                </div>


                {/* ==================================================
                    RIGHT SIDE
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

                            {/* ==================================================
                                ITEMS
                            ================================================== */}

                            {cartItems.map(
                                (item) => {

                                    const price =
                                        Number(
                                            item.product_price ??
                                            item.price ??
                                            item.product?.price ??
                                            0
                                        );

                                    const quantity =
                                        Number(
                                            item.quantity ?? 0
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
                                                        item.product?.name ??
                                                        "Product"
                                                    }
                                                </strong>

                                                <div className="text-muted small">
                                                    Qty: {quantity}
                                                </div>

                                            </div>


                                            <span>

                                                ৳{" "}
                                                {(
                                                    price *
                                                    quantity
                                                ).toFixed(2)}

                                            </span>

                                        </div>

                                    );
                                }
                            )}


                            <hr />


                            {/* ==================================================
                                SUBTOTAL
                            ================================================== */}

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Subtotal
                                </span>

                                <strong>
                                    ৳{" "}
                                    {subtotal.toFixed(2)}
                                </strong>

                            </div>


                            {/* ==================================================
                                DELIVERY
                            ================================================== */}

                            <div className="d-flex justify-content-between mb-2">

                                <span>
                                    Delivery
                                </span>

                                <strong>
                                    ৳{" "}
                                    {deliveryCharge.toFixed(2)}
                                </strong>

                            </div>


                            <hr />


                            {/* ==================================================
                                TOTAL
                            ================================================== */}

                            <div className="d-flex justify-content-between mb-4">

                                <h5>
                                    Total
                                </h5>

                                <h5 className="text-primary">
                                    ৳{" "}
                                    {grandTotal.toFixed(2)}
                                </h5>

                            </div>


                            {/* ==================================================
                                PLACE ORDER
                            ================================================== */}

                            <button
                                type="button"
                                className="btn btn-primary w-100 py-3"
                                disabled={
                                    placingOrder ||
                                    !selectedAddress
                                }
                                onClick={
                                    handlePlaceOrder
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