import {
    Link,
    useSearchParams,
} from "react-router-dom";
import { useState } from "react";
import { toast } from "react-toastify";
import { retryPayment } from "../../services/paymentService";


const PaymentFailed = () => {
    const [retrying, setRetrying] = useState(false);

    const [
        searchParams,
    ] = useSearchParams();


    const orderId =
        searchParams.get("order_id");


    const transactionId =
        searchParams.get("tran_id");


    const reason =
        searchParams.get("reason");

    const handleRetry = async () => {
        if (!orderId || retrying) return;
        try {
            setRetrying(true);
            const response = await retryPayment(orderId);
            const gatewayUrl = response?.gateway_url || response?.data?.gateway_url;
            if (!gatewayUrl) throw new Error("Payment gateway URL was not returned.");
            window.location.href = gatewayUrl;
        } catch (error) {
            toast.error(error.response?.data?.detail || "Unable to retry payment.");
        } finally {
            setRetrying(false);
        }
    };


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-md-7">

                    <div className="card shadow-sm">

                        <div className="card-body text-center p-5">

                            <div
                                className="display-4 mb-3"
                            >
                                ✕
                            </div>


                            <h2 className="mb-3">
                                Payment Failed
                            </h2>


                            <p className="text-muted">
                                Your payment could not
                                be completed.
                            </p>


                            {reason && (

                                <div className="alert alert-danger">

                                    {reason}

                                </div>

                            )}


                            {orderId && (

                                <p>
                                    <strong>
                                        Order ID:
                                    </strong>{" "}
                                    {orderId}
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


                            <div className="d-flex gap-2 justify-content-center mt-4">

                                {orderId && (
                                    <button type="button" className="btn btn-danger" onClick={handleRetry} disabled={retrying}>
                                        {retrying ? "Retrying..." : "Retry Payment"}
                                    </button>
                                )}

                                {orderId && (

                                    <Link
                                        to={`/orders/${orderId}`}
                                        className="btn btn-primary"
                                    >
                                        View Order
                                    </Link>

                                )}


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

            </div>

        </div>
    );
};


export default PaymentFailed;

