import {
    useEffect,
    useRef,
} from "react";

import {
    Link,
    useSearchParams,
} from "react-router-dom";

import {
    cancelPayment,
} from "../../services/paymentService";


const PaymentCancelled = () => {

    const [
        searchParams,
    ] = useSearchParams();


    const cancellationSent =
        useRef(false);


    useEffect(() => {

        if (cancellationSent.current) {
            return;
        }

        cancellationSent.current = true;


        const paymentId =
            searchParams.get("payment_id") ||
            searchParams.get("paymentId") ||
            searchParams.get("id") ||
            sessionStorage.getItem(
                "pending_payment_id"
            );


        // ======================================================
        // CANCEL PAYMENT ON BACKEND
        // ======================================================

        const cancelPendingPayment =
            async () => {

                if (!paymentId) {

                    console.log(
                        "No payment ID found for cancellation."
                    );

                } else {

                    try {

                        const response =
                            await cancelPayment(
                                paymentId
                            );


                        console.log(
                            "Payment cancelled:",
                            response?.data
                        );

                    } catch (error) {

                        console.error(
                            "Payment cancellation error:",
                            error
                        );

                    }

                }


                // ==================================================
                // CLEAN PAYMENT SESSION DATA
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

                sessionStorage.removeItem(
                    "pending_payment_url"
                );

            };


        void cancelPendingPayment();


    }, [searchParams]);


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card shadow-sm border-0">

                        <div className="card-body text-center py-5">

                            <div className="display-1">
                                ⚠️
                            </div>


                            <h1 className="text-warning mt-3">
                                Payment Cancelled
                            </h1>


                            <p className="text-muted">
                                You cancelled the payment
                                process. Your order has not
                                been paid online.
                            </p>


                            <div className="alert alert-info text-start">

                                <strong>
                                    What can you do?
                                </strong>

                                <ul className="mb-0 mt-2">

                                    <li>
                                        Return to your orders
                                        and check the payment
                                        status.
                                    </li>

                                    <li>
                                        You can try making
                                        the payment again
                                        if supported.
                                    </li>

                                    <li>
                                        You can continue
                                        shopping.
                                    </li>

                                </ul>

                            </div>


                            <div className="d-grid gap-2 mt-4">

                                <Link
                                    to="/orders"
                                    className="btn btn-primary btn-lg"
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
                                    className="btn btn-outline-primary"
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


export default PaymentCancelled;