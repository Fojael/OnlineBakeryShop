import {
    useState,
} from "react";

import {
    Link,
    useSearchParams,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    retryPayment,
    getPaymentRedirectUrl,
    getPaymentId,
    getPaymentErrorMessage,
} from "../../services/paymentService";


const PaymentFailed = () => {

    const [
        searchParams,
    ] = useSearchParams();


    const [
        retrying,
        setRetrying,
    ] = useState(false);


    // ==========================================================
    // GET PAYMENT ID
    // ==========================================================

    const paymentId =
        searchParams.get("payment_id") ||
        searchParams.get("paymentId") ||
        searchParams.get("id") ||
        sessionStorage.getItem(
            "pending_payment_id"
        );


    // ==========================================================
    // GET ORDER ID
    // ==========================================================

    const orderId =
        searchParams.get("order_id") ||
        searchParams.get("orderId") ||
        sessionStorage.getItem(
            "pending_order_id"
        );


    // ==========================================================
    // RETRY PAYMENT
    // ==========================================================

    const handleRetry = async () => {

        if (retrying) {
            return;
        }


        if (!paymentId) {

            toast.error(
                "Payment information was not found."
            );

            return;
        }


        try {

            setRetrying(true);


            // ==================================================
            // CREATE NEW PAYMENT SESSION
            // ==================================================

            const response =
                await retryPayment(
                    paymentId
                );


            console.log(
                "Retry payment response:",
                response?.data
            );


            // ==================================================
            // GET NEW PAYMENT ID
            // ==================================================

            const newPaymentId =
                getPaymentId(
                    response
                );


            // ==================================================
            // GET PAYMENT URL
            // ==================================================

            const paymentUrl =
                getPaymentRedirectUrl(
                    response
                );


            if (!paymentUrl) {

                throw new Error(
                    "Payment gateway URL was not returned."
                );

            }


            // ==================================================
            // SAVE NEW PAYMENT INFORMATION
            // ==================================================

            if (newPaymentId) {

                sessionStorage.setItem(
                    "pending_payment_id",
                    String(newPaymentId)
                );

            }


            if (orderId) {

                sessionStorage.setItem(
                    "pending_order_id",
                    String(orderId)
                );

            }


            sessionStorage.setItem(
                "pending_payment_url",
                paymentUrl
            );


            // ==================================================
            // REDIRECT
            // ==================================================

            toast.info(
                "Redirecting to payment gateway..."
            );


            window.location.href =
                paymentUrl;


        } catch (error) {

            console.error(
                "Retry payment error:",
                error
            );


            toast.error(
                getPaymentErrorMessage(
                    error
                )
            );

        } finally {

            setRetrying(false);

        }

    };


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card shadow-sm border-0">

                        <div className="card-body text-center py-5">

                            <div className="display-1">
                                ❌
                            </div>


                            <h1 className="text-danger mt-3">
                                Payment Failed
                            </h1>


                            <p className="text-muted">
                                Unfortunately, your payment
                                could not be completed.
                            </p>


                            {paymentId && (

                                <p>
                                    Payment ID:{" "}
                                    <strong>
                                        #{paymentId}
                                    </strong>
                                </p>

                            )}


                            {orderId && (

                                <p className="text-muted">
                                    Order ID:{" "}
                                    <strong>
                                        #{orderId}
                                    </strong>
                                </p>

                            )}


                            <div className="alert alert-warning text-start">

                                <strong>
                                    Payment was not completed.
                                </strong>

                                <div className="small mt-1">
                                    You can try the payment
                                    again or check your order
                                    status.
                                </div>

                            </div>


                            <div className="d-grid gap-2 mt-4">

                                {paymentId && (

                                    <button
                                        type="button"
                                        className="btn btn-primary btn-lg"
                                        onClick={
                                            handleRetry
                                        }
                                        disabled={
                                            retrying
                                        }
                                    >

                                        {retrying ? (

                                            <>

                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                    aria-hidden="true"
                                                />

                                                Creating new payment...

                                            </>

                                        ) : (

                                            <>
                                                🔄 Try Payment Again
                                            </>

                                        )}

                                    </button>

                                )}


                                <Link
                                    to="/orders"
                                    className="btn btn-outline-primary"
                                >
                                    View My Orders
                                </Link>


                                <Link
                                    to="/products"
                                    className="btn btn-outline-secondary"
                                >
                                    Continue Shopping
                                </Link>


                                <Link
                                    to="/cart"
                                    className="btn btn-outline-dark"
                                >
                                    Back to Cart
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

};


export default PaymentFailed;