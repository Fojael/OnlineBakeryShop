import { useState } from "react";

const Cart = () => {
    const [cartItems, setCartItems] = useState([
        {
            id: 1,
            name: "Chocolate Cake",
            price: 15.99,
            quantity: 2,
            image: "https://via.placeholder.com/150",
        },
        {
            id: 2,
            name: "Cup Cake",
            price: 4.99,
            quantity: 3,
            image: "https://via.placeholder.com/150",
        },
        {
            id: 3,
            name: "Cookies",
            price: 6.99,
            quantity: 1,
            image: "https://via.placeholder.com/150",
        },
    ]);

    // Increase Quantity
    const increaseQuantity = (id) => {
        setCartItems(
            cartItems.map((item) =>
                item.id === id
                    ? {
                          ...item,
                          quantity: item.quantity + 1,
                      }
                    : item
            )
        );
    };

    // Decrease Quantity
    const decreaseQuantity = (id) => {
        setCartItems(
            cartItems.map((item) =>
                item.id === id && item.quantity > 1
                    ? {
                          ...item,
                          quantity: item.quantity - 1,
                      }
                    : item
            )
        );
    };

    // Remove Item
    const removeItem = (id) => {
        setCartItems(
            cartItems.filter((item) => item.id !== id)
        );
    };

    // Total Price
    const totalPrice = cartItems.reduce(
        (total, item) =>
            total + item.price * item.quantity,
        0
    );

    return (
        <div className="container py-5">

            <h1 className="text-center mb-5">
                Shopping Cart
            </h1>

            {cartItems.length === 0 ? (
                <div className="text-center">
                    <h4>Your cart is empty.</h4>
                </div>
            ) : (
                <>
                    {/* Cart Items */}
                    <div className="row">

                        {cartItems.map((item) => (
                            <div
                                className="col-12 mb-4"
                                key={item.id}
                            >
                                <div className="card shadow">

                                    <div className="row g-0 align-items-center">

                                        {/* Product Image */}
                                        <div className="col-md-2">
                                            <img
                                                src={item.image}
                                                alt={item.name}
                                                className="img-fluid rounded-start"
                                            />
                                        </div>

                                        {/* Product Details */}
                                        <div className="col-md-4">
                                            <div className="card-body">

                                                <h5>
                                                    {item.name}
                                                </h5>

                                                <p>
                                                    Price:
                                                    {" "}
                                                    £{item.price}
                                                </p>

                                            </div>
                                        </div>

                                        {/* Quantity */}
                                        <div className="col-md-3 text-center">

                                            <button
                                                className="btn btn-outline-secondary me-2"
                                                onClick={() =>
                                                    decreaseQuantity(
                                                        item.id
                                                    )
                                                }
                                            >
                                                -
                                            </button>

                                            <span>
                                                {item.quantity}
                                            </span>

                                            <button
                                                className="btn btn-outline-secondary ms-2"
                                                onClick={() =>
                                                    increaseQuantity(
                                                        item.id
                                                    )
                                                }
                                            >
                                                +
                                            </button>

                                        </div>

                                        {/* Subtotal */}
                                        <div className="col-md-2 text-center">

                                            <p>
                                                <strong>
                                                    £
                                                    {(
                                                        item.price *
                                                        item.quantity
                                                    ).toFixed(2)}
                                                </strong>
                                            </p>

                                        </div>

                                        {/* Remove Button */}
                                        <div className="col-md-1 text-center">

                                            <button
                                                className="btn btn-danger"
                                                onClick={() =>
                                                    removeItem(
                                                        item.id
                                                    )
                                                }
                                            >
                                                X
                                            </button>

                                        </div>

                                    </div>

                                </div>
                            </div>
                        ))}

                    </div>

                    {/* Cart Summary */}
                    <div className="row justify-content-end">

                        <div className="col-md-4">

                            <div className="card shadow p-4">

                                <h3>
                                    Order Summary
                                </h3>

                                <hr />

                                <p>
                                    Total Items:
                                    {" "}
                                    {cartItems.length}
                                </p>

                                <h4>
                                    Total Price:
                                    {" "}
                                    £{totalPrice.toFixed(2)}
                                </h4>

                                <button className="btn btn-success w-100 mt-3">
                                    Proceed to Checkout
                                </button>

                            </div>

                        </div>

                    </div>
                </>
            )}
        </div>
    );
};

export default Cart;