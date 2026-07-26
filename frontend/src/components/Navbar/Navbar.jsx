import { Link } from "react-router-dom";

const Navbar = () => {
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

                        <Link className="nav-link" to="/login">
                            Login
                        </Link>

                        <Link className="nav-link" to="/register">
                            Register
                        </Link>

                    </div>
                </div>

            </div>
        </nav>
    );
};

export default Navbar;