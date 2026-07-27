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
            <h4>Admin Panel</h4>
            <hr />

            <ul className="nav flex-column">

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/dashboard">
                        Dashboard
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/products">
                        Products
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/categories">
                        Categories
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/inventory">
                        Inventory
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/suppliers">
                        Suppliers
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/orders">
                        Orders
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/customers">
                        Customers
                    </Link>
                </li>

                <li className="nav-item">
                    <Link className="nav-link text-white" to="/admin/reports">
                        Reports
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