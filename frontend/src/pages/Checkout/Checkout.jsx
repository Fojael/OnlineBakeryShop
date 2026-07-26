import { useState } from "react";

const Checkout = () => {
    const [shippingInfo, setShippingInfo] = useState({
        fullName: "",
        phone: "",
        email: "",
        address: "",
        city: "",
        postalCode: "",
    });

    const [paymentMethod, setPaymentMethod] = useState(
        "Cash on Delivery"
    );

    const cartItems = [
        {
            id: 1,
            name: "Chocolate Cake",
            price: 15.99,
            quantity: 2,
        },
        {
            id: 2,
            name: "Cup Cake",
            price: 4.99,
            quantity: 3,
        },
    ];

    const subtotal = cartItems.reduce(
        (total, item) =>
            total + item.price * item.quantity,
        0
    );

    const deliveryCharge = 5.00;

    const totalPrice = subtotal + deliveryCharge;

    const handleChange = (e) => {
        setShippingInfo({
            ...shippingInfo,
            [e.target.name]: e.target.value,
        });
    };

    const handlePlaceOrder = () => {
        alert("Order placed successfully!");
    };

    return (
        <div className="container py-5">

            <h1 className="text-center mb-5">
                Checkout
            </h1>

            <div className="row">

                {/* Shipping Information */}
                <div className="col-lg-7">

                    <div className="card shadow p-4 mb-4">

                        <h3 className="mb-4">
                            Shipping Information
                        </h3>

                        <div className="row">

                            <div className="col-md-6 mb-3">
                                <input
                                    type="text"
                                    name="fullName"
                                    placeholder="Full Name"
                                    className="form-control"
                                    value={shippingInfo.fullName}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="col-md-6 mb-3">
                                <input
                                    type="text"
                                    name="phone"
                                    placeholder="Phone Number"
                                    className="form-control"
                                    value={shippingInfo.phone}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="col-md-6 mb-3">
                                <input
                                    type="email"
                                    name="email"
                                    placeholder="Email Address"
                                    className="form-control"
                                    value={shippingInfo.email}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="col-md-6 mb-3">
                                <input
                                    type="text"
                                    name="city"
                                    placeholder="City"
                                    className="form-control"
                                    value={shippingInfo.city}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="col-md-12 mb-3">
                                <textarea
                                    name="address"
                                    rows="3"
                                    placeholder="Shipping Address"
                                    className="form-control"
                                    value={shippingInfo.address}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="col-md-6 mb-3">
                                <input
                                    type="text"
                                    name="postalCode"
                                    placeholder="Postal Code"
                                    className="form-control"
                                    value={shippingInfo.postalCode}
                                    onChange={handleChange}
                                />
                            </div>

                        </div>

                    </div>


                    {/* Payment Method */}
                    <div className="card shadow p-4">

                        <h3 className="mb-4">
                            Payment Method
                        </h3>

                        <div className="form-check mb-3">
                            <input
                                type="radio"
                                className="form-check-input"
                                checked={
                                    paymentMethod ===
                                    "Cash on Delivery"
                                }
                                onChange={() =>
                                    setPaymentMethod(
                                        "Cash on Delivery"
                                    )
                                }
                            />

                            <label className="form-check-label">
                                Cash on Delivery
                            </label>
                        </div>

                        <div className="form-check mb-3">
                            <input
                                type="radio"
                                className="form-check-input"
                                checked={
                                    paymentMethod ===
                                    "Credit/Debit Card"
                                }
                                onChange={() =>
                                    setPaymentMethod(
                                        "Credit/Debit Card"
                                    )
                                }
                            />

                            <label className="form-check-label">
                                Credit / Debit Card
                            </label>
                        </div>

                        <div className="form-check">
                            <input
                                type="radio"
                                className="form-check-input"
                                checked={
                                    paymentMethod ===
                                    "Mobile Banking"
                                }
                                onChange={() =>
                                    setPaymentMethod(
                                        "Mobile Banking"
                                    )
                                }
                            />

                            <label className="form-check-label">
                                Mobile Banking
                            </label>
                        </div>

                    </div>

                </div>


                {/* Order Summary */}
                <div className="col-lg-5">

                    <div className="card shadow p-4">

                        <h3 className="mb-4">
                            Order Summary
                        </h3>

                        {cartItems.map((item) => (
                            <div
                                key={item.id}
                                className="d-flex justify-content-between mb-3"
                            >
                                <div>
                                    {item.name}
                                    <br />
                                    Qty: {item.quantity}
                                </div>

                                <div>
                                    £
                                    {(
                                        item.price *
                                        item.quantity
                                    ).toFixed(2)}
                                </div>
                            </div>
                        ))}

                        <hr />

                        <div className="d-flex justify-content-between">
                            <p>Subtotal</p>
                            <p>£{subtotal.toFixed(2)}</p>
                        </div>

                        <div className="d-flex justify-content-between">
                            <p>Delivery Charge</p>
                            <p>£{deliveryCharge.toFixed(2)}</p>
                        </div>

                        <hr />

                        <div className="d-flex justify-content-between">
                            <h5>Total</h5>
                            <h5>
                                £{totalPrice.toFixed(2)}
                            </h5>
                        </div>

                        <button
                            className="btn btn-success w-100 mt-4"
                            onClick={handlePlaceOrder}
                        >
                            Place Order
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Checkout;