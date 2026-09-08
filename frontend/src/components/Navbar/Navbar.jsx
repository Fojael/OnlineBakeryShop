import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    Link,
    useNavigate,
} from "react-router-dom";

import { useDispatch, useSelector } from "react-redux";

import {
    toast,
} from "react-toastify";

import {
    logout,
} from "../../services/authService";

import {
    getCart,
} from "../../services/cartService";

import {
    clearCart as clearCartState,
} from "../../redux/cartSlice";

import NotificationBell from "../Notifications/NotificationBell";


const Navbar = () => {

    const navigate = useNavigate();

    const dispatch = useDispatch();

    const cartItems = useSelector(
        (state) => state.cart.cartItems
    );

    const [auth, setAuth] = useState(() => ({
        token:
            localStorage.getItem("access") ||
            sessionStorage.getItem("access"),
        role:
            localStorage.getItem("role") ||
            sessionStorage.getItem("role") ||
            "",
        username:
            localStorage.getItem("username") ||
            "User",
    }));

    const syncAuthentication = useCallback(async () => {
        const nextAuth = {
            token:
                localStorage.getItem("access") ||
                sessionStorage.getItem("access"),
            role:
                localStorage.getItem("role") ||
                sessionStorage.getItem("role") ||
                "",
            username:
                localStorage.getItem("username") ||
                "User",
        };

        setAuth(nextAuth);

        if (
            nextAuth.token &&
            String(nextAuth.role).toUpperCase() === "CUSTOMER"
        ) {
            try {
                await getCart();
            } catch {
                dispatch(clearCartState());
            }
        } else {
            dispatch(clearCartState());
        }
    }, [dispatch]);

    useEffect(() => {
        const handleAuthenticationChanged = () => {
            void syncAuthentication();
        };

        window.addEventListener(
            "auth-changed",
            handleAuthenticationChanged
        );

        const timer = setTimeout(() => {
            void syncAuthentication();
        }, 0);

        return () => {
            clearTimeout(timer);
            window.removeEventListener(
                "auth-changed",
                handleAuthenticationChanged
            );
        };
    }, [syncAuthentication]);

    const cartQuantity = cartItems.reduce(
        (total, item) => total + Number(item.quantity || 0),
        0
    );


    // ==========================================================
    // AUTH DATA
    // ==========================================================

    const token = auth.token;

    const role = auth.role;


    const username = auth.username;


    // ==========================================================
    // LOGOUT
    // ==========================================================

    const handleLogout = async () => {

        try {

            const refresh =
                localStorage.getItem("refresh")
                ||
                sessionStorage.getItem("refresh");


            if (refresh) {

                await logout(refresh);

            }

        } catch (error) {

            console.error(
                "Logout error:",
                error
            );

        }


        // Clear authentication

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        localStorage.removeItem("role");
        localStorage.removeItem("username");
        localStorage.removeItem("email");


        sessionStorage.removeItem("access");
        sessionStorage.removeItem("refresh");
        sessionStorage.removeItem("user");
        sessionStorage.removeItem("role");
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("email");

        dispatch(clearCartState());


        // Tell NotificationProvider
        // that authentication changed.

        window.dispatchEvent(
            new Event("auth-changed")
        );


        toast.success(
            "Logged out successfully!"
        );


        navigate(
            "/login",
            {
                replace: true,
            }
        );

    };


    // ==========================================================
    // DASHBOARD PATH
    // ==========================================================

    const normalizedRole =
        String(role)
            .trim()
            .toUpperCase();


    const dashboardPath =
        normalizedRole === "ADMIN"
            ? "/admin/dashboard"
            : normalizedRole === "CUSTOMER"
                ? "/customer/dashboard"
                : normalizedRole === "SUPPLIER"
                    ? "/supplier/dashboard"
                    : normalizedRole === "DELIVERY"
                        ? "/delivery/dashboard"
                        : normalizedRole === "DELIVERY_RIDER"
                            ? "/delivery/dashboard"
                            : "/";


    // ==========================================================
    // UI
    // ==========================================================

    return (

        <nav
            className="
                navbar
                navbar-expand-lg
                navbar-dark
                bg-dark
                shadow-sm
            "
        >

            <div className="container">


                {/* BRAND */}

                <Link
                    className="
                        navbar-brand
                        fw-bold
                    "
                    to="/"
                >

                    🥖 Online Bakery Shop

                </Link>


                {/* MOBILE TOGGLE */}

                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarContent"
                    aria-controls="navbarContent"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >

                    <span
                        className="navbar-toggler-icon"
                    />

                </button>


                {/* NAVIGATION */}

                <div
                    className="
                        collapse
                        navbar-collapse
                    "
                    id="navbarContent"
                >

                    <ul
                        className="
                            navbar-nav
                            ms-auto
                            align-items-lg-center
                            gap-lg-2
                        "
                    >


                        {/* HOME */}

                        <li className="nav-item">

                            <Link
                                className="nav-link"
                                to="/"
                            >
                                Home
                            </Link>

                        </li>


                        {/* PRODUCTS */}

                        <li className="nav-item">

                            <Link
                                className="nav-link"
                                to="/products"
                            >
                                Products
                            </Link>

                        </li>

                        {normalizedRole === "CUSTOMER" && (
                            <>
                                <li className="nav-item"><Link className="nav-link" to="/orders">My Orders</Link></li>
                                <li className="nav-item"><Link className="nav-link" to="/refunds">Refund Requests</Link></li>
                                <li className="nav-item"><Link className="nav-link" to="/wishlist">Wishlist</Link></li>
                                <li className="nav-item">
                                    <Link
                                        className="nav-link position-relative d-inline-block"
                                        to="/cart"
                                    >
                                        Cart
                                        {cartQuantity > 0 && (
                                            <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                                                {cartQuantity > 99
                                                    ? "99+"
                                                    : cartQuantity}
                                            </span>
                                        )}
                                    </Link>
                                </li>
                            </>
                        )}


                        {/* ABOUT */}

                        <li className="nav-item">

                            <Link
                                className="nav-link"
                                to="/about"
                            >
                                About
                            </Link>

                        </li>


                        {/* CONTACT */}

                        <li className="nav-item">

                            <Link
                                className="nav-link"
                                to="/contact"
                            >
                                Contact
                            </Link>

                        </li>


                        {/* ==================================================
                            NOTIFICATION BELL
                        ================================================== */}

                        {token && (

                            <li
                                className="
                                    nav-item
                                    d-flex
                                    align-items-center
                                    ms-lg-2
                                "
                            >

                                <NotificationBell />

                            </li>

                        )}


                        {/* ==================================================
                            NOT LOGGED IN
                        ================================================== */}

                        {!token ? (

                            <>

                                <li className="nav-item">

                                    <Link
                                        className="nav-link"
                                        to="/login"
                                    >
                                        Login
                                    </Link>

                                </li>


                                <li className="nav-item">

                                    <Link
                                        className="
                                            btn
                                            btn-warning
                                            ms-lg-2
                                        "
                                        to="/register"
                                    >
                                        Register
                                    </Link>

                                </li>

                            </>

                        ) : (

                            /* ==================================================
                               LOGGED IN
                            ================================================== */

                            <li
                                className="
                                    nav-item
                                    dropdown
                                "
                            >

                                <button
                                    type="button"
                                    className="
                                        btn
                                        btn-outline-light
                                        dropdown-toggle
                                        ms-lg-2
                                    "
                                    data-bs-toggle="dropdown"
                                    aria-expanded="false"
                                >

                                    👋 Hello, {username}

                                </button>


                                <ul
                                    className="
                                        dropdown-menu
                                        dropdown-menu-end
                                    "
                                >

                                    <li>

                                        <Link
                                            className="dropdown-item"
                                            to={dashboardPath}
                                        >

                                            📊 Dashboard

                                        </Link>

                                    </li>


                                    <li>

                                        <Link
                                            className="dropdown-item"
                                            to="/profile"
                                        >

                                            👤 Profile

                                        </Link>

                                    </li>


                                    <li>

                                        <Link
                                            className="dropdown-item"
                                            to="/notifications"
                                        >

                                            🔔 Notifications

                                        </Link>

                                    </li>


                                    <li>

                                        <hr
                                            className="
                                                dropdown-divider
                                            "
                                        />

                                    </li>


                                    <li>

                                        <button
                                            type="button"
                                            className="
                                                dropdown-item
                                                text-danger
                                            "
                                            onClick={
                                                handleLogout
                                            }
                                        >

                                            🚪 Logout

                                        </button>

                                    </li>

                                </ul>

                            </li>

                        )}

                    </ul>

                </div>

            </div>

        </nav>

    );

};


export default Navbar;