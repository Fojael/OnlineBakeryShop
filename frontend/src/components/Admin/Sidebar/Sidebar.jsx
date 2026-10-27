import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const navigationSections = [
    [
        { label: "Dashboard", to: "/admin/dashboard" },
        { label: "Category Management", to: "/admin/categories" },
        { label: "Product Management", to: "/admin/products" },
        { label: "Inventory", to: "/admin/inventory" },
        { label: "Supplier Management", to: "/admin/suppliers" },
        { label: "Stock Replenishment", to: "/admin/replenishments" },
        { label: "Customer Management", to: "/admin/customers" },
    ],
    [
        { label: "Order Management", to: "/admin/orders" },
        { label: "Create Offline Sale", to: "/admin/offline-sales" },
        { label: "Offline Sales History", to: "/admin/offline-sales/history" },
        { label: "Delivery Management", to: "/admin/delivery" },
        { label: "Rider Management", to: "/admin/riders" },
    ],
    [
        { label: "Payment Management", to: "/admin/payments" },
        { label: "Refunds", to: "/admin/refunds" },
        { label: "Sales Reports", to: "/admin/reports" },
        { label: "AI Prediction", to: "/admin/ai-prediction" },
        { label: "Notifications", to: "/admin/notifications" },
        { label: "Profile", to: "/admin/profile" },
    ],
];

const Sidebar = ({ isOpen = false, onClose = () => {} }) => {
    const linkClass = ({ isActive }) =>
        `nav-link ${isActive ? "active bg-primary text-white rounded" : "text-white"}`;

    return (
        <>
            {isOpen && (
                <button
                    type="button"
                    className="admin-sidebar-backdrop d-md-none"
                    aria-label="Close admin navigation"
                    onClick={onClose}
                />
            )}

            <aside
                id="admin-sidebar"
                className={`admin-sidebar bg-dark text-white p-3${isOpen ? " is-open" : ""}`}
                aria-label="Admin navigation"
            >
                <div className="d-flex align-items-center justify-content-between">
                    <h4 className="mb-3 fw-bold">Admin Dashboard</h4>
                    <button
                        type="button"
                        className="btn btn-link text-white d-md-none mb-3"
                        aria-label="Close admin navigation"
                        onClick={onClose}
                    >
                        <i className="bi bi-x-lg" aria-hidden="true" />
                    </button>
                </div>

                <hr className="border-secondary" />

                <nav aria-label="Admin pages">
                    <ul className="nav flex-column">
                        {navigationSections.map((section, sectionIndex) => (
                            <li className="admin-sidebar__section" key={section[0].to}>
                                {sectionIndex > 0 && (
                                    <hr className="border-secondary my-3" />
                                )}
                                <ul className="nav flex-column">
                                    {section.map(({ label, to }) => (
                                        <li className="nav-item mb-1" key={to}>
                                            <NavLink
                                                to={to}
                                                className={linkClass}
                                                onClick={onClose}
                                            >
                                                {label}
                                            </NavLink>
                                        </li>
                                    ))}
                                </ul>
                            </li>
                        ))}
                    </ul>
                </nav>
            </aside>
        </>
    );
};

export default Sidebar;
