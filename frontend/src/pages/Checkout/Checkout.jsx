import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import { createOrder } from "../../services/orderService";

const Checkout = () => {
    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);

    const [formData, setFormData] = useState({
        shipping_address: "",
        payment_method: "Cash on Delivery",
        total_amount: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.shipping_address.trim()) {
            toast.warning("Shipping address is required.");
            return;
        }

        if (
            !formData.total_amount ||
            Number(formData.total_amount) <= 0
        ) {
            toast.warning("Total amount must be greater than 0.");
            return;
        }

        const orderData = {
            shipping_address: formData.shipping_address,
            payment_method: formData.payment_method,
            total_amount: Number(formData.total_amount),
        };

        try {
            setLoading(true);

            await createOrder(orderData);

            toast.success("Order placed successfully.");

            navigate("/orders");
        } catch (error) {
            console.error(error);
            toast.error("Failed to place order.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-7">

                    <div className="card shadow">

                        <div className="card-header bg-primary text-white">
                            <h3 className="mb-0">
                                Checkout
                            </h3>
                        </div>

                        <div className="card-body">

                            <form onSubmit={handleSubmit}>

                                {/* Shipping Address */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Shipping Address
                                    </label>

                                    <textarea
                                        className="form-control"
                                        rows="3"
                                        name="shipping_address"
                                        value={formData.shipping_address}
                                        onChange={handleChange}
                                        placeholder="Enter your delivery address"
                                    />

                                </div>

                                {/* Payment Method */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Payment Method
                                    </label>

                                    <select
                                        className="form-select"
                                        name="payment_method"
                                        value={formData.payment_method}
                                        onChange={handleChange}
                                    >
                                        <option>
                                            Cash on Delivery
                                        </option>

                                        <option>
                                            bKash
                                        </option>

                                        <option>
                                            Nagad
                                        </option>

                                        <option>
                                            Rocket
                                        </option>

                                        <option>
                                            Credit Card
                                        </option>

                                    </select>

                                </div>

                                {/* Total Amount */}

                                <div className="mb-4">

                                    <label className="form-label">
                                        Total Amount (৳)
                                    </label>

                                    <input
                                        type="number"
                                        className="form-control"
                                        name="total_amount"
                                        value={formData.total_amount}
                                        onChange={handleChange}
                                        min="1"
                                        placeholder="Enter total amount"
                                    />

                                </div>

                                {/* Buttons */}

                                <button
                                    type="submit"
                                    className="btn btn-success"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span
                                                className="spinner-border spinner-border-sm me-2"
                                                role="status"
                                            ></span>

                                            Placing Order...
                                        </>
                                    ) : (
                                        "Place Order"
                                    )}
                                </button>

                                <button
                                    type="button"
                                    className="btn btn-secondary ms-2"
                                    onClick={() => navigate("/cart")}
                                >
                                    Back to Cart
                                </button>

                            </form>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Checkout;