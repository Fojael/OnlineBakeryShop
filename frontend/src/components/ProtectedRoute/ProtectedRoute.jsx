import { Navigate, useLocation } from "react-router-dom";

const ProtectedRoute = ({
    children,
    allowedRoles = [],
}) => {

    const location = useLocation();

    // =========================================================
    // GET TOKEN
    // =========================================================

    const accessToken =
        localStorage.getItem("access") ||
        sessionStorage.getItem("access");

    const refreshToken =
        localStorage.getItem("refresh") ||
        sessionStorage.getItem("refresh");

    // =========================================================
    // NOT LOGGED IN
    // =========================================================

    if (!accessToken || !refreshToken) {

        return (
            <Navigate
                to="/login"
                replace
                state={{
                    from: location,
                }}
            />
        );
    }

    // =========================================================
    // GET USER
    // =========================================================

    const storedUser =
        localStorage.getItem("user") ||
        sessionStorage.getItem("user");

    let user = null;

    try {

        if (storedUser) {
            user = JSON.parse(storedUser);
        }

    } catch (error) {

        console.error(
            "Invalid user data:",
            error
        );

        localStorage.removeItem("user");
        sessionStorage.removeItem("user");

        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    // =========================================================
    // USER DATA MISSING
    // =========================================================

    if (!user) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    // =========================================================
    // NORMALIZE ROLE
    // =========================================================

    const role =
        String(user.role || "")
            .trim()
            .toUpperCase();

    // =========================================================
    // ROLE CHECK
    // =========================================================

    if (
        allowedRoles.length > 0 &&
        !allowedRoles.includes(role)
    ) {

        console.error(
            "Unauthorized role:",
            role
        );

        // Send user to their appropriate home
        if (role === "ADMIN") {
            return (
                <Navigate
                    to="/admin/dashboard"
                    replace
                />
            );
        }

        if (role === "CUSTOMER") {
            return (
                <Navigate
                    to="/"
                    replace
                />
            );
        }

        if (role === "SUPPLIER") {
            return (
                <Navigate
                    to="/supplier/dashboard"
                    replace
                />
            );
        }

        if (
            role === "DELIVERY_RIDER" ||
            role === "DELIVERY RIDER"
        ) {
            return (
                <Navigate
                    to="/delivery/dashboard"
                    replace
                />
            );
        }

        return (
            <Navigate
                to="/"
                replace
            />
        );
    }

    // =========================================================
    // AUTHORIZED
    // =========================================================

    return children;
};

export default ProtectedRoute;