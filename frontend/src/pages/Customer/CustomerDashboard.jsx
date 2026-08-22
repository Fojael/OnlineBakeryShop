import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import { getCart } from "../../services/cartService";
import { getOrders } from "../../services/orderService";

const CustomerDashboard = () => {
    const username =
        localStorage.getItem("username") || "Customer";

    const [loading, setLoading] = useState(true);

    const [cartItems, setCartItems] = useState(0);

    const [orders, setOrders] = useState([]);

    const [wishlistCount] = useState(0);

    const [error, setError] = useState("");

    useEffect(() => {
        let mounted = true;

        const loadDashboard = async () => {
            setLoading(true);

            try {
                // -------------------------
                // LOAD CART
                // -------------------------

                try {
                    const cartResponse = await getCart();

                    const items = Array.isArray(
                        cartResponse.data.items
                    )
                        ? cartResponse.data.items
                        : [];

                    const totalItems = items.reduce(
                        (sum, item) =>
                            sum + Number(item.quantity),
                        0
                    );

                    if (mounted) {
                        setCartItems(totalItems);
                    }
                } catch (err) {
                    console.error("Cart Error:", err);

                    if (mounted) {
                        setCartItems(0);
                    }
                }

                // -------------------------
                // LOAD ORDERS
                // -------------------------

                try {
                    const orderResponse = await getOrders();

                    const orderList = Array.isArray(
                        orderResponse.data
                    )
                        ? orderResponse.data
                        : [];

                    if (mounted) {
                        setOrders(orderList);
                    }
                } catch (err) {
                    console.error("Orders Error:", err);

                    if (mounted) {
                        setOrders([]);
                    }
                }
            } catch (err) {
                console.error(err);

                if (mounted) {
                    setError("Unable to load dashboard.");
                }

                toast.error(
                    err?.response?.data?.detail ||
                        "Unable to load dashboard."
                );
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadDashboard();

        return () => {
            mounted = false;
        };
    }, []);

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div
                    className="spinner-border text-primary"
                    role="status"
                >
                    <span className="visually-hidden">
                        Loading...
                    </span>
                </div>

                <h4 className="mt-3">
                    Loading Dashboard...
                </h4>
            </div>
        );
    }

    return (
        <div className="container py-5">

            {/* Welcome */}

            <div className="mb-5">
                <h2 className="fw-bold">
                    👋 Welcome, {username}
                </h2>

                <p className="text-muted">
                    Manage your orders, cart,
                    wishlist and account.
                </p>
            </div>

            {error && (
                <div className="alert alert-danger">
                    {error}
                </div>
            )}

            {/* Statistics */}

            <div className="row g-4 mb-5">

                <div className="col-md-6 col-lg-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>📦</h1>

                            <h2>{orders.length}</h2>

                            <p className="text-muted">
                                Total Orders
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>❤️</h1>

                            <h2>{wishlistCount}</h2>

                            <p className="text-muted">
                                Wishlist
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>🛒</h1>

                            <h2>{cartItems}</h2>

                            <p className="text-muted">
                                Cart Items
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>📍</h1>

                            <h2>0</h2>

                            <p className="text-muted">
                                Addresses
                            </p>
                        </div>
                    </div>
                </div>

            </div>

            {/* Quick Actions */}

            <div className="card shadow-sm mb-5">

                <div className="card-header">
                    <h4 className="mb-0">
                        🚀 Quick Actions
                    </h4>
                </div>

                <div className="card-body">

                    <div className="row g-3">

                        <div className="col-md-4">
                            <Link
                                to="/products"
                                className="btn btn-outline-primary w-100 py-3"
                            >
                                🛍 Continue Shopping
                            </Link>
                        </div>

                        <div className="col-md-4">
                            <Link
                                to="/cart"
                                className="btn btn-outline-success w-100 py-3"
                            >
                                🛒 View Cart
                            </Link>
                        </div>

                        <div className="col-md-4">
                            <Link
                                to="/orders"
                                className="btn btn-outline-dark w-100 py-3"
                            >
                                📦 My Orders
                            </Link>
                        </div>

                        <div className="col-md-4">
                            <Link
                                to="/profile"
                                className="btn btn-outline-info w-100 py-3"
                            >
                                👤 Profile
                            </Link>
                        </div>

                        <div className="col-md-4">
                            <Link
                                to="/checkout"
                                className="btn btn-outline-warning w-100 py-3"
                            >
                                💳 Checkout
                            </Link>
                        </div>

                    </div>

                </div>

            </div>

            {/* Recent Orders */}

            <div className="card shadow-sm">

                <div className="card-header">
                    <h4 className="mb-0">
                        📋 Recent Orders
                    </h4>
                </div>

                <div className="card-body">

                    {orders.length === 0 ? (
                        <p className="text-muted">
                            You haven't placed any orders yet.
                        </p>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-hover">

                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Status</th>
                                        <th>Total</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>

                                <tbody>

                                    {orders.slice(0, 5).map((order) => (
                                        <tr key={order.id}>
                                            <td>{order.id}</td>

                                            <td>{order.status}</td>

                                            <td>
                                                ৳{" "}
                                                {Number(
                                                    order.total_amount
                                                ).toFixed(2)}
                                            </td>

                                            <td>
                                                {new Date(
                                                    order.created_at
                                                ).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}

                                </tbody>

                            </table>
                        </div>
                    )}

                </div>

            </div>

        </div>
    );
};

export default CustomerDashboard;