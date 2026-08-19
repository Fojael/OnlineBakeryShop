import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { logout } from "../../services/authService";

const Navbar = () => {
    const navigate = useNavigate();

    const token = localStorage.getItem("access");
    const role = localStorage.getItem("role");
    const username = localStorage.getItem("username") || "User";

    const handleLogout = async () => {
        try {
            const refresh = localStorage.getItem("refresh");

            if (refresh) {
                await logout(refresh);
            }
        } catch (error) {
            console.log(error);
        }

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("role");
        localStorage.removeItem("username");
        localStorage.removeItem("email");

        toast.success("Logged out successfully!");

        navigate("/login", { replace: true });
    };

    const dashboardPath =
        role === "ADMIN"
            ? "/admin/dashboard"
            : role === "CUSTOMER"
            ? "/customer/dashboard"
            : role === "SUPPLIER"
            ? "/supplier/dashboard"
            : role === "DELIVERY"
            ? "/delivery/dashboard"
            : "/";

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
            <div className="container">

                <Link className="navbar-brand fw-bold" to="/">
                    🥖 Online Bakery Shop
                </Link>

                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarContent"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div
                    className="collapse navbar-collapse"
                    id="navbarContent"
                >
                    <ul className="navbar-nav ms-auto align-items-lg-center">

                        <li className="nav-item">
                            <Link className="nav-link" to="/">
                                Home
                            </Link>
                        </li>

                        <li className="nav-item">
                            <Link className="nav-link" to="/products">
                                Products
                            </Link>
                        </li>

                        <li className="nav-item">
                            <Link className="nav-link" to="/about">
                                About
                            </Link>
                        </li>

                        <li className="nav-item">
                            <Link className="nav-link" to="/contact">
                                Contact
                            </Link>
                        </li>

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
                                        className="btn btn-warning ms-lg-2"
                                        to="/register"
                                    >
                                        Register
                                    </Link>
                                </li>
                            </>
                        ) : (
                            <li className="nav-item dropdown">
                                <button
                                    className="btn btn-outline-light dropdown-toggle ms-lg-3"
                                    data-bs-toggle="dropdown"
                                >
                                    👋 Hello, {username}
                                </button>

                                <ul className="dropdown-menu dropdown-menu-end">

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
                                        <hr className="dropdown-divider" />
                                    </li>

                                    <li>
                                        <button
                                            className="dropdown-item text-danger"
                                            onClick={handleLogout}
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