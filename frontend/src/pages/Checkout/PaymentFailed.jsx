import {
    useState,
} from "react";

import {
    Link,
    useSearchParams,
} from "react-router-dom";

import { toast } from "react-toastify";

import {
    retryPayment,
    getPaymentRedirectUrl,
    getPaymentErrorMessage,
} from "../../services/paymentService";


const PaymentFailed = () => {

    const [
        searchParams
    ] = useSearchParams();


    const [
        retrying,
        setRetrying
    ] = useState(false);


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


    const handleRetry = async () => {

        if (!paymentId) {

            toast.error(
                "Payment information was not found."
            );

            return;

        }


        try {

            setRetrying(true);


            const response =
                await retryPayment(
                    paymentId
                );


            console.log(
                "Retry payment response:",
                response.data
            );


            const paymentUrl =
                getPaymentRedirectUrl(
                    response
                );


            if (!paymentUrl) {

                throw new Error(
                    "Payment gateway URL was not returned."
                );

            }


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

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

};


export default PaymentFailed;