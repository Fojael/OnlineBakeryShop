import {
    Link,
    useSearchParams,
} from "react-router-dom";


const PaymentCancelled = () => {

    const [
        searchParams,
    ] = useSearchParams();


    const orderId =
        searchParams.get("order_id");


    const transactionId =
        searchParams.get("tran_id");


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-md-7">

                    <div className="card shadow-sm">

                        <div className="card-body text-center p-5">

                            <div
                                className="display-4 mb-3"
                            >
                                !
                            </div>


                            <h2 className="mb-3">
                                Payment Cancelled
                            </h2>


                            <p className="text-muted">
                                The payment process was
                                cancelled.
                            </p>


                            <div className="alert alert-info">

                                Your order remains pending.
                                You can retry the payment
                                from your order details page.

                            </div>


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


export default PaymentCancelled;

