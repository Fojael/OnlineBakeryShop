import { Link } from "react-router-dom";

const Sidebar = () => {
    return (
        <div
            className="bg-dark text-white p-3"
            style={{
                width: "250px",
                minHeight: "100vh",
            }}
        >
            <h4>Admin Dashboard</h4>
            <hr />

            <ul className="nav flex-column">
                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/dashboard">
                        Dashboard
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/categories">
                        Category Management
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/products">
                        Product Management
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/inventory">
                        Inventory / Stock
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/suppliers">
                        Supplier Management
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/customers">
                        Customer Management
                    </Link>
                </li>

                <li className="nav-item mt-2">
                    <div className="text-uppercase text-secondary small fw-bold">Order Management</div>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/orders">
                        Pending Orders
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/orders">
                        Accepted Orders
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/orders">
                        Processing Orders
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/orders">
                        Ready Orders
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/orders">
                        Completed Orders
                    </Link>
                </li>

                <li className="nav-item mt-2">
                    <div className="text-uppercase text-secondary small fw-bold">Delivery Management</div>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Assign Rider
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Active Deliveries
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Delivery History
                    </Link>
                </li>

                <li className="nav-item mt-2">
                    <div className="text-uppercase text-secondary small fw-bold">Rider Management</div>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Add Rider
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Rider List
                    </Link>
                </li>
                <li className="nav-item">
                    <Link className="nav-link text-white ms-3" to="/admin/delivery-riders">
                        Rider Status
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/payments">
                        Payment Management
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/reports">
                        Sales Reports
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/ai-prediction">
                        AI Prediction
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/notifications">
                        Notifications
                    </Link>
                </li>
            </ul>
        </div>
    );
};

export default Sidebar;