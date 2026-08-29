import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verifyPayment } from "../../services/paymentService";

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();

  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState(
    "Verifying your payment. Please wait..."
  );
  const [order, setOrder] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const verify = async () => {
      try {
        /*
         * SSLCommerz can return several parameters.
         * We forward the complete query string to the backend.
         */
        const queryString = searchParams.toString();

        if (!queryString) {
          if (isMounted) {
            setStatus("failed");
            setMessage(
              "Payment verification information was not found."
            );
          }

          return;
        }

        const response = await verifyPayment(queryString);

        if (!isMounted) {
          return;
        }

        setStatus("success");

        setMessage(
          response?.message ||
            "Your payment was completed successfully."
        );

        setOrder(response?.order || null);

        /*
         * Payment verification succeeded.
         *
         * Remove temporary checkout information.
         */
        sessionStorage.removeItem("checkout_data");
        sessionStorage.removeItem("payment_pending");
        localStorage.removeItem("pending_order_id");
      } catch (error) {
        if (!isMounted) {
          return;
        }

        console.error(
          "Payment verification error:",
          error
        );

        const backendMessage =
          error?.response?.data?.detail ||
          error?.response?.data?.message ||
          "Payment verification failed.";

        setStatus("failed");
        setMessage(backendMessage);
      }
    };

    verify();

    return () => {
      isMounted = false;
    };
  }, [searchParams]);

  /*
   * ========================================================
   * LOADING
   * ========================================================
   */

  if (status === "loading") {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-7">
            <div className="card shadow-sm border-0">
              <div className="card-body text-center p-5">

                <div
                  className="spinner-border text-primary mb-4"
                  role="status"
                >
                  <span className="visually-hidden">
                    Loading...
                  </span>
                </div>

                <h3 className="mb-3">
                  Verifying Payment
                </h3>

                <p className="text-muted mb-0">
                  {message}
                </p>

              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /*
   * ========================================================
   * PAYMENT SUCCESS
   * ========================================================
   */

  if (status === "success") {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-8">

            <div className="card shadow-sm border-0">
              <div className="card-body text-center p-5">

                <div
                  className="rounded-circle bg-success bg-opacity-10
                  d-inline-flex align-items-center justify-content-center
                  mb-4"
                  style={{
                    width: "80px",
                    height: "80px",
                  }}
                >
                  <span
                    className="text-success"
                    style={{ fontSize: "40px" }}
                  >
                    ✓
                  </span>
                </div>

                <h2 className="text-success mb-3">
                  Payment Successful
                </h2>

                <p className="text-muted mb-4">
                  {message}
                </p>

                {order && (
                  <div className="card bg-light border-0 mb-4">
                    <div className="card-body">

                      <h5 className="mb-3">
                        Order Information
                      </h5>

                      <div className="row text-start">

                        <div className="col-sm-6 mb-2">
                          <strong>
                            Order ID:
                          </strong>{" "}
                          #{order.id}
                        </div>

                        <div className="col-sm-6 mb-2">
                          <strong>
                            Status:
                          </strong>{" "}
                          {order.status}
                        </div>

                        <div className="col-sm-6 mb-2">
                          <strong>
                            Payment:
                          </strong>{" "}
                          {order.payment_status ||
                            "Paid"}
                        </div>

                        <div className="col-sm-6 mb-2">
                          <strong>
                            Total:
                          </strong>{" "}
                          ৳{order.total_amount}
                        </div>

                      </div>

                      {order.transaction_id && (
                        <div className="mt-3 text-start">
                          <strong>
                            Transaction ID:
                          </strong>{" "}
                          {order.transaction_id}
                        </div>
                      )}

                    </div>
                  </div>
                )}

                <div className="d-flex justify-content-center gap-2 flex-wrap">

                  <Link
                    to="/orders"
                    className="btn btn-primary"
                  >
                    View My Orders
                  </Link>

                  <Link
                    to="/products"
                    className="btn btn-outline-primary"
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
  }

  /*
   * ========================================================
   * PAYMENT FAILED
   * ========================================================
   */

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-7">

          <div className="card shadow-sm border-0">
            <div className="card-body text-center p-5">

              <div
                className="rounded-circle bg-danger bg-opacity-10
                d-inline-flex align-items-center justify-content-center
                mb-4"
                style={{
                  width: "80px",
                  height: "80px",
                }}
              >
                <span
                  className="text-danger"
                  style={{ fontSize: "40px" }}
                >
                  ×
                </span>
              </div>

              <h2 className="text-danger mb-3">
                Payment Verification Failed
              </h2>

              <p className="text-muted mb-4">
                {message}
              </p>

              <div className="d-flex justify-content-center gap-2 flex-wrap">

                <Link
                  to="/checkout"
                  className="btn btn-primary"
                >
                  Try Payment Again
                </Link>

                <Link
                  to="/orders"
                  className="btn btn-outline-secondary"
                >
                  View Orders
                </Link>

              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}