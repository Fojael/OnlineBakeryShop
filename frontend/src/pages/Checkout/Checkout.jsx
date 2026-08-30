import {
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    createOrder,
} from "../../services/orderService";

import {
    createPayment,
} from "../../services/paymentService";


const Checkout = () => {

    const navigate = useNavigate();

    // ========================================================
    // STATE
    // ========================================================

    const [
        shippingAddress,
        setShippingAddress,
    ] = useState("");

    const [
        paymentMethod,
        setPaymentMethod,
    ] = useState("Cash on Delivery");

    const [
        loading,
        setLoading,
    ] = useState(false);


    // ========================================================
    // PLACE ORDER
    // ========================================================

    const handlePlaceOrder = async () => {

        // ----------------------------------------------------
        // Validate shipping address
        // ----------------------------------------------------

        if (!shippingAddress.trim()) {

            toast.error(
                "Please enter your shipping address."
            );

            return;
        }

        // ----------------------------------------------------
        // Prevent duplicate request
        // ----------------------------------------------------

        if (loading) {
            return;
        }

        setLoading(true);

        try {

            // =================================================
            // ORDER DATA
            // =================================================

            const orderData = {
                shipping_address:
                    shippingAddress.trim(),

                payment_method:
                    paymentMethod,
            };

            console.log(
                "Sending order data:",
                orderData
            );

            // =================================================
            // CREATE ORDER
            // =================================================

            const response = await createOrder(
                orderData
            );

            console.log(
                "Complete order response:",
                response
            );

            console.log(
                "Order response data:",
                response.data
            );

            // =================================================
            // GET ORDER
            // =================================================

            const order =
                response.data?.order ||
                response.data;

            const orderId =
                order?.id ||
                response.data?.order_id ||
                response.data?.id;

            // =================================================
            // CHECK ORDER ID
            // =================================================

            if (!orderId) {

                console.error(
                    "Order ID missing. Backend returned:",
                    response.data
                );

                throw new Error(
                    "Order was created, but Order ID was not returned."
                );
            }

            console.log(
                "Created Order ID:",
                orderId
            );

            // =================================================
            // CASH ON DELIVERY
            // =================================================

            if (
                paymentMethod
                === "Cash on Delivery"
            ) {

                toast.success(
                    "Order placed successfully."
                );

                navigate(
                    `/orders/${orderId}`
                );

                return;
            }

            // =================================================
            // SSL COMMERZ
            // =================================================

            if (
                paymentMethod
                === "SSLCommerz"
            ) {

                console.log(
                    "Creating SSLCommerz payment for order:",
                    orderId
                );

                const paymentResponse =
                    await createPayment(
                        orderId
                    );

                console.log(
                    "Payment response:",
                    paymentResponse
                );

                // =================================================
                // GET GATEWAY URL
                // =================================================

                const gatewayUrl =
                    paymentResponse?.gateway_url ||
                    paymentResponse?.data?.gateway_url;

                if (!gatewayUrl) {

                    console.error(
                        "Gateway URL missing:",
                        paymentResponse
                    );

                    throw new Error(
                        "Payment gateway URL was not returned."
                    );
                }

                toast.info(
                    "Redirecting to SSLCommerz..."
                );

                // =================================================
                // REDIRECT TO SSL COMMERZ
                // =================================================

                window.location.href =
                    gatewayUrl;

                return;
            }

            // =================================================
            // UNSUPPORTED PAYMENT METHOD
            // =================================================

            throw new Error(
                "Unsupported payment method."
            );

        } catch (error) {

            console.error(
                "Checkout error:",
                error
            );

            console.error(
                "Backend error response:",
                error?.response?.data
            );

            const backendMessage =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                error?.message ||
                "Could not place order.";

            toast.error(
                backendMessage
            );

        } finally {

            setLoading(false);
        }
    };


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow-sm">

                        <div className="card-body p-4">

                            <h2 className="mb-4">
                                Checkout
                            </h2>

                            {/* ==================================
                                SHIPPING ADDRESS
                            ================================== */}

                            <div className="mb-4">

                                <label
                                    className="form-label"
                                >
                                    Shipping Address
                                </label>

                                <textarea
                                    className="form-control"
                                    rows="4"
                                    value={
                                        shippingAddress
                                    }
                                    onChange={(
                                        event
                                    ) =>
                                        setShippingAddress(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Enter your complete shipping address"
                                    disabled={loading}
                                />

                            </div>


                            {/* ==================================
                                PAYMENT METHOD
                            ================================== */}

                            <div className="mb-4">

                                <label
                                    className="form-label"
                                >
                                    Payment Method
                                </label>

                                {/* ==============================
                                    COD
                                ============================== */}

                                <div className="form-check mb-2">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="cod"
                                        value="Cash on Delivery"
                                        checked={
                                            paymentMethod
                                            ===
                                            "Cash on Delivery"
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setPaymentMethod(
                                                event.target.value
                                            )
                                        }
                                        disabled={loading}
                                    />

                                    <label
                                        className="form-check-label"
                                        htmlFor="cod"
                                    >
                                        Cash on Delivery
                                    </label>

                                </div>


                                {/* ==============================
                                    SSL COMMERZ
                                ============================== */}

                                <div className="form-check">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="sslcommerz"
                                        value="SSLCommerz"
                                        checked={
                                            paymentMethod
                                            ===
                                            "SSLCommerz"
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setPaymentMethod(
                                                event.target.value
                                            )
                                        }
                                        disabled={loading}
                                    />

                                    <label
                                        className="form-check-label"
                                        htmlFor="sslcommerz"
                                    >
                                        SSLCommerz
                                    </label>

                                </div>

                            </div>


                            {/* ==================================
                                PLACE ORDER BUTTON
                            ================================== */}

                            <button
                                type="button"
                                className="btn btn-primary w-100"
                                onClick={
                                    handlePlaceOrder
                                }
                                disabled={loading}
                            >

                                {loading
                                    ? "Processing..."
                                    : "Place Order"
                                }

                            </button>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};


export default Checkout;