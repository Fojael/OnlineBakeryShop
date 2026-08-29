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

        if (!shippingAddress.trim()) {

            toast.error(
                "Please enter your shipping address."
            );

            return;
        }


        if (loading) {
            return;
        }


        setLoading(true);


        try {

            // ==================================================
            // CREATE ORDER
            // ==================================================

            const orderResponse =
                await createOrder({

                    shipping_address:
                        shippingAddress.trim(),

                    payment_method:
                        paymentMethod,

                });


            const order =
                orderResponse.order;


            if (!order || !order.id) {

                throw new Error(
                    "Order ID was not returned."
                );
            }


            // ==================================================
            // CASH ON DELIVERY
            // ==================================================

            if (
                paymentMethod ===
                "Cash on Delivery"
            ) {

                toast.success(
                    "Order placed successfully."
                );


                navigate(
                    `/orders/${order.id}`
                );


                return;
            }


            // ==================================================
            // SSLCOMMERZ
            // ==================================================

            if (
                paymentMethod ===
                "SSLCommerz"
            ) {

                const paymentResponse =
                    await createPayment(
                        order.id
                    );


                if (
                    paymentResponse &&
                    paymentResponse.gateway_url
                ) {

                    toast.info(
                        "Redirecting to SSLCommerz..."
                    );


                    window.location.href =
                        paymentResponse.gateway_url;


                    return;
                }


                throw new Error(
                    "Payment gateway URL was not returned."
                );
            }


            // ==================================================
            // UNSUPPORTED METHOD
            // ==================================================

            throw new Error(
                "Unsupported payment method."
            );

        } catch (error) {

            console.error(
                "Order creation error:",
                error
            );


            const message =
                error?.response?.data?.detail
                ||
                error?.message
                ||
                "Could not place order.";


            toast.error(
                message
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
                                    onChange={(event) =>
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


                                {/* COD */}

                                <div className="form-check mb-2">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="cod"
                                        value="Cash on Delivery"
                                        checked={
                                            paymentMethod ===
                                            "Cash on Delivery"
                                        }
                                        onChange={(event) =>
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


                                {/* SSLCommerz */}

                                <div className="form-check">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="sslcommerz"
                                        value="SSLCommerz"
                                        checked={
                                            paymentMethod ===
                                            "SSLCommerz"
                                        }
                                        onChange={(event) =>
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