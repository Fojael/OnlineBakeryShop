import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createOrder } from "../../services/orderService";

import {
  createPayment,
  redirectToGateway,
} from "../../services/paymentService";


const Checkout = () => {

  const navigate = useNavigate();

  const [
    shippingAddress,
    setShippingAddress,
  ] = useState("");

  const [
    paymentMethod,
    setPaymentMethod,
  ] = useState(
    "Cash on Delivery"
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  const handleSubmit = async (
    event
  ) => {

    event.preventDefault();

    if (!shippingAddress.trim()) {

      setError(
        "Shipping address is required."
      );

      return;
    }


    try {

      setLoading(true);
      setError("");


      const orderResponse =
        await createOrder({
          shipping_address:
            shippingAddress.trim(),

          payment_method:
            paymentMethod,
        });


      const order =
        orderResponse.order;


      if (
        paymentMethod ===
        "Cash on Delivery"
      ) {

        localStorage.removeItem(
          "cart"
        );

        localStorage.removeItem(
          "checkout"
        );

        navigate(
          `/payment/success?order_id=${order.id}&cod=1`
        );

        return;
      }


      const paymentResponse =
        await createPayment(
          order.id
        );


      localStorage.setItem(
        "pending_payment_order_id",
        String(order.id)
      );


      redirectToGateway(
        paymentResponse.gateway_url
      );

    } catch (err) {

      setError(
        err?.response?.data?.detail ||
        "Could not start checkout."
      );

    } finally {

      setLoading(false);
    }
  };


  return (
    <div className="container py-4">

      <h2>
        Checkout
      </h2>


      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}


      <form
        onSubmit={handleSubmit}
      >

        <div className="mb-3">

          <label className="form-label">
            Shipping Address
          </label>


          <textarea
            className="form-control"
            rows="4"
            value={shippingAddress}
            onChange={(event) =>
              setShippingAddress(
                event.target.value
              )
            }
            required
          />

        </div>


        <div className="mb-3">

          <label className="form-label">
            Payment Method
          </label>


          <select
            className="form-select"
            value={paymentMethod}
            onChange={(event) =>
              setPaymentMethod(
                event.target.value
              )
            }
          >

            <option value="Cash on Delivery">
              Cash on Delivery
            </option>

            <option value="SSLCommerz">
              SSLCommerz
            </option>

          </select>

        </div>


        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading
            ? "Processing..."
            : "Place Order"}
        </button>

      </form>

    </div>
  );
};


export default Checkout;