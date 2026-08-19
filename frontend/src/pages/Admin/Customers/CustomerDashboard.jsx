import { Link } from "react-router-dom";

const CustomerDashboard = () => {
    const username =
        localStorage.getItem("username") || "Customer";

    return (
        <div className="container py-5">

            {/* =======================================
                Welcome
            ======================================= */}

            <div className="mb-5">
                <h2 className="fw-bold">
                    👋 Welcome, {username}
                </h2>

                <p className="text-muted">
                    Manage your orders, cart, wishlist and account.
                </p>
            </div>

            {/* =======================================
                Statistics
            ======================================= */}

            <div className="row g-4 mb-5">

                <div className="col-md-6 col-lg-3">
                    <div className="card border-0 shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>📦</h1>

                            <h3>0</h3>

                            <p className="text-muted mb-0">
                                Total Orders
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card border-0 shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>❤️</h1>

                            <h3>0</h3>

                            <p className="text-muted mb-0">
                                Wishlist
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card border-0 shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>🛒</h1>

                            <h3>0</h3>

                            <p className="text-muted mb-0">
                                Cart Items
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 col-lg-3">
                    <div className="card border-0 shadow-sm text-center h-100">
                        <div className="card-body">
                            <h1>📍</h1>

                            <h3>0</h3>

                            <p className="text-muted mb-0">
                                Addresses
                            </p>
                        </div>
                    </div>
                </div>

            </div>

            {/* =======================================
                Quick Actions
            ======================================= */}

            <div className="card shadow-sm border-0">

                <div className="card-header bg-white">
                    <h4 className="mb-0">
                        🚀 Quick Actions
                    </h4>
                </div>

                <div className="card-body">

                    <div className="row g-3">

                        <div className="col-md-6 col-lg-4">
                            <Link
                                to="/products"
                                className="btn btn-outline-primary w-100 py-3"
                            >
                                🛍 Continue Shopping
                            </Link>
                        </div>

                        <div className="col-md-6 col-lg-4">
                            <Link
                                to="/orders"
                                className="btn btn-outline-success w-100 py-3"
                            >
                                📦 My Orders
                            </Link>
                        </div>

                        <div className="col-md-6 col-lg-4">
                            <button
                                className="btn btn-outline-danger w-100 py-3"
                            >
                                ❤️ Wishlist
                            </button>
                        </div>

                        <div className="col-md-6 col-lg-4">
                            <button
                                className="btn btn-outline-warning w-100 py-3"
                            >
                                📍 Address Book
                            </button>
                        </div>

                        <div className="col-md-6 col-lg-4">
                            <Link
                                to="/profile"
                                className="btn btn-outline-info w-100 py-3"
                            >
                                👤 Profile
                            </Link>
                        </div>

                        <div className="col-md-6 col-lg-4">
                            <Link
                                to="/profile"
                                className="btn btn-outline-secondary w-100 py-3"
                            >
                                🔒 Change Password
                            </Link>
                        </div>

                    </div>

                </div>

            </div>

            {/* =======================================
                Recent Orders (Placeholder)
            ======================================= */}

            <div className="card shadow-sm border-0 mt-5">

                <div className="card-header bg-white">
                    <h4 className="mb-0">
                        📋 Recent Orders
                    </h4>
                </div>

                <div className="card-body text-center">

                    <p className="text-muted mb-0">
                        You haven't placed any orders yet.
                    </p>

                </div>

            </div>

        </div>
    );
};

export default CustomerDashboard;