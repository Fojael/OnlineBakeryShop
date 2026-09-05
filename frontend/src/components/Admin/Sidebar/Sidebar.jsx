import { NavLink } from "react-router-dom";

const Sidebar = () => {
    const linkClass = ({ isActive }) =>
        `nav-link ${
            isActive
                ? "active bg-primary text-white rounded"
                : "text-white"
        }`;

    return (
        <div
            className="bg-dark text-white p-3"
            style={{
                width: "260px",
                minHeight: "100vh",
            }}
        >
            <h4 className="mb-3 fw-bold">
                Admin Dashboard
            </h4>

            <hr className="border-secondary" />

            <ul className="nav flex-column">

                {/* Dashboard */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/dashboard"
                        className={linkClass}
                    >
                        Dashboard
                    </NavLink>
                </li>

                {/* Products */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/categories"
                        className={linkClass}
                    >
                        Category Management
                    </NavLink>
                </li>

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/products"
                        className={linkClass}
                    >
                        Product Management
                    </NavLink>
                </li>

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/inventory"
                        className={linkClass}
                    >
                        Inventory
                    </NavLink>
                </li>

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/suppliers"
                        className={linkClass}
                    >
                        Supplier Management
                    </NavLink>
                </li>

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/customers"
                        className={linkClass}
                    >
                        Customer Management
                    </NavLink>
                </li>

                <hr className="border-secondary my-3" />

                {/* Orders */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/orders"
                        className={linkClass}
                    >
                        Order Management
                    </NavLink>
                </li>

                {/* Delivery */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/delivery-management"
                        className={linkClass}
                    >
                        Delivery Management
                    </NavLink>
                </li>

                {/* Riders */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/riders"
                        className={linkClass}
                    >
                        Rider Management
                    </NavLink>
                </li>

                <hr className="border-secondary my-3" />

                {/* Payments */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/payments"
                        className={linkClass}
                    >
                        Payment Management
                    </NavLink>
                </li>

                {/* Reports */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/reports"
                        className={linkClass}
                    >
                        Sales Reports
                    </NavLink>
                </li>

                {/* AI */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/ai-prediction"
                        className={linkClass}
                    >
                        AI Prediction
                    </NavLink>
                </li>

                {/* Notifications */}

                <li className="nav-item mb-1">
                    <NavLink
                        to="/admin/notifications"
                        className={linkClass}
                    >
                        Notifications
                    </NavLink>
                </li>

            </ul>
        </div>
    );
};

export default Sidebar;