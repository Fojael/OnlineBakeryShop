import {
    FaBell,
    FaUserCircle,
} from "react-icons/fa";

import {
    Link,
} from "react-router-dom";

import useNotification
    from "../../hooks/useNotification";


const SupplierNavbar = () => {

    const {
        unreadCount,
    } = useNotification();


    const storedUser =
        localStorage.getItem("user");


    let user = null;


    try {

        user = storedUser
            ? JSON.parse(storedUser)
            : null;

    } catch (error) {

        console.error(
            "Failed to parse supplier user:",
            error
        );

    }


    return (

        <header className="supplier-navbar">

            <div>

                <h5 className="mb-0 fw-bold">
                    Supplier Dashboard
                </h5>

                <small className="text-muted">
                    Manage your bakery supplies
                </small>

            </div>


            <div className="d-flex align-items-center gap-4">

                {/* NOTIFICATION */}

                <Link
                    to="/notifications"
                    className="supplier-notification-link"
                >

                    <FaBell />

                    {unreadCount > 0 && (

                        <span className="supplier-notification-badge">

                            {unreadCount > 99
                                ? "99+"
                                : unreadCount}

                        </span>

                    )}

                </Link>


                {/* USER */}

                <Link
                    to="/supplier/profile"
                    className="supplier-user-link"
                >

                    <FaUserCircle />

                    <span>

                        {user?.username ||
                            user?.email ||
                            "Supplier"}

                    </span>

                </Link>

            </div>

        </header>

    );
};


export default SupplierNavbar;