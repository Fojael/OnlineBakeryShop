import {
    NavLink,
    useNavigate,
} from "react-router-dom";

import {
    FaTachometerAlt,
    FaUser,
    FaBoxes,
    FaMoneyBillWave,
    FaBell,
    FaSignOutAlt,
} from "react-icons/fa";


const SupplierSidebar = ({
    onLogout,
}) => {

    const navigate = useNavigate();


    const handleLogout = () => {

        if (onLogout) {
            onLogout();
        } else {

            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            localStorage.removeItem("user");
            localStorage.removeItem("role");

            sessionStorage.removeItem("access");
            sessionStorage.removeItem("refresh");
            sessionStorage.removeItem("user");

            navigate(
                "/login",
                {
                    replace: true,
                }
            );
        }

    };


    return (

        <aside className="supplier-sidebar">

            {/* BRAND */}

            <div className="supplier-sidebar-brand">

                <h4 className="fw-bold mb-0">
                    Bakery Shop
                </h4>

                <small>
                    Supplier Panel
                </small>

            </div>


            {/* MENU */}

            <nav className="supplier-sidebar-menu">

                <NavLink
                    to="/supplier/dashboard"
                    className={({ isActive }) =>
                        `supplier-nav-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >

                    <FaTachometerAlt />

                    <span>
                        Dashboard
                    </span>

                </NavLink>


                <NavLink
                    to="/supplier/profile"
                    className={({ isActive }) =>
                        `supplier-nav-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >

                    <FaUser />

                    <span>
                        My Profile
                    </span>

                </NavLink>


                <NavLink
                    to="/supplier/replenishments"
                    className={({ isActive }) =>
                        `supplier-nav-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >

                    <FaBoxes />

                    <span>
                        Replenishment Requests
                    </span>

                </NavLink>


                <NavLink
                    to="/supplier/payments"
                    className={({ isActive }) =>
                        `supplier-nav-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >

                    <FaMoneyBillWave />

                    <span>
                        Payments
                    </span>

                </NavLink>


                <NavLink
                    to="/notifications"
                    className={({ isActive }) =>
                        `supplier-nav-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >

                    <FaBell />

                    <span>
                        Notifications
                    </span>

                </NavLink>

            </nav>


            {/* LOGOUT */}

            <div className="supplier-sidebar-footer">

                <button
                    type="button"
                    className="supplier-logout-btn"
                    onClick={handleLogout}
                >

                    <FaSignOutAlt />

                    <span>
                        Logout
                    </span>

                </button>

            </div>

        </aside>

    );
};


export default SupplierSidebar;

