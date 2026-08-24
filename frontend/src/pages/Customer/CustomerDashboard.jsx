import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import { getCart } from "../../services/cartService";
import { getOrders } from "../../services/orderService";
import { getWishlist } from "../../services/wishlistService";
import { getAddresses } from "../../services/addressService";

const CustomerDashboard = () => {
    // ==========================================================
    // USER
    // ==========================================================

    const username =
        localStorage.getItem("username") || "Customer";

    // ==========================================================
    // STATE
    // ==========================================================

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const [cartItems, setCartItems] = useState(0);

    const [wishlistCount, setWishlistCount] =
        useState(0);

    const [addressCount, setAddressCount] =
        useState(0);

    const [orders, setOrders] = useState([]);

    // ==========================================================
    // LOAD DASHBOARD
    // ==========================================================

    useEffect(() => {
        let mounted = true;

        const loadDashboard = async () => {
            try {
                setLoading(true);
                setError("");

                // ==================================================
                // LOAD CART
                // ==================================================

                try {
                    const cartResponse =
                        await getCart();

                    const cart =
                        cartResponse.data;

                    const items =
                        Array.isArray(cart.items)
                            ? cart.items
                            : [];

                    const totalItems =
                        items.reduce(
                            (sum, item) =>
                                sum +
                                Number(
                                    item.quantity
                                ),
                            0
                        );

                    if (mounted) {
                        setCartItems(
                            totalItems
                        );
                    }
                } catch (err) {
                    console.error(
                        "Cart Error:",
                        err
                    );

                    if (mounted) {
                        setCartItems(0);
                    }
                }

                // ==================================================
                // LOAD ORDERS
                // ==================================================

                try {
                    const orderResponse =
                        await getOrders();

                    const orderList =
                        Array.isArray(
                            orderResponse.data
                        )
                            ? orderResponse.data
                            : [];

                    if (mounted) {
                        setOrders(
                            orderList
                        );
                    }
                } catch (err) {
                    console.error(
                        "Orders Error:",
                        err
                    );

                    if (mounted) {
                        setOrders([]);
                    }
                }

                // ==================================================
                // LOAD WISHLIST
                // ==================================================

                try {
                    const wishlistResponse =
                        await getWishlist();

                    const wishlistItems =
                        Array.isArray(
                            wishlistResponse
                                .data
                                ?.items
                        )
                            ? wishlistResponse
                                  .data.items
                            : [];

                    if (mounted) {
                        setWishlistCount(
                            wishlistItems.length
                        );
                    }
                } catch (err) {
                    console.error(
                        "Wishlist Error:",
                        err
                    );

                    if (mounted) {
                        setWishlistCount(0);
                    }
                }

                // ==================================================
                // LOAD ADDRESSES
                // ==================================================

                try {
                    const addressResponse =
                        await getAddresses();

                    const addressList =
                        Array.isArray(
                            addressResponse.data
                        )
                            ? addressResponse.data
                            : [];

                    if (mounted) {
                        setAddressCount(
                            addressList.length
                        );
                    }
                } catch (err) {
                    console.error(
                        "Address Error:",
                        err
                    );

                    if (mounted) {
                        setAddressCount(0);
                    }
                }
            } catch (err) {
                console.error(
                    "Dashboard Error:",
                    err
                );

                if (mounted) {
                    setError(
                        "Unable to load dashboard."
                    );
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

    // ==========================================================
    // LOADING
    // ==========================================================

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

    // ==========================================================
    // DASHBOARD
    // ==========================================================

    return (
        <div className="container py-5">

            {/* ==================================================
                WELCOME
            ================================================== */}

            <div className="mb-5">

                <h2 className="fw-bold">
                    👋 Welcome, {username}
                </h2>

                <p className="text-muted">
                    Manage your orders, cart,
                    wishlist and account.
                </p>

            </div>

            {/* ==================================================
                ERROR
            ================================================== */}

            {error && (
                <div className="alert alert-danger">
                    {error}
                </div>
            )}

            {/* ==================================================
                STATISTICS
            ================================================== */}

            <div className="row g-4 mb-5">

                {/* ==================================================
                    ORDERS
                ================================================== */}

                <div className="col-md-6 col-lg-3">

                    <div className="card border-0 shadow-sm h-100 text-center">

                        <div className="card-body">

                            <h1>📦</h1>

                            <h2 className="fw-bold">
                                {orders.length}
                            </h2>

                            <p className="text-muted mb-0">
                                Total Orders
                            </p>

                        </div>

                    </div>

                </div>

                {/* ==================================================
                    WISHLIST
                ================================================== */}

                <div className="col-md-6 col-lg-3">

                    <div className="card border-0 shadow-sm h-100 text-center">

                        <div className="card-body">

                            <h1>❤️</h1>

                            <h2 className="fw-bold">
                                {wishlistCount}
                            </h2>

                            <p className="text-muted mb-0">
                                Wishlist Items
                            </p>

                        </div>

                    </div>

                </div>

                {/* ==================================================
                    CART
                ================================================== */}

                <div className="col-md-6 col-lg-3">

                    <div className="card border-0 shadow-sm h-100 text-center">

                        <div className="card-body">

                            <h1>🛒</h1>

                            <h2 className="fw-bold">
                                {cartItems}
                            </h2>

                            <p className="text-muted mb-0">
                                Cart Items
                            </p>

                        </div>

                    </div>

                </div>

                {/* ==================================================
                    ADDRESS
                ================================================== */}

                <div className="col-md-6 col-lg-3">

                    <Link
                        to="/address"
                        className="text-decoration-none text-dark"
                    >

                        <div className="card border-0 shadow-sm h-100 text-center">

                            <div className="card-body">

                                <h1>📍</h1>

                                <h2 className="fw-bold">
                                    {addressCount}
                                </h2>

                                <p className="text-muted mb-0">
                                    Saved Addresses
                                </p>

                            </div>

                        </div>

                    </Link>

                </div>

            </div>

            {/* ==================================================
                QUICK ACTIONS
            ================================================== */}

            <div className="card border-0 shadow-sm mb-5">

                <div className="card-header bg-white">

                    <h4 className="mb-0">
                        🚀 Quick Actions
                    </h4>

                </div>

                <div className="card-body">

                    <div className="row g-3">

                        {/* Products */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/products"
                                className="btn btn-outline-primary w-100 py-3"
                            >
                                🛍 Continue Shopping
                            </Link>

                        </div>

                        {/* Cart */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/cart"
                                className="btn btn-outline-success w-100 py-3"
                            >
                                🛒 View Cart
                            </Link>

                        </div>

                        {/* Wishlist */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/wishlist"
                                className="btn btn-outline-danger w-100 py-3"
                            >
                                ❤️ Wishlist
                            </Link>

                        </div>

                        {/* Orders */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/orders"
                                className="btn btn-outline-dark w-100 py-3"
                            >
                                📦 My Orders
                            </Link>

                        </div>

                        {/* Checkout */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/checkout"
                                className="btn btn-outline-warning w-100 py-3"
                            >
                                💳 Checkout
                            </Link>

                        </div>

                        {/* Profile */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/profile"
                                className="btn btn-outline-info w-100 py-3"
                            >
                                👤 My Profile
                            </Link>

                        </div>

                        {/* Address */}

                        <div className="col-md-6 col-lg-4">

                            <Link
                                to="/address"
                                className="btn btn-outline-secondary w-100 py-3"
                            >
                                📍 My Addresses
                            </Link>

                        </div>

                    </div>

                </div>

            </div>

            {/* ==================================================
                RECENT ORDERS
            ================================================== */}

            <div className="card border-0 shadow-sm">

                <div className="card-header bg-white">

                    <h4 className="mb-0">
                        📋 Recent Orders
                    </h4>

                </div>

                <div className="card-body">

                    {orders.length === 0 ? (

                        <div className="text-center py-4">

                            <h5 className="text-muted">
                                You haven't placed
                                any orders yet.
                            </h5>

                            <Link
                                to="/products"
                                className="btn btn-primary mt-3"
                            >
                                Start Shopping
                            </Link>

                        </div>

                    ) : (

                        <div className="table-responsive">

                            <table className="table table-hover align-middle">

                                <thead className="table-light">

                                    <tr>

                                        <th>#</th>

                                        <th>
                                            Order ID
                                        </th>

                                        <th>
                                            Status
                                        </th>

                                        <th>
                                            Total
                                        </th>

                                        <th>
                                            Date
                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {orders
                                        .slice(0, 5)
                                        .map(
                                            (
                                                order,
                                                index
                                            ) => (

                                                <tr
                                                    key={
                                                        order.id
                                                    }
                                                >

                                                    <td>
                                                        {index +
                                                            1}
                                                    </td>

                                                    <td>
                                                        #
                                                        {
                                                            order.id
                                                        }
                                                    </td>

                                                    <td>

                                                        <span
                                                            className={`badge ${
                                                                order.status ===
                                                                "Delivered"
                                                                    ? "bg-success"
                                                                    : order.status ===
                                                                      "Pending"
                                                                    ? "bg-warning text-dark"
                                                                    : order.status ===
                                                                      "Cancelled"
                                                                    ? "bg-danger"
                                                                    : "bg-info"
                                                            }`}
                                                        >
                                                            {
                                                                order.status
                                                            }
                                                        </span>

                                                    </td>

                                                    <td>
                                                        ৳{" "}
                                                        {Number(
                                                            order.total_amount
                                                        ).toFixed(
                                                            2
                                                        )}
                                                    </td>

                                                    <td>
                                                        {new Date(
                                                            order.created_at
                                                        ).toLocaleDateString()}
                                                    </td>

                                                </tr>

                                            )
                                        )}

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