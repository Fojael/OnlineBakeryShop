import { Link, useNavigate } from "react-router-dom";
import { logout } from "../../services/authService";

const Navbar = () => {
    const navigate = useNavigate();

    const token = localStorage.getItem("access");

    const handleLogout = async () => {
    try {
        const refreshToken = localStorage.getItem("refresh");

        await logout(refreshToken);

        // Remove JWT tokens and role
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("role");

        alert("Logout Successful!");

        navigate("/login");

    } catch (error) {

        console.log(error);

        // Clear localStorage even if the API fails
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("role");

        navigate("/login");
    }
};
    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
            <div className="container">

                {/* Logo */}
                <Link className="navbar-brand" to="/">
                    Online Bakery Shop
                </Link>

                {/* Mobile Menu Button */}
                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarContent"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                {/* Show Logout when logged in */}
{token && (
    <button
        className="btn btn-danger ms-2"
        onClick={handleLogout}
    >
        Logout
    </button>
)}

                {/* Navbar Links */}
                <div
                    className="collapse navbar-collapse"
                    id="navbarContent"
                >
                    <div className="navbar-nav ms-auto">

                        <Link className="nav-link" to="/">
                            Home
                        </Link>

                        <Link className="nav-link" to="/products">
                            Products
                        </Link>

                        <Link className="nav-link" to="/cart">
                            Cart
                        </Link>

                        <Link className="nav-link" to="/orders">
                            Orders
                        </Link>

                        <Link className="nav-link" to="/profile">
                            Profile
                        </Link>

                        <Link className="nav-link" to="/about">
                            About
                        </Link>

                        <Link className="nav-link" to="/contact">
                            Contact
                        </Link>

                       {/* Show Login and Register when not logged in */}
{!token && (
    <>
        <Link className="nav-link" to="/login">
            Login
        </Link>

        <Link className="nav-link" to="/register">
            Register
        </Link>
    </>
)}

                    </div>
                </div>

            </div>
        </nav>
    );
};

export default Navbar;