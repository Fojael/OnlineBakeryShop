import { Navigate } from "react-router-dom";

const ProtectedAdminRoute = ({ children }) => {

    const token = localStorage.getItem("access");
    const role = localStorage.getItem("role");

    // User is not logged in
    if (!token) {
        return <Navigate to="/login" />;
    }

    // User is not an admin
    if (role !== "ADMIN") {
        return <Navigate to="/" />;
    }

    // Allow access
    return children;
};

export default ProtectedAdminRoute;