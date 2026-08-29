import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    createOrder,
} from "../../services/orderService";

import {
    createPayment,
    redirectToGateway,
} from "../../services/paymentService";


const Checkout = () => {

    const navigate =
        useNavigate();


    const [
        shippingAddress,
        setShippingAddress,
    ] = useState("");


    const [
        paymentMethod,
        setPaymentMethod,
    ] = useState(
        "Cash on Delivery"
    );


    const [
        loading,
        setLoading,
    ] = useState(false);


    const [
        error,
        setError,
    ] = useState("");


    // ======================================================
    // SUBMIT
    // ======================================================

    const handleSubmit = async (
        event
    ) => {

        event.preventDefault();


        // --------------------------------------------------
        // Validate address
        // --------------------------------------------------

        if (
            !shippingAddress.trim()
        ) {

            setError(
                "Shipping address is required."
            );

            return;
        }


        try {

            setLoading(true);

            setError("");


            // ------------------------------------------------
            // Create order
            // ------------------------------------------------

            const orderResponse =
                await createOrder({

                    shipping_address:
                        shippingAddress.trim(),

                    payment_method:
                        paymentMethod,
                });


            const order =
                orderResponse.order;


            if (!order) {

                throw new Error(
                    "Order was not returned by the server."
                );
            }


            // =================================================
            // COD
            // =================================================

            if (
                paymentMethod ===
                "Cash on Delivery"
            ) {

                localStorage.removeItem(
                    "cart"
                );

                localStorage.removeItem(
                    "checkout"
                );


                navigate(
                    `/payment/success?order_id=${order.id}&cod=1`
                );


                return;
            }


            // =================================================
            // ONLINE PAYMENT
            // =================================================

            const paymentResponse =
                await createPayment(
                    order.id
                );


            if (
                !paymentResponse?.gateway_url
            ) {

                throw new Error(
                    "Payment gateway URL was not returned."
                );
            }


            localStorage.setItem(
                "pending_payment_order_id",
                String(order.id)
            );


            redirectToGateway(
                paymentResponse.gateway_url
            );

        } catch (err) {

            console.error(
                "Checkout error:",
                err
            );


            const data =
                err?.response?.data;


            const message =
                data?.detail ||
                data?.message ||
                data?.error ||
                err?.message ||
                "Could not start checkout.";


            setError(
                message
            );

        } finally {

            setLoading(false);
        }
    };


    // ======================================================
    // UI
    // ======================================================

    return (

        <div className="container py-4">

            <h2 className="mb-4">
                Checkout
            </h2>


            {error && (

                <div className="alert alert-danger">

                    {error}

                </div>
            )}


            <form
                onSubmit={
                    handleSubmit
                }
            >

                {/* ==========================================
                    SHIPPING ADDRESS
                =========================================== */}

                <div className="mb-3">

                    <label
                        className="form-label"
                        htmlFor="shipping-address"
                    >
                        Shipping Address
                    </label>


                    <textarea
                        id="shipping-address"
                        className="form-control"
                        rows="4"
                        value={
                            shippingAddress
                        }
                        onChange={
                            (event) =>
                                setShippingAddress(
                                    event.target.value
                                )
                        }
                        required
                    />

                </div>


                {/* ==========================================
                    PAYMENT METHOD
                =========================================== */}

                <div className="mb-3">

                    <label
                        className="form-label"
                        htmlFor="payment-method"
                    >
                        Payment Method
                    </label>


                    <select
                        id="payment-method"
                        className="form-select"
                        value={
                            paymentMethod
                        }
                        onChange={
                            (event) =>
                                setPaymentMethod(
                                    event.target.value
                                )
                        }
                    >

                        <option
                            value="Cash on Delivery"
                        >
                            Cash on Delivery
                        </option>


                        <option
                            value="SSLCommerz"
                        >
                            SSLCommerz
                        </option>

                    </select>

                </div>


                {/* ==========================================
                    SUBMIT
                =========================================== */}

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                >

                    {loading
                        ? "Processing..."
                        : "Place Order"
                    }

                </button>

            </form>

        </div>
    );
};


export default Checkout;