import {
    Link,
    useSearchParams,
} from "react-router-dom";

import {
    useEffect,
} from "react";

import {
    cancelPayment,
} from "../../services/paymentService";


const PaymentCancelled = () => {

    const [
        searchParams
    ] = useSearchParams();


    useEffect(() => {

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


        // ======================================================
        // NOTIFY BACKEND
        // ======================================================

        if (paymentId) {

            cancelPayment(
                paymentId
            )
                .then(
                    (response) => {

                        console.log(
                            "Payment cancelled:",
                            response.data
                        );

                    }
                )
                .catch(
                    (error) => {

                        console.error(
                            "Payment cancellation error:",
                            error
                        );

                    }
                );

        }


        // ======================================================
        // CLEAN PENDING PAYMENT
        // ======================================================

        sessionStorage.removeItem(
            "pending_payment_id"
        );

        sessionStorage.removeItem(
            "pending_payment_method"
        );

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
                                        You can try placing
                                        the payment again if
                                        supported.
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