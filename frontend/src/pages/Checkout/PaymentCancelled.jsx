import { useState } from "react";

import {
  Link,
  useSearchParams,
} from "react-router-dom";

import {
  retryPayment,
  redirectToGateway,
} from "../../services/paymentService";


const PaymentCancelled = () => {

  const [
    searchParams
  ] = useSearchParams();


  const orderId =
    searchParams.get(
      "order_id"
    );


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  const handleRetry =
    async () => {

      if (!orderId) {

        setError(
          "Order ID is missing."
        );

        return;
      }


      try {

        setLoading(true);
        setError("");


        const data =
          await retryPayment(
            orderId
          );


        localStorage.setItem(
          "pending_payment_order_id",
          String(orderId)
        );


        redirectToGateway(
          data.gateway_url
        );

      } catch (err) {

        setError(
          err?.response?.data?.detail ||
          "Could not start a new payment attempt."
        );

      } finally {

        setLoading(false);
      }
    };


  return (
    <div className="container py-5">

      <h2>
        Payment Cancelled
      </h2>


      <p>
        The payment was cancelled.
        Your order remains pending
        and can be paid again.
      </p>


      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}


      {orderId && (

        <button
          type="button"
          className="btn btn-primary me-2"
          onClick={handleRetry}
          disabled={loading}
        >
          {loading
            ? "Starting..."
            : "Retry Payment"}
        </button>

      )}


      <Link
        to="/orders"
        className="btn btn-secondary"
      >
        View Orders
      </Link>

    </div>
  );
};


export default PaymentCancelled;