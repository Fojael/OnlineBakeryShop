import { Link, useSearchParams } from "react-router-dom";

const PaymentFailed = () => {
    const [searchParams] = useSearchParams();

    const orderId = searchParams.get("order_id");
    const transactionId = searchParams.get("tran_id");

    return (
        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-md-7 col-lg-6">

                    <div className="card border-0 shadow-sm">

                        <div className="card-body text-center p-5">

                            {/* ==================================================
                                FAILED ICON
                            ================================================== */}

                            <div
                                className="rounded-circle bg-danger bg-opacity-10 d-inline-flex align-items-center justify-content-center mb-4"
                                style={{
                                    width: "90px",
                                    height: "90px",
                                }}
                            >
                                <span
                                    className="text-danger"
                                    style={{
                                        fontSize: "45px",
                                    }}
                                >
                                    ✕
                                </span>
                            </div>

                            {/* ==================================================
                                TITLE
                            ================================================== */}

                            <h2 className="fw-bold text-danger">
                                Payment Failed
                            </h2>

                            <p className="text-muted mt-3">
                                Unfortunately, your payment could not
                                be completed.
                            </p>

                            <p className="text-muted">
                                Please try again or choose another
                                payment method.
                            </p>

                            {/* ==================================================
                                PAYMENT INFORMATION
                            ================================================== */}

                            {(orderId || transactionId) && (
                                <div className="alert alert-light border text-start mt-4">

                                    {orderId && (
                                        <div className="mb-2">
                                            <strong>
                                                Order ID:
                                            </strong>{" "}
                                            #{orderId}
                                        </div>
                                    )}

                                    {transactionId && (
                                        <div>
                                            <strong>
                                                Transaction ID:
                                            </strong>{" "}
                                            {transactionId}
                                        </div>
                                    )}

                                </div>
                            )}

                            {/* ==================================================
                                ACTION BUTTONS
                            ================================================== */}

                            <div className="d-grid gap-2 mt-4">

                                {orderId && (
                                    <Link
                                        to={`/checkout?order_id=${orderId}`}
                                        className="btn btn-primary"
                                    >
                                        Try Payment Again
                                    </Link>
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