import {
    useEffect,
    useState,
} from "react";

import {
    Link,
    useSearchParams,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    checkPaymentStatus,
    getPayment,
    getPaymentId,
    getOrderId,
    getTransactionId,
    getPaymentStatus,
    isPaymentSuccessful,
    getPaymentErrorMessage,
} from "../../services/paymentService";


const PaymentSuccess = () => {

    const [
        searchParams
    ] = useSearchParams();


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        payment,
        setPayment
    ] = useState(null);


    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        let mounted = true;


        const verifyPayment = async () => {

            try {

                setLoading(true);

                setError("");


                // ==================================================
                // GET PAYMENT ID
                // ==================================================

                const paymentId =
                    searchParams.get(
                        "payment_id"
                    ) ||
                    searchParams.get(
                        "paymentId"
                    ) ||
                    sessionStorage.getItem(
                        "pending_payment_id"
                    );


                if (!paymentId) {

                    throw new Error(
                        "Payment information was not found."
                    );

                }


                // ==================================================
                // CHECK PAYMENT STATUS
                // ==================================================

                const response =
                    await checkPaymentStatus(
                        paymentId
                    );


                console.log(
                    "Payment status:",
                    response.data
                );


                if (mounted) {

                    setPayment(
                        response.data
                    );

                }


                // ==================================================
                // CHECK STATUS
                // ==================================================

                const status =
                    getPaymentStatus(
                        response
                    );


                if (
                    !isPaymentSuccessful(
                        status
                    )
                ) {

                    throw new Error(
                        "Payment has not been confirmed yet."
                    );

                }


                // ==================================================
                // CLEAN SESSION
                // ==================================================

                sessionStorage.removeItem(
                    "pending_payment_id"
                );

                sessionStorage.removeItem(
                    "pending_order_id"
                );

                sessionStorage.removeItem(
                    "pending_payment_method"
                );


                toast.success(
                    "Payment completed successfully!"
                );

            } catch (err) {

                console.error(
                    "Payment verification error:",
                    err
                );


                if (mounted) {

                    setError(
                        getPaymentErrorMessage(
                            err
                        )
                    );

                }

            } finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        };


        verifyPayment();


        return () => {

            mounted = false;

        };

    }, [searchParams]);


    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {

        return (

            <div className="container py-5">

                <div className="card shadow-sm">

                    <div className="card-body text-center py-5">

                        <div
                            className="spinner-border text-success"
                            role="status"
                        />

                        <h4 className="mt-3">
                            Verifying Payment...
                        </h4>

                        <p className="text-muted">
                            Please wait while we confirm
                            your payment.
                        </p>

                    </div>

                </div>

            </div>

        );

    }


    // ==========================================================
    // ERROR
    // ==========================================================

    if (error) {

        return (

            <div className="container py-5">

                <div className="card shadow-sm">

                    <div className="card-body text-center py-5">

                        <div
                            className="display-3 mb-3"
                        >
                            ⚠️
                        </div>

                        <h2>
                            Payment Verification Failed
                        </h2>

                        <p className="text-muted">
                            {error}
                        </p>

                        <div className="d-flex justify-content-center gap-2">

                            <Link
                                to="/orders"
                                className="btn btn-primary"
                            >
                                View Orders
                            </Link>

                            <Link
                                to="/products"
                                className="btn btn-outline-secondary"
                            >
                                Continue Shopping
                            </Link>

                        </div>

                    </div>

                </div>

            </div>

        );

    }


    // ==========================================================
    // PAYMENT DATA
    // ==========================================================

    const paymentId =
        getPaymentId(payment);


    const orderId =
        getOrderId(payment);


    const transactionId =
        getTransactionId(payment);


    const status =
        getPaymentStatus(payment);


    // ==========================================================
    // SUCCESS PAGE
    // ==========================================================

    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card shadow-sm border-0">

                        <div className="card-body text-center py-5">

                            <div className="display-1">
                                ✅
                            </div>

                            <h1 className="text-success mt-3">
                                Payment Successful!
                            </h1>

                            <p className="text-muted">
                                Your payment has been
                                successfully confirmed.
                            </p>


                            <hr />


                            {orderId && (

                                <p>
                                    <strong>
                                        Order ID:
                                    </strong>{" "}
                                    #{orderId}
                                </p>

                            )}


                            {paymentId && (

                                <p>
                                    <strong>
                                        Payment ID:
                                    </strong>{" "}
                                    #{paymentId}
                                </p>

                            )}


                            {transactionId && (

                                <p>
                                    <strong>
                                        Transaction ID:
                                    </strong>{" "}
                                    {transactionId}
                                </p>

                            )}


                            {status && (

                                <p>
                                    <strong>
                                        Status:
                                    </strong>{" "}
                                    {status}
                                </p>

                            )}


                            <div className="d-grid gap-2 mt-4">

                                {orderId && (

                                    <Link
                                        to={`/orders/${orderId}`}
                                        className="btn btn-success btn-lg"
                                    >
                                        View Order
                                    </Link>

                                )}

                                <Link
                                    to="/orders"
                                    className="btn btn-outline-primary"
                                >
                                    My Orders
                                </Link>

                                <Link
                                    to="/products"
                                    className="btn btn-outline-secondary"
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