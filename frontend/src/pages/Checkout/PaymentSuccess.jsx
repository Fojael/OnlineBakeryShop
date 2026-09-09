import {
    useEffect,
    useState,
} from "react";

import {
    Link,
    useSearchParams,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";
import { getPaymentStatus } from "../../services/paymentService";


const PaymentSuccess = () => {
    const [
        searchParams,
    ] = useSearchParams();


    const orderId =
        searchParams.get("order_id");


    const paymentId =
        searchParams.get("payment_id");


    const transactionId =
        searchParams.get("tran_id");

    const [verification, setVerification] = useState({
        loading: Boolean(orderId),
        confirmed: false,
        error: "",
    });


    useEffect(() => {
        if (!orderId) return;
        getPaymentStatus(orderId)
            .then((response) => {
                const confirmed = response.data?.status === "Success";
                setVerification({ loading: false, confirmed, error: confirmed ? "" : "Payment is still being verified." });
                if (confirmed) toast.success("Payment completed successfully.");
            })
            .catch((error) => setVerification({ loading: false, confirmed: false, error: error.response?.data?.detail || "Unable to verify payment status." }));

    }, [orderId]);


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-md-7">

                    <div className="card shadow-sm">

                        <div className="card-body text-center p-5">

                            <div
                                className="display-4 mb-3"
                            >
                                ✓
                            </div>


                            <h2 className="mb-3">
                                {verification.loading ? "Verifying Payment" : verification.confirmed ? "Payment Successful" : "Payment Verification Pending"}
                            </h2>


                            <p className="text-muted">
                                {verification.loading ? "Confirming the gateway result with the server." : verification.error || "Your payment has been successfully processed."}
                            </p>


                            {orderId && (

                                <p>
                                    <strong>
                                        Order ID:
                                    </strong>{" "}
                                    {orderId}
                                </p>

                            )}


                            {paymentId && (

                                <p>
                                    <strong>
                                        Payment ID:
                                    </strong>{" "}
                                    {paymentId}
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


export default PaymentSuccess;
