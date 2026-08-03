import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

const Cart = () => {
    const [cartItems, setCartItems] = useState([
        {
            id: 1,
            name: "Chocolate Cake",
            price: 650,
            quantity: 2,
            image: "https://via.placeholder.com/150",
        },
        {
            id: 2,
            name: "Red Velvet Cake",
            price: 850,
            quantity: 1,
            image: "https://via.placeholder.com/150",
        },
        {
            id: 3,
            name: "Cookies Box",
            price: 350,
            quantity: 3,
            image: "https://via.placeholder.com/150",
        },
    ]);

    // Increase Quantity
    const increaseQuantity = (id) => {
        setCartItems((prev) =>
            prev.map((item) =>
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
        setCartItems((prev) =>
            prev.map((item) =>
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
        if (!window.confirm("Remove this product from cart?")) return;

        setCartItems((prev) =>
            prev.filter((item) => item.id !== id)
        );

        toast.success("Product removed from cart.");
    };

    // Clear Cart
    const clearCart = () => {
        if (!window.confirm("Clear your shopping cart?")) return;

        setCartItems([]);

        toast.success("Cart cleared successfully.");
    };

    // Total Quantity
    const totalQuantity = cartItems.reduce(
        (sum, item) => sum + item.quantity,
        0
    );

    // Total Price
    const totalPrice = cartItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    return (
        <div className="container py-5">

            <div className="d-flex justify-content-between align-items-center mb-4">

                <h2 className="fw-bold">
                    🛒 Shopping Cart
                </h2>

                {cartItems.length > 0 && (
                    <button
                        className="btn btn-outline-danger"
                        onClick={clearCart}
                    >
                        Clear Cart
                    </button>
                )}

            </div>

            {cartItems.length === 0 ? (

                <div className="text-center py-5">

                    <h3>Your cart is empty.</h3>

                    <p className="text-muted">
                        Add delicious bakery products to your cart.
                    </p>

                    <Link
                        to="/products"
                        className="btn btn-primary mt-3"
                    >
                        Continue Shopping
                    </Link>

                </div>

            ) : (

                <div className="row">

                    {/* Cart Items */}
                    <div className="col-lg-8">

                        {cartItems.map((item) => (

                            <div
                                key={item.id}
                                className="card shadow-sm mb-3"
                            >

                                <div className="row g-0 align-items-center">

                                    <div className="col-md-3">

                                        <img
                                            src={item.image}
                                            alt={item.name}
                                            className="img-fluid rounded-start"
                                            style={{
                                                height: "180px",
                                                width: "100%",
                                                objectFit: "cover",
                                            }}
                                        />

                                    </div>

                                    <div className="col-md-6">

                                        <div className="card-body">

                                            <h5>{item.name}</h5>

                                            <p className="text-muted">
                                                Price: ৳ {item.price}
                                            </p>

                                            <div className="d-flex align-items-center">

                                                <button
                                                    className="btn btn-outline-secondary btn-sm"
                                                    onClick={() =>
                                                        decreaseQuantity(item.id)
                                                    }
                                                >
                                                    -
                                                </button>

                                                <span className="mx-3 fw-bold">
                                                    {item.quantity}
                                                </span>

                                                <button
                                                    className="btn btn-outline-secondary btn-sm"
                                                    onClick={() =>
                                                        increaseQuantity(item.id)
                                                    }
                                                >
                                                    +
                                                </button>

                                            </div>

                                        </div>

                                    </div>

                                    <div className="col-md-3 text-center">

                                        <h5 className="text-danger">
                                            ৳ {item.price * item.quantity}
                                        </h5>

                                        <button
                                            className="btn btn-sm btn-danger mt-2"
                                            onClick={() =>
                                                removeItem(item.id)
                                            }
                                        >
                                            Remove
                                        </button>

                                    </div>

                                </div>

                            </div>

                        ))}

                    </div>

                    {/* Summary */}
                    <div className="col-lg-4">

                        <div className="card shadow">

                            <div className="card-body">

                                <h4 className="mb-4">
                                    Order Summary
                                </h4>

                                <div className="d-flex justify-content-between">

                                    <span>Total Items</span>

                                    <strong>
                                        {totalQuantity}
                                    </strong>

                                </div>

                                <hr />

                                <div className="d-flex justify-content-between">

                                    <span>Total Price</span>

                                    <strong className="text-danger">
                                        ৳ {totalPrice}
                                    </strong>

                                </div>

                                <hr />

                                <Link
                                    to="/checkout"
                                    className="btn btn-success w-100 mb-2"
                                >
                                    Proceed to Checkout
                                </Link>

                                <Link
                                    to="/products"
                                    className="btn btn-outline-primary w-100"
                                >
                                    Continue Shopping
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            )}

        </div>
    );
};

export default Cart;