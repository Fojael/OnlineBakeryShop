import {
    useEffect,
    useState,
} from "react";

import {
    Link,
    useNavigate,
    useSearchParams,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    checkPaymentStatus,
    getOrderId,
    getTransactionId,
    getPaymentStatus,
    isPaymentSuccessful,
    isPaymentFailed,
    isPaymentCancelled,
} from "../../services/paymentService";


const PaymentSuccess = () => {

    const navigate =
        useNavigate();


    const [
        searchParams,
    ] = useSearchParams();


    const [
        loading,
        setLoading,
    ] = useState(true);


    const [
        payment,
        setPayment,
    ] = useState(null);


    const [
        error,
        setError,
    ] = useState("");


    // ==========================================================
    // PAYMENT ID
    // ==========================================================

    const paymentId =
        searchParams.get("payment_id") ||
        searchParams.get("paymentId") ||
        searchParams.get("id") ||
        sessionStorage.getItem(
            "pending_payment_id"
        );


    // ==========================================================
    // CLEAN PENDING PAYMENT DATA
    // ==========================================================

    const clearPendingPayment =
        () => {

            sessionStorage.removeItem(
                "pending_payment_id"
            );

            sessionStorage.removeItem(
                "pending_order_id"
            );

            sessionStorage.removeItem(
                "pending_payment_method"
            );

            sessionStorage.removeItem(
                "pending_payment_url"
            );

        };


    // ==========================================================
    // VERIFY PAYMENT
    // ==========================================================

    useEffect(() => {

        let mounted = true;


        const verifyPayment =
            async () => {

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


                    // ==================================================
                    // CHECK PAYMENT WITH BACKEND
                    // ==================================================

                    const response =
                        await checkPaymentStatus(
                            paymentId
                        );


                    if (!mounted) {
                        return;
                    }


                    const paymentData =
                        response?.data ?? {};


                    setPayment(
                        paymentData
                    );


                    // ==================================================
                    // GET STATUS
                    // ==================================================

                    const status =
                        getPaymentStatus(
                            paymentData
                        );


                    console.log(
                        "Payment status:",
                        status
                    );


                    // ==================================================
                    // SUCCESS
                    // ==================================================

                    if (
                        isPaymentSuccessful(
                            status
                        )
                    ) {

                        toast.success(
                            "Payment completed successfully!"
                        );


                        clearPendingPayment();

                    }

                    // ==================================================
                    // FAILED
                    // ==================================================

                    else if (
                        isPaymentFailed(
                            status
                        )
                    ) {

                        setError(
                            "Your payment failed. Please try again."
                        );

                        toast.error(
                            "Payment failed."
                        );

                    }

                    // ==================================================
                    // CANCELLED
                    // ==================================================

                    else if (
                        isPaymentCancelled(
                            status
                        )
                    ) {

                        setError(
                            "The payment was cancelled."
                        );

                        toast.warning(
                            "Payment was cancelled."
                        );

                    }

                    // ==================================================
                    // PENDING / UNKNOWN
                    // ==================================================

                    else {

                        setError(
                            "Payment is still being processed. Please check your order status."
                        );

                        toast.info(
                            "Payment verification is still pending."
                        );

                    }


                } catch (err) {

                    console.error(
                        "Payment verification error:",
                        err
                    );


                    if (!mounted) {
                        return;
                    }


                    const message =
                        err?.response?.data?.detail ||
                        err?.response?.data?.message ||
                        "Unable to verify payment.";


                    setError(message);

                    toast.error(message);

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


    // ==========================================================
    // EXTRACT PAYMENT INFORMATION
    // ==========================================================

    const orderId =
        getOrderId(
            payment
        );


    const transactionId =
        getTransactionId(
            payment
        );


    const paymentStatus =
        getPaymentStatus(
            payment
        );


    // ==========================================================
    // LOADING
    // ==========================================================

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


    // ==========================================================
    // FAILED / PENDING / CANCELLED
    // ==========================================================

    if (error) {

        return (

            <div className="container py-5">

                <div className="row justify-content-center">

                    <div className="col-lg-7">

                        <div className="card border-0 shadow-sm">

                            <div className="card-body text-center py-5">

                                <div className="display-1 text-warning">
                                    ⚠️
                                </div>


                                <h2 className="mt-3">
                                    Payment Verification
                                </h2>


                                <p className="text-muted">
                                    {error}
                                </p>


                                {paymentId && (

                                    <p>
                                        Payment ID:{" "}
                                        <strong>
                                            #{paymentId}
                                        </strong>
                                    </p>

                                )}


                                {paymentStatus && (

                                    <p>

                                        Status:{" "}

                                        <span className="badge bg-warning text-dark">

                                            {String(
                                                paymentStatus
                                            )}

                                        </span>

                                    </p>

                                )}


                                <div className="d-flex justify-content-center gap-2 flex-wrap mt-4">

                                    <button
                                        type="button"
                                        className="btn btn-primary"
                                        onClick={() =>
                                            navigate(
                                                "/checkout"
                                            )
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


                                    <Link
                                        to="/products"
                                        className="btn btn-outline-primary"
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

    }


    // ==========================================================
    // SUCCESS PAGE
    // ==========================================================

    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card border-0 shadow-sm">

                        <div className="card-body text-center py-5">


                            {/* SUCCESS ICON */}

                            <div className="display-1 text-success">
                                ✓
                            </div>


                            <h1 className="fw-bold mt-3">
                                Payment Successful!
                            </h1>


                            <p className="text-muted">
                                Your payment has been
                                successfully processed.
                            </p>


                            {/* PAYMENT INFORMATION */}

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

                                        <div className="d-flex justify-content-between mb-2">

                                            <span>
                                                Transaction ID
                                            </span>

                                            <strong>
                                                {transactionId}
                                            </strong>

                                        </div>

                                    )}


                                    {paymentStatus && (

                                        <div className="d-flex justify-content-between">

                                            <span>
                                                Status
                                            </span>

                                            <span className="badge bg-success">

                                                {String(
                                                    paymentStatus
                                                )}

                                            </span>

                                        </div>

                                    )}

                                </div>

                            </div>


                            {/* ACTIONS */}

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