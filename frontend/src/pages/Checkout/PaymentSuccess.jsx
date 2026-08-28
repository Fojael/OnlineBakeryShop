import {
    useEffect,
    useState,
} from "react";

import {
    Link,
    useNavigate,
    useSearchParams,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    checkPaymentStatus,
    getOrderId,
    getTransactionId,
} from "../../services/paymentService";


const PaymentSuccess = () => {

    const navigate = useNavigate();

    const [searchParams] =
        useSearchParams();

    const [loading, setLoading] =
        useState(true);

    const [payment, setPayment] =
        useState(null);

    const [error, setError] =
        useState("");


    // =========================================================
    // PAYMENT ID
    // =========================================================

    const paymentId =
        searchParams.get("payment_id") ||
        searchParams.get("paymentId") ||
        searchParams.get("id");


    // =========================================================
    // CHECK PAYMENT
    // =========================================================

    useEffect(() => {

        let mounted = true;


        const verifyPayment = async () => {

            if (!paymentId) {

                if (mounted) {

                    setError(
                        "Payment information was not found."
                    );

                    setLoading(false);

                }

                return;

            }


            try {

                setLoading(true);

                setError("");


                const response =
                    await checkPaymentStatus(
                        paymentId
                    );


                if (!mounted) {
                    return;
                }


                const paymentData =
                    response?.data || {};


                setPayment(
                    paymentData
                );


                toast.success(
                    "Payment completed successfully!"
                );


            } catch (err) {

                console.error(
                    "Payment verification error:",
                    err
                );


                if (!mounted) {
                    return;
                }


                setError(
                    err?.response?.data?.detail ||
                    err?.response?.data?.message ||
                    "Unable to verify payment."
                );


                toast.error(
                    err?.response?.data?.detail ||
                    err?.response?.data?.message ||
                    "Unable to verify payment."
                );

            } finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        };


        void verifyPayment();


        return () => {

            mounted = false;

        };

    }, [paymentId]);


    // =========================================================
    // EXTRACT ORDER / TRANSACTION
    // =========================================================

    const orderId =
        getOrderId(payment);

    const transactionId =
        getTransactionId(payment);


    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {

        return (

            <div className="container py-5">

                <div className="card border-0 shadow-sm">

                    <div className="card-body text-center py-5">

                        <div
                            className="spinner-border text-success"
                            role="status"
                        >
                            <span className="visually-hidden">
                                Verifying payment...
                            </span>
                        </div>

                        <h4 className="mt-4">
                            Verifying Payment...
                        </h4>

                        <p className="text-muted mb-0">
                            Please wait while we confirm
                            your payment.
                        </p>

                    </div>

                </div>

            </div>

        );

    }


    // =========================================================
    // ERROR
    // =========================================================

    if (error) {

        return (

            <div className="container py-5">

                <div className="card border-0 shadow-sm">

                    <div className="card-body text-center py-5">

                        <div
                            className="display-1 text-danger"
                        >
                            ✕
                        </div>

                        <h2 className="mt-3">
                            Payment Verification Failed
                        </h2>

                        <p className="text-muted">
                            {error}
                        </p>

                        <div className="d-flex justify-content-center gap-2">

                            <button
                                type="button"
                                className="btn btn-primary"
                                onClick={() =>
                                    navigate("/checkout")
                                }
                            >
                                Back to Checkout
                            </button>

                            <Link
                                to="/orders"
                                className="btn btn-outline-secondary"
                            >
                                My Orders
                            </Link>

                        </div>

                    </div>

                </div>

            </div>

        );

    }


    // =========================================================
    // SUCCESS PAGE
    // =========================================================

    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card border-0 shadow-sm">

                        <div className="card-body text-center py-5">

                            <div
                                className="display-1 text-success"
                            >
                                ✓
                            </div>

                            <h1 className="fw-bold mt-3">
                                Payment Successful!
                            </h1>

                            <p className="text-muted">
                                Your payment has been
                                successfully processed.
                            </p>


                            {/* =================================
                                PAYMENT INFORMATION
                            ================================= */}

                            <div className="card bg-light mt-4">

                                <div className="card-body text-start">

                                    <h5 className="mb-3">
                                        Payment Information
                                    </h5>


                                    {paymentId && (

                                        <div className="d-flex justify-content-between mb-2">

                                            <span>
                                                Payment ID
                                            </span>

                                            <strong>
                                                {paymentId}
                                            </strong>

                                        </div>

                                    )}


                                    {orderId && (

                                        <div className="d-flex justify-content-between mb-2">

                                            <span>
                                                Order ID
                                            </span>

                                            <strong>
                                                #{orderId}
                                            </strong>

                                        </div>

                                    )}


                                    {transactionId && (

                                        <div className="d-flex justify-content-between">

                                            <span>
                                                Transaction ID
                                            </span>

                                            <strong>
                                                {transactionId}
                                            </strong>

                                        </div>

                                    )}

                                </div>

                            </div>


                            {/* =================================
                                ACTIONS
                            ================================= */}

                            <div className="d-flex flex-column flex-sm-row justify-content-center gap-2 mt-4">

                                {orderId ? (

                                    <Link
                                        to={`/orders/${orderId}`}
                                        className="btn btn-success btn-lg"
                                    >
                                        View Order
                                    </Link>

                                ) : (

                                    <Link
                                        to="/orders"
                                        className="btn btn-success btn-lg"
                                    >
                                        My Orders
                                    </Link>

                                )}


                                <Link
                                    to="/products"
                                    className="btn btn-outline-primary btn-lg"
                                >
                                    Continue Shopping
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

};


export default PaymentSuccess;