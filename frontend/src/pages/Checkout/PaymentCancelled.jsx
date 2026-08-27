
import { Link, useSearchParams } from "react-router-dom";


// ==========================================================
// PAYMENT CANCELLED
// ==========================================================

const PaymentCancelled = () => {

    const [searchParams] =
        useSearchParams();

    const orderId =
        searchParams.get("order_id");


    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-md-7">

                    <div className="card shadow-sm text-center">

                        <div className="card-body p-5">

                            <div
                                className="display-4 mb-3"
                            >
                                !
                            </div>

                            <h2 className="text-warning mb-3">
                                Payment Cancelled
                            </h2>

                            <p className="text-muted">
                                Your payment process was
                                cancelled.
                            </p>

                            {orderId && (

                                <p>
                                    <strong>
                                        Order ID:
                                    </strong>{" "}
                                    #{orderId}
                                </p>

                            )}

                            <div className="d-flex justify-content-center gap-2 mt-4">

                                <Link
                                    to="/orders"
                                    className="btn btn-primary"
                                >
                                    My Orders
                                </Link>

                                <Link
                                    to="/"
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


export default PaymentCancelled;